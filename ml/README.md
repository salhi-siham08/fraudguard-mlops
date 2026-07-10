# Module Machine Learning & MLOps — ML Engineer (P6)

## 🎯 Objectif

Entraînement automatisé, évaluation et gestion du cycle de vie des modèles de détection de fraude. Ce module assure le lien entre la donnée transformée (dbt) et les services de consommation (API). Il intègre le tracking complet via **MLflow**.

---

## 📋 Prérequis

- Python 3.10+
- Environnement virtuel activé
- Dépendances installées :
  ```powershell
  pip install -r requirements.txt
  ```
- Serveur MLflow lancé (port 5000)

---

## 📁 Structure du module

```
ml/
├── train.py              # Script principal : entraînement + logging MLflow
├── evaluate.py           # Validation du modèle en production
├── artifacts/            # Graphiques exportés (ROC, Confusion Matrix)
├── mlartifacts/          # Stockage local des modèles (Artefacts MLflow)
├── requirements.txt      # Dépendances spécifiques au module
└── README.md             # Présente documentation
```

---

## 🗃️ Données sources

- **Base** : `fraud_ingestion.duckdb` (située à la racine)
- **Table** : `main.fct_transactions_ml` (produite par P4/dbt)
- **Nettoyage** : Dédoublonnage final (1081 doublons supprimés) et suppression des colonnes techniques (`transaction_id`, `transaction_time`)
- **Features** : Utilisation des variables calculées par dbt (`is_night`, `transaction_hour`)

---

## 🚀 Comment lancer le module

### 1. Démarrer le serveur MLflow (obligatoire)

À lancer depuis le dossier `ml/` dans un terminal dédié :

```powershell
python -m mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts --port 5000
```

### 2. Entraîner et enregistrer le meilleur modèle

Se placer dans le dossier `ml` :

```powershell
cd ml
```

Lancer l'entraînement :

```powershell
python train.py --data-path ../fraud_ingestion.duckdb --tracking-uri http://localhost:5000
```

> Le script compare `LogisticRegression`, `RandomForest` et `XGBoost`. Il enregistre automatiquement le meilleur modèle dans le Registry avec l'alias `production`.

### 3. Évaluer le modèle de production

```powershell
python evaluate.py --data-path ../fraud_ingestion.duckdb --tracking-uri http://localhost:5000
```

---

## 🔌 Intégration avec les autres modules

### Pour P5 (Orchestration Dagster)

Le script est conçu pour être appelé directement comme un package Python :

```python
# Note : L'orchestrateur doit être lancé depuis la racine du projet
from ml.train import main

main(
    data_path="fraud_ingestion.duckdb",
    tracking_uri="http://localhost:5000"
)
```

### Pour P7 (Déploiement API FastAPI)

Le chargement du modèle est standardisé via l'alias de production :

```python
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("http://localhost:5000")

# Le pipeline chargé inclut déjà le RobustScaler (preprocessing)
model = mlflow.sklearn.load_model("models:/fraud-detection-model@production")

# Prédiction (X_new contient les colonnes dbt brutes)
y_proba = model.predict_proba(X_new)[:, 1]
y_pred = (y_proba >= 0.5).astype(int)
```

---

## ✅ Vérification (Résultats du Meilleur Modèle)

Le modèle sélectionné est le **RandomForest + SMOTE**.

| Métrique | Valeur |
|---|---|
| **Précision** | 0.9259 |
| **Recall** | 0.7894 |
| **F1-Score** | 0.8523 |
| **AUC-ROC** | 0.9657 |

**Matrice de confusion** : seulement 6 faux positifs détectés sur 56 863 transactions de test.

---

## 🛠️ Problèmes rencontrés & Solutions

| Problème | Solution |
|---|---|
| **Portabilité des chemins** | Passage aux chemins relatifs (`./mlartifacts`) pour éviter les erreurs liées aux noms d'utilisateurs Windows différents entre coéquipiers. |
| **Incompatibilité DuckDB** | Alignement de l'équipe sur DuckDB >= 1.5 pour garantir la lecture des tables `main.fct_transactions_ml`. |
| **Dédoublonnage** | dbt ne supprimant pas les doublons physiques, un filtrage `drop_duplicates(subset=cols_sans_id)` est appliqué dans le script d'entraînement pour garantir l'intégrité de l'évaluation. |

---

**Module prêt pour le déploiement. 🚀**
