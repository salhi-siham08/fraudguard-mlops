# Module Ingestion — Data Engineer (P3)

## Objectif
Ingestion automatisée du dataset *Credit Card Fraud Detection* (Kaggle) dans DuckDB,
avec simulation d'arrivée progressive de données (chargement incrémental).

## Prérequis
- Python 3.10+
- Environnement virtuel activé
- Dépendances installées : `pip install -r requirements.txt` (dlt, duckdb, pandas)

## Structure
pipelines/
├── pipeline_ingestion.py     # chargement complet initial (284 807 lignes)
├── split_days.py             # découpe le CSV en 10 fichiers "journée"
├── pipeline_incremental.py   # charge les fichiers journée en mode append
└── README.md
## Données sources
- Fichier `data/raw/creditcard.csv` (non versionné sur Git, voir `.gitignore`)
- Téléchargé depuis Kaggle : *Credit Card Fraud Detection*
- 284 807 lignes, 31 colonnes (Time, V1-V28, Amount, Class)

## Comment lancer le pipeline

### 1. Chargement complet (première fois)
```powershell
python pipelines\pipeline_ingestion.py
```
Charge tout `creditcard.csv` dans la table `raw.transactions` (write_disposition="replace").

### 2. Simulation de nouvelles données
```powershell
python pipelines\split_days.py
```
Découpe le dataset en 10 fichiers `data/incoming/day_01.csv` à `day_10.csv`,
avec une colonne `transaction_id` unique par ligne.

### 3. Chargement incrémental
```powershell
python pipelines\pipeline_incremental.py
```
Charge les fichiers `day_XX.csv` un par un dans `raw.transactions` en mode `append`,
avec `transaction_id` comme clé primaire pour éviter les doublons en cas de relance.

## Vérification
```python
import duckdb
con = duckdb.connect("fraud_ingestion.duckdb")
con.sql("SELECT COUNT(*) FROM raw.transactions").df()          # doit renvoyer 284807
con.sql("SELECT COUNT(DISTINCT transaction_id) FROM raw.transactions").df()  # doit être = au total
```

## Table produite
- **Base** : `fraud_ingestion.duckdb`
- **Schéma** : `raw`
- **Table** : `raw.transactions`
- **Clé primaire** : `transaction_id`

Cette table est prête à être consommée par :
- **P4 (dbt)** pour les transformations et les tests de qualité
- **P5 (Dagster)** pour l'orchestration (via la fonction `run_incremental_load()`)

## Problèmes rencontrés
- Erreur `Adding columns with constraints not yet supported` lors du premier essai
  du chargement incrémental : la table existait déjà sans `transaction_id`.
  Solution : drop du schéma `raw` puis relance propre du pipeline incrémental
  (qui recrée la table avec la bonne structure dès le premier fichier).