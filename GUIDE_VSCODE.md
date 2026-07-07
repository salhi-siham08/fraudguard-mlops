# 🚀 Guide : ouvrir et lancer l'EDA dans VS Code

## 1. Prérequis (une seule fois)
1. Installer [Python 3.10+](https://www.python.org/downloads/) (cocher "Add to PATH" à l'installation)
2. Installer [VS Code](https://code.visualstudio.com/)
3. Dans VS Code → onglet Extensions (Ctrl+Shift+X) → installer :
   - **Python** (Microsoft)
   - **Jupyter** (Microsoft)

## 2. Préparer le projet
1. Créer un dossier, par exemple `eda_fraude/`, et y placer :
   - `01_eda_fraude_v2.ipynb`
   - `requirements.txt`
   - (optionnel) `creditcard.csv` ← le vrai dataset Kaggle, si tu l'as
2. Ouvrir ce dossier dans VS Code : **File → Open Folder**

## 3. Installer les librairies
Ouvrir le terminal intégré (Ctrl+ù ou Terminal → New Terminal) puis :

    # (Recommandé) créer un environnement virtuel
    python -m venv .venv

    # L'activer :
    #   Windows :
    .venv\Scripts\activate
    #   Mac/Linux :
    source .venv/bin/activate

    # Installer les dépendances
    pip install -r requirements.txt

## 4. Lancer le notebook
1. Cliquer sur `01_eda_fraude_v2.ipynb` dans VS Code
2. En haut à droite : **Select Kernel** → choisir `.venv` (ou ton Python)
3. Cliquer sur **Run All** ▶▶

## 5. Comportement intelligent
- Si `creditcard.csv` est dans le dossier → le notebook utilise **le vrai dataset**
- Sinon → il génère des **données synthétiques réalistes** automatiquement
- Dans les deux cas il crée :
  - `figures/` : les 8 graphiques PNG pour le rapport
  - `reference_drift.csv` : échantillon de référence pour Evidently (Sprint 3)

## ⚠️ Si le vrai dataset est utilisé (284 807 lignes)
Tout fonctionne pareil, c'est juste un peu plus long (2-5 min pour la grille
des 28 densités). Ne panique pas si une cellule tourne un moment. ☕
