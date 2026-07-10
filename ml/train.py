"""
train.py - Entrainement des modeles de detection de fraude
Personne 6 - ML Engineer (Livrables 5 + 6)

Integre les conclusions EDA de P8 :
- Doublons supprimes avant l'entrainement (verifie empiriquement que dbt/P4 ne
  deduplique pas reellement malgre le commentaire dans son SQL : 284 807 lignes
  dans la table alors que 1081 doublons avaient ete detectes par P8)
- Desequilibre extreme (0.173% de fraude) -> SMOTE ET class_weight compares
- Split stratifie obligatoire
- RobustScaler sur amount (asymetrique, outliers) -> integre dans un Pipeline
- Feature heure / nuit (fraude 3-4x plus frequente la nuit), deja calculees par P4
- Evaluation : precision, rappel, F1, AUC-ROC (jamais l'accuracy seule)
- Feature importance (RandomForest / XGBoost) pour valider les colonnes
  discriminantes identifiees par P8 (V17, V14, V12, V10...)

Source de donnees : table main.fct_transactions_ml produite par le pipeline dbt
de P4 (colonnes transaction_time/amount/class/v1..v28/transaction_hour/is_night/
amount_log), lue directement depuis le fichier DuckDB.

Usage:
    python train.py --data-path ../fraud_ingestion.duckdb --tracking-uri http://localhost:5000
"""

import argparse
import os
import matplotlib
matplotlib.use('Agg')  # force le mode sans affichage graphique (fichier uniquement)

import matplotlib.pyplot as plt

import duckdb
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

RANDOM_STATE = 42
MLFLOW_EXPERIMENT_NAME = "fraud-detection"
REGISTERED_MODEL_NAME = "fraud-detection-model"
ARTIFACTS_DIR = "artifacts"

TARGET_COL = "class"
AMOUNT_COL = "amount"
# transaction_id : identifiant unique -> jamais une feature (fuite de donnees)
# transaction_time / transaction_hour_abs : redondants avec transaction_hour/is_night
DROP_COLS = ["class", "transaction_id", "transaction_time", "transaction_hour_abs"]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_and_clean_data(path: str) -> pd.DataFrame:
    """
    path = chemin vers fraud_ingestion.duckdb (table main.fct_transactions_ml,
    nettoyee/transformee par P4, mais PAS dedoublonnee -> on le fait ici).

    NB: transaction_id est un row_number() genere par dbt, donc unique pour
    CHAQUE ligne meme quand toutes les autres colonnes sont identiques.
    On l'exclut du subset, sinon duplicated()/drop_duplicates() ne trouve
    jamais rien (confirme empiriquement : 0 doublon detecte avec l'ID,
    1081 sans l'ID -> coherent avec l'EDA de P8).
    """
    con = duckdb.connect(path)
    df = con.sql("SELECT * FROM main.fct_transactions_ml").df()
    con.close()
    print(f"[load] {len(df)} lignes chargees depuis main.fct_transactions_ml (dbt, P4)")

    n_before = len(df)
    cols_sans_id = [c for c in df.columns if c != "transaction_id"]
    df = df.drop_duplicates(subset=cols_sans_id)
    n_after = len(df)
    print(f"[clean] Doublons supprimes : {n_before - n_after} ({n_before} -> {n_after} lignes)")
    return df

def split_data(df: pd.DataFrame):
    """Split uniquement (pas de scaling ici -> le scaler vit dans le Pipeline)."""
    X = df.drop(columns=DROP_COLS)
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    return X_train, X_test, y_train, y_test


def build_preprocessor() -> ColumnTransformer:
    """RobustScaler sur la colonne montant uniquement (P8: asymetrique, outliers).
    Les autres colonnes (v1-v28, transaction_hour, is_night, amount_log...)
    passent telles quelles (remainder='passthrough')."""
    return ColumnTransformer(
        transformers=[("amount_scaler", RobustScaler(), [AMOUNT_COL])],
        remainder="passthrough",
    )


# ---------------------------------------------------------------------------
# Modeles
# ---------------------------------------------------------------------------

