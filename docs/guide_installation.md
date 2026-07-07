# 🚀 Guide d'installation — FraudGuard

Ce guide explique comment installer et lancer le projet **fraudguard-mlops** sur votre
machine, de zéro jusqu'à l'exécution de l'analyse exploratoire (EDA).

> 📌 Les sections marquées **🔜 à venir** seront complétées au fur et à mesure des sprints,
> quand les composants correspondants (pipeline, API, Docker) seront livrés.

---

## 1. Prérequis

Avant de commencer, installez sur votre machine :

| Outil | Version | Lien | Vérification |
|---|---|---|---|
| Python | 3.11 ou + | [python.org/downloads](https://www.python.org/downloads/) | `python --version` |
| Git | dernière | [git-scm.com](https://git-scm.com/downloads) | `git --version` |
| VS Code | dernière | [code.visualstudio.com](https://code.visualstudio.com/) | — |

⚠️ **Windows** : lors de l'installation de Python, cochez la case **« Add Python to PATH »**.

Dans VS Code, installez les extensions (Ctrl+Shift+X) :
- **Python** (Microsoft)
- **Jupyter** (Microsoft)

## 2. Cloner le projet

Ouvrez un terminal (PowerShell sur Windows) et exécutez :

```bash
git clone https://github.com/salhi-siham08/fraudguard-mlops.git
cd fraudguard-mlops
```

Puis ouvrez le dossier dans VS Code : **File → Open Folder** → sélectionnez `fraudguard-mlops`.

💡 Si un bandeau **« Restricted Mode »** apparaît en haut de VS Code : cliquez sur
**Manage** → **Trust** (faire confiance au dossier), sinon les notebooks ne s'exécuteront pas.

## 3. Créer l'environnement virtuel

Dans le terminal intégré de VS Code (**Terminal → New Terminal**), exécutez
**une commande à la fois** :

```bash
python -m venv .venv
```
*(cette commande prend ~1 minute sans rien afficher : c'est normal, attendez le retour du curseur)*

**Activer l'environnement :**

```powershell
# Windows (PowerShell) :
.venv\Scripts\activate
```
```bash
# Mac / Linux :
source .venv/bin/activate
```

✅ Vous devez voir `(.venv)` apparaître au début de la ligne du terminal.

❌ **Erreur Windows « l'exécution de scripts est désactivée »** ? Exécutez ceci puis
réessayez l'activation :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

*(2 à 5 minutes de téléchargement ; c'est terminé quand vous voyez `Successfully installed ...`)*

## 5. Télécharger le dataset

1. Aller sur [Credit Card Fraud Detection — Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
   *(compte Kaggle gratuit requis)*
2. Cliquer sur **Download** → dézipper l'archive
3. Placer le fichier **`creditcard.csv`** à la **racine** du projet :

```
fraudguard-mlops/
├── creditcard.csv        ← ICI
├── 01_eda_fraude_v2.ipynb
├── requirements.txt
└── ...
```

⚠️ **Ne jamais committer ce fichier sur GitHub** (144 Mo — il est déjà exclu par le
`.gitignore`, ne modifiez pas cette règle).

💡 **Pas encore le dataset ?** Pas bloquant : le notebook EDA détecte son absence et
génère automatiquement des données synthétiques réalistes pour travailler en attendant.

## 6. Lancer l'analyse exploratoire (EDA)

1. Ouvrir `01_eda_fraude_v2.ipynb` dans VS Code
2. En haut à droite : **Select Kernel** → **Python Environments** → choisir **`.venv`**
   *(si `.venv` n'apparaît pas : fermer et rouvrir VS Code)*
3. Cliquer sur **Run All** ▶▶
4. Vérifier la sortie de la cellule de chargement :
   - `📦 Dataset : RÉEL (Kaggle - creditcard.csv)` → analyse sur les vraies données ✅
   - `📦 Dataset : SYNTHÉTIQUE` → le CSV n'a pas été trouvé (vérifier l'étape 5)

⏳ **Patience** : avec le dataset réel (284 807 lignes), la grille des 28 densités
(section 8) prend 2 à 5 minutes. Ne pas interrompre.

Le notebook génère automatiquement :
- `figures/` : les 8 graphiques de l'analyse
- `reference_drift.csv` : échantillon de référence pour le monitoring de dérive (Sprint 3)

## 7. Workflow Git de l'équipe

La branche `main` est **protégée** : aucun push direct, tout passe par une Pull Request
approuvée par un autre membre.

```bash
# 1. Toujours partir d'une main à jour
git checkout main
git pull

# 2. Créer SA branche pour la tâche
git checkout -b feature/ma-tache

# 3. Travailler, puis committer
git add .
git commit -m "feat: description claire de ce qui a ete fait"

# 4. Pousser et ouvrir une Pull Request sur GitHub
git push origin feature/ma-tache
```

Sur GitHub : **Compare & pull request** → décrire la PR → un autre membre **Approve** →
**Merge**.

Préfixes de commit conseillés : `feat:` (nouvelle fonctionnalité), `fix:` (correction),
`docs:` (documentation), `test:` (tests), `chore:` (maintenance).

---

## 🔜 Sections à venir (complétées au fil des sprints)

### 8. Lancer le pipeline DataOps (dlt → DuckDB → dbt → Dagster)
*🔜 Sera documenté à la livraison du pipeline (P3, P4, P5 — Sprint 2).*

### 9. Entraîner le modèle et consulter MLflow
*🔜 Sera documenté à la livraison du composant ML (P6 — Sprint 2).*

### 10. Lancer l'API FastAPI et Docker
*🔜 Sera documenté à la livraison du déploiement (P7 — Sprint 2-3).*

### 11. Monitoring et détection de dérive
*🔜 Sera documenté au Sprint 3 (P8).*

---

## 🆘 Problèmes fréquents

| Problème | Solution |
|---|---|
| `python` n'est pas reconnu | Réinstaller Python en cochant « Add to PATH », puis rouvrir le terminal |
| Activation du venv refusée (Windows) | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `.venv` invisible dans Select Kernel | Fermer et rouvrir VS Code |
| Push refusé « Permission denied » | Mauvais compte GitHub mémorisé → Gestionnaire d'identification Windows → supprimer `git:https://github.com` → re-pousser et se connecter avec le bon compte |
| Push refusé « file exceeds 100 MB » | `creditcard.csv` a été ajouté par erreur → vérifier le `.gitignore` et retirer le fichier de l'index (`git rm --cached creditcard.csv`) |
| Le notebook tourne longtemps | Normal sur la section 8 avec le dataset réel (2-5 min) |

*Guide maintenu par Siham SALHI (P8 — Data Analyst). Dernière mise à jour : Sprint 2.*
