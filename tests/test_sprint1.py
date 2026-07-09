import os

def test_eda_notebook_exists():
    """Vérifier que le notebook EDA est présent"""
    assert os.path.exists("01_eda_fraude_v2.ipynb")

def test_requirements_exists():
    """Vérifier que le fichier requirements est présent"""
    assert os.path.exists("requirements.txt")
