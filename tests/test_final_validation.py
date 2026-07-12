import os

# 1. Test DataOps (Khansaa P3 & Salma P4)
def test_dataops_deliverables():
    # Vérifier si Khansaa a mis le pipeline dlt
    assert os.path.exists("pipelines/ingestion_dlt.py"), "Pipeline dlt manquant !"
    # Vérifier si Salma a mis le dossier dbt
    assert os.path.exists("fraud_dbt/dbt_project.yml"), "Projet dbt manquant !"

# 2. Test Machine Learning (Chaimae P6)
def test_ml_deliverables():
    # Vérifier si le notebook d'analyse ou de train est présent
    assert os.path.exists("01_eda_fraude_v2.ipynb"), "Notebook EDA manquant !"

# 3. Test Déploiement & DevOps (Oumaima P7)
def test_deployment_deliverables():
    # Vérifier si Docker et Requirements sont là
    assert os.path.exists("requirements.txt"), "Fichier requirements manquant !"
    assert os.path.exists("Dockerfile") or os.path.exists("docker-compose.yml"), "Config Docker manquante !"

# 4. Test Documentation (Siham P8 & Hasnae P1)
def test_documentation_exists():
    assert os.path.exists("README.md"), "README manquant !"
    assert os.path.exists("docs/"), "Dossier documentation manquant !"
