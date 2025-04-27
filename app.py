from flask import Flask, render_template, request, jsonify
import os
import uuid
import json
import PyPDF2
import spacy
from collections import defaultdict
from operator import itemgetter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Charger le modèle français (ou anglais si problème)
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    nlp = spacy.load("en_core_web_sm")
    print("Modèle français non trouvé, utilisation du modèle anglais")

# Configuration
SKILLS_SECTION_KEYWORDS = {'compétence', 'competence', 'skill', 'connaissance'}
EXPERIENCE_SECTION_KEYWORDS = {'expérience', 'experience', 'projet', 'project'}

TECH_SKILLS = {
    'python', 'java', 'javascript', 'c++', 'sql', 'mongodb',
    'react', 'angular', 'docker', 'aws', 'machine learning'
}

class CVManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_manager()
        return cls._instance
    
    def init_manager(self):
        self.cv_database = []
        self.current_criteria = {}
        self.load_data()
    
    def load_data(self):
        if os.path.exists('cv_database.json'):
            with open('cv_database.json', 'r', encoding='utf-8') as f:
                self.cv_database = json.load(f)
    
    def save_data(self):
        with open('cv_database.json', 'w', encoding='utf-8') as f:
            json.dump(self.cv_database, f, ensure_ascii=False, indent=2)
    
    def add_cv(self, nom, prenom, pdf_file):
        """Ajoute un nouveau CV et met à jour le classement"""
        text = self.extract_text(pdf_file)
        skills = self.extract_skills(text)
        
        cv_data = {
            "id": str(uuid.uuid4()),
            "nom": nom,
            "prenom": prenom,
            "contenu": text,
            "competences": skills,
            "score": 0  # Calculé lors du matching
        }
        
        self.cv_database.append(cv_data)
        self.update_ranking()
        self.save_data()
        return cv_data
    
    def extract_text(self, pdf_file):
        """Extrait le texte d'un PDF"""
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4()}.pdf")
        pdf_file.save(temp_path)
        
        with open(temp_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join([page.extract_text() for page in reader.pages])
        
        os.remove(temp_path)
        return text
    
    def extract_skills(self, text):
        """Extrait les compétences avec scoring"""
        doc = nlp(text.lower())
        skills = defaultdict(int)
        current_section = None
        
        for sent in doc.sents:
            sent_text = sent.text
            if any(kw in sent_text for kw in SKILLS_SECTION_KEYWORDS):
                current_section = "SKILLS"
            elif any(kw in sent_text for kw in EXPERIENCE_SECTION_KEYWORDS):
                current_section = "EXPERIENCE"
            
            for token in sent:
                if token.text in TECH_SKILLS:
                    if current_section == "EXPERIENCE":
                        skills[token.text] = 2
                    elif current_section == "SKILLS" and skills[token.text] < 1:
                        skills[token.text] = 1
        
        return dict(skills)
    
    def set_criteria(self, criteria):
        """Définit les critères de matching"""
        self.current_criteria = criteria
        self.update_ranking()
    
    def update_ranking(self):
        """Met à jour le classement des CV"""
        for cv in self.cv_database:
            cv['score'] = self.calculate_score(cv['competences'])
        
        # Tri par score décroissant
        self.cv_database.sort(key=lambda x: x['score'], reverse=True)
    
    def calculate_score(self, skills):
        """Calcule le score selon les critères actuels"""
        return sum(
            skills.get(skill, 0) * weight 
            for skill, weight in self.current_criteria.items()
        )
    
    def get_ranked_cvs(self):
        """Retourne les CV classés"""
        return self.cv_database

# Instance globale
cv_manager = CVManager()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        files = request.files.getlist('cvs')
        
        results = []
        for file in files:
            if file and file.filename.endswith('.pdf'):
                results.append(cv_manager.add_cv(nom, prenom, file))
        
        return jsonify({
            "status": "success",
            "added": len(results),
            "ranking": cv_manager.get_ranked_cvs()
        })
    
    return render_template('index.html')

@app.route('/set_criteria', methods=['POST'])
def set_criteria():
    criteria = request.json.get('criteria', {})
    cv_manager.set_criteria(criteria)
    return jsonify({
        "status": "updated",
        "ranking": cv_manager.get_ranked_cvs()
    })

if __name__ == '__main__':
    app.run(debug=True)