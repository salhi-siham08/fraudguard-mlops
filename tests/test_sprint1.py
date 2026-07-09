import os

# --- VÉRIFICATION P1 (HASNAE - Vision) ---
def test_documentation_exists():
    """Vérifier que les documents de vision ou README sont présents"""
    assert os.path.exists("README.md") or os.path.exists("docs/vision_projet.md"), "La documentation de vision est manquante !"

# --- VÉRIFICATION P3 (KHANSAA - Ingestion) ---
def test_ingestion_script_exists():
    """Vérifier que le script d'ingestion dlt de Khansaa est présent"""
    assert os.path.exists("pipelines/ingestion_dlt.py"), "Le script d'ingestion dlt est introuvable !"

# --- VÉRIFICATION P4 (SALMA - dbt) ---
def test_dbt_setup_exists():
    """Vérifier que la structure dbt de Salma est initialisée"""
    assert os.path.exists("fraud_dbt/dbt_project.yml"), "Le projet dbt n'est pas encore initialisé !"

# --- VÉRIFICATION P8 (SIHAM - EDA) ---
def test_eda_notebook_exists():
    """Vérifier que le notebook d'analyse de Siham est présent"""
    assert os.path.exists("01_eda_fraude_v2.ipynb"), "Le notebook EDA est introuvable !"
