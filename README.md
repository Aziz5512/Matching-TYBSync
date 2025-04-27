# Matching intelligent entre utilisateurs dans le cadre du projet TYBSync
C'est un projet sous le cadre de Intern Explorer ISIMM
# Système de Matching Intelligent de CV

## 📝 Fonctionnalités
Créer un système de matching qui :
° Compare les compétences recherchées et proposées.
° Classe les profils selon la pertinence.
° Bonus: utiliser une approche sémantique (embeddings).

But : Permettre aux utilisateurs de trouver rapidement des profils qui correspondent à leurs besoins.

## 🛠 Installation

### Prérequis
- Python 3.9+
- pip


 . Cloner le dépôt
```bash
git clone https://github.com/votre-repo/matching-cv.git
cd matching-cv

### . Créer l'environnement virtuel
bash
python -m venv cv_env
### . Activer l'environnement
Windows :

bash
cv_env\Scripts\activate
macOS/Linux :

bash
source cv_env/bin/activate
### . Installer les dépendances
bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
📂 Structure des fichiers
matching-cv/
├── app.py                 # Backend principal
├── templates/
│   └── index.html         # Interface utilisateur
├── uploads/               # Dossier temporaire pour les PDF
├── processed/             # Résultats JSON
└── cv_database.json       # Base de données des CV
🚀 Lancement
bash
python app.py
Ouvrir http://localhost:5000 dans votre navigateur