def build_classifier(model_name: str, strategy: str, y_train: pd.Series):
    """Construit uniquement le classifieur (sans preprocessing).
    class_weight n'existe pas pour XGBoost -> on utilise scale_pos_weight."""
    if model_name == "LogisticRegression":
        kwargs = {"max_iter": 2000, "random_state": RANDOM_STATE}
        if strategy == "class_weight":
            kwargs["class_weight"] = "balanced"
        return LogisticRegression(**kwargs)

    if model_name == "RandomForest":
        kwargs = {"n_estimators": 300, "random_state": RANDOM_STATE, "n_jobs": -1}
        if strategy == "class_weight":
            kwargs["class_weight"] = "balanced"
        return RandomForestClassifier(**kwargs)

    if model_name == "XGBoost":
        kwargs = {"random_state": RANDOM_STATE, "eval_metric": "logloss", "n_jobs": -1}
        if strategy == "class_weight":
            ratio = (y_train == 0).sum() / (y_train == 1).sum()
            kwargs["scale_pos_weight"] = ratio
        return XGBClassifier(**kwargs)

    raise ValueError(f"Modele inconnu : {model_name}")


def apply_smote(X_train, y_train):
    sm = SMOTE(random_state=RANDOM_STATE)
    return sm.fit_resample(X_train, y_train)


# ---------------------------------------------------------------------------
# Evaluation / plots
# ---------------------------------------------------------------------------

def evaluate_predictions(y_true, y_pred, y_proba) -> dict:
    return {
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "auc_roc": roc_auc_score(y_true, y_proba),
    }


