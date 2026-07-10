"""
evaluate.py - Evaluation du modele en production (MLflow Model Registry)
Personne 6 - ML Engineer

Recharge le modele (Pipeline complet : preprocessor + classifieur) via son
alias "production" et recalcule les metriques sur le meme split de test
(random_state fixe -> reproductible) que train.py.

Le modele charge attend des donnees BRUTES (montant non normalise) car le
RobustScaler est integre dans le Pipeline logge par train.py.

Usage:
    python evaluate.py --data-path ../fraud_ingestion.duckdb --tracking-uri http://localhost:5000
"""

import argparse
import os

import mlflow
import mlflow.sklearn

from train import (
    ARTIFACTS_DIR,
    REGISTERED_MODEL_NAME,
    confusion_counts,
    evaluate_predictions,
    get_output_feature_names,
    load_and_clean_data,
    plot_confusion,
    plot_feature_importance,
    plot_roc_curve,
    split_data,
)


def main(data_path: str, tracking_uri: str, alias: str):
    mlflow.set_tracking_uri(tracking_uri)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    df = load_and_clean_data(data_path)
    X_train, X_test, y_train, y_test = split_data(df)

    model_uri = f"models:/{REGISTERED_MODEL_NAME}@{alias}"
    print(f"[load] Chargement du modele : {model_uri}")
    pipeline = mlflow.sklearn.load_model(model_uri)

    # Donnees brutes envoyees directement : le RobustScaler est deja dans le Pipeline
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    metrics = evaluate_predictions(y_test, y_pred, y_proba)
    cm_counts = confusion_counts(y_test, y_pred)

    print(f"\n=== Evaluation du modele '{alias}' ===")
    for k, v in metrics.items():
        print(f"{k:>10}: {v:.4f}")
    print(f"\n=== Matrice de confusion (chiffres) ===")
    for k, v in cm_counts.items():
        print(f"{k:>18}: {v}")

    roc_path = os.path.join(ARTIFACTS_DIR, "eval_roc.png")
    cm_path = os.path.join(ARTIFACTS_DIR, "eval_confusion.png")
    fi_path = os.path.join(ARTIFACTS_DIR, "eval_feature_importance.png")

    plot_roc_curve(y_test, y_proba, roc_path)
    plot_confusion(y_test, y_pred, cm_path)

    # IMPORTANT: memes noms de colonnes dans le meme ordre que train.py
    # (ColumnTransformer met "amount" scale en premier, puis le reste en
    # passthrough dans l'ordre d'origine). Utiliser X_train.columns.tolist()
    # brut ici decalait tous les labels d'un cran par rapport aux vraies
    # importances retournees par le modele.
    output_feature_names = get_output_feature_names(X_train.columns.tolist())
    has_fi = plot_feature_importance(pipeline, output_feature_names, fi_path)

    print(f"\n[done] Graphiques sauvegardes : {roc_path}, {cm_path}"
          + (f", {fi_path}" if has_fi else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation du modele de detection de fraude")
    parser.add_argument(
        "--data-path", default="../fraud_ingestion.duckdb",
        help="Chemin vers fraud_ingestion.duckdb (table main.fct_transactions_ml de P4)",
    )
    parser.add_argument("--tracking-uri", default="http://localhost:5000", help="URI du serveur MLflow")
    parser.add_argument("--alias", default="production", help="Alias du modele dans le Registry")
    args = parser.parse_args()
    main(args.data_path, args.tracking_uri, args.alias)