def confusion_counts(y_true, y_pred) -> dict:
    """TN/FP/FN/TP en metriques MLflow numeriques (en plus de l'image)."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }


def plot_roc_curve(y_true, y_proba, out_path: str):
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    auc = roc_auc_score(y_true, y_proba)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"AUC = {auc:.4f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.xlabel("Taux de faux positifs")
    plt.ylabel("Taux de vrais positifs")
    plt.title("Courbe ROC")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_confusion(y_true, y_pred, out_path: str):
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Normale", "Fraude"])
    disp.plot(cmap="Blues", values_format="d")
    plt.title("Matrice de confusion")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_feature_importance(pipeline: Pipeline, feature_names: list, out_path: str, top_n: int = 15):
    """Feature importance pour RandomForest/XGBoost uniquement (pas LogisticRegression).
    Sert a verifier que v17, v14, v12, v10 (P8) ressortent bien en tete."""
    clf = pipeline.named_steps["model"]
    if not hasattr(clf, "feature_importances_"):
        return False

    importances = clf.feature_importances_
    order = np.argsort(importances)[::-1][:top_n]

    plt.figure(figsize=(8, 6))
    plt.barh(range(len(order)), importances[order][::-1])
    plt.yticks(range(len(order)), [feature_names[i] for i in order][::-1])
    plt.xlabel("Importance")
    plt.title("Top features les plus importantes")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return True


def get_output_feature_names(input_columns: list) -> list:
    """ColumnTransformer met la colonne montant (scaled) en premier, puis le reste
    (passthrough) dans leur ordre d'origine. On reconstruit la liste dans cet ordre exact."""
    remainder_cols = [c for c in input_columns if c != AMOUNT_COL]
    return [AMOUNT_COL] + remainder_cols


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(data_path: str, tracking_uri: str):
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    df = load_and_clean_data(data_path)
    X_train, X_test, y_train, y_test = split_data(df)

    print(f"[split] Taux de fraude train : {y_train.mean() * 100:.3f}%")
    print(f"[split] Taux de fraude test  : {y_test.mean() * 100:.3f}%")

    output_feature_names = get_output_feature_names(X_train.columns.tolist())

    model_names = ["LogisticRegression", "RandomForest", "XGBoost"]
    strategies = ["smote", "class_weight"]
    results = []

    for model_name in model_names:
        for strategy in strategies:
            run_name = f"{model_name}_{strategy}"

            # --- Preprocessing : fit UNIQUEMENT sur le train, jamais sur SMOTE-resample ---
            preprocessor = build_preprocessor()
            X_train_transformed = preprocessor.fit_transform(X_train)
            X_test_transformed = preprocessor.transform(X_test)

            if strategy == "smote":
                X_fit, y_fit = apply_smote(X_train_transformed, y_train)
            else:
                X_fit, y_fit = X_train_transformed, y_train

            classifier = build_classifier(model_name, strategy, y_train)
            classifier.fit(X_fit, y_fit)

            # --- Pipeline final = preprocessor deja fit + modele deja fit ---
            # On reconstruit un Pipeline "sklearn-complet" pour le logging MLflow,
            # afin que P7 puisse appeler predict() sur des donnees brutes (montant non normalise).
            full_pipeline = Pipeline([("preprocessor", preprocessor), ("model", classifier)])

            y_pred = full_pipeline.predict(X_test)
            y_proba = full_pipeline.predict_proba(X_test)[:, 1]
            metrics = evaluate_predictions(y_test, y_pred, y_proba)
            cm_counts = confusion_counts(y_test, y_pred)

            with mlflow.start_run(run_name=run_name):
                mlflow.log_param("model", model_name)
                mlflow.log_param("balancing", strategy)
                mlflow.log_params(classifier.get_params())
                mlflow.log_metrics(metrics)
                mlflow.log_metrics(cm_counts)

                roc_path = os.path.join(ARTIFACTS_DIR, f"roc_{run_name}.png")
                cm_path = os.path.join(ARTIFACTS_DIR, f"cm_{run_name}.png")
                plot_roc_curve(y_test, y_proba, roc_path)
                plot_confusion(y_test, y_pred, cm_path)
                mlflow.log_artifact(roc_path)
                mlflow.log_artifact(cm_path)

                fi_path = os.path.join(ARTIFACTS_DIR, f"feature_importance_{run_name}.png")
                if plot_feature_importance(full_pipeline, output_feature_names, fi_path):
                    mlflow.log_artifact(fi_path)

                # --- Signature + input_example : P7 sait exactement quoi envoyer ---
                signature = infer_signature(X_train, full_pipeline.predict(X_train.head(5)))
                logged_model_info = mlflow.sklearn.log_model(
                    full_pipeline,
                    "model",
                    signature=signature,
                    input_example=X_train.head(5),
                    skops_trusted_types=["xgboost.core.Booster", "xgboost.sklearn.XGBClassifier"],
                )

                run_id = mlflow.active_run().info.run_id
                print(f"[run] {run_name} -> F1={metrics['f1']:.4f} AUC={metrics['auc_roc']:.4f} "
                      f"(recall={metrics['recall']:.4f})")

                results.append({
                    "run_name": run_name,
                    "run_id": run_id,
                    "model_uri": logged_model_info.model_uri,
                    **metrics,
                })

    results_df = pd.DataFrame(results).sort_values("f1", ascending=False)
    print("\n=== Resume des runs (tries par F1) ===")
    print(results_df.to_string(index=False))

    best = results_df.iloc[0]
    print(f"\n[best] {best['run_name']} (F1={best['f1']:.4f}, AUC={best['auc_roc']:.4f})")

    # On utilise le model_uri REEL retourne par log_model (compatible MLflow 3.x
    # "Logged Models" : models/m-xxxx), pas un chemin runs:/.../model reconstruit
    # a la main qui ne pointe plus vers rien dans les versions recentes de MLflow.
    best_model_uri = best["model_uri"]
    mv = mlflow.register_model(best_model_uri, REGISTERED_MODEL_NAME)

    client = mlflow.tracking.MlflowClient()
    client.set_registered_model_alias(REGISTERED_MODEL_NAME, "production", mv.version)
    print(f"[registry] Modele version {mv.version} enregistre avec l'alias 'production'.")

    results_df.to_csv(os.path.join(ARTIFACTS_DIR, "results_summary.csv"), index=False)
    print(f"[done] Resultats sauvegardes dans {ARTIFACTS_DIR}/results_summary.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrainement des modeles de detection de fraude")
    parser.add_argument(
        "--data-path", default="../fraud_ingestion.duckdb",
        help="Chemin vers fraud_ingestion.duckdb (table main.fct_transactions_ml de P4)",
    )
    parser.add_argument("--tracking-uri", default="http://localhost:5000", help="URI du serveur MLflow")
    args = parser.parse_args()
    main(args.data_path, args.tracking_uri)