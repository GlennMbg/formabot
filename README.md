# FormaBot — Assistant ADN Potentiel

> Chatbot de recommandation de formations professionnelles pour les dirigeants de TPE du BTP.

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://formabot-mboga.streamlit.app/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Qualiopi](https://img.shields.io/badge/Qualiopi-certifi%C3%A9-green)](https://travail-emploi.gouv.fr/formation-professionnelle/acteurs-cadre-et-qualite-de-la-formation-professionnelle/qualiopi)

Projet réalisé dans le cadre du **mémoire de fin d'études M2** de la formation *Chef de projet Data et Intelligence Artificielle* (RNCP 37137) à **Nexa Digital School**.

**Cabinet métier** : [ADN Potentiel](https://adnpotentiel.com) — cabinet de formation, conseil et coaching basé à Lille, spécialisé dans l'accompagnement des dirigeants de TPE du secteur BTP. Certifié Qualiopi, référencé OPCO Constructys.

## Fonctionnalités

- Chatbot conversationnel français + anglais (auto-détection langue)
- Recherche dans le catalogue ADN Potentiel par thème, format, durée, public, certification
- Recommandations aléatoires avec anti-répétition
- Top N des formations par thème
- Détails complets d'une formation (prix, durée, format, objectifs, prérequis)
- Persistance locale des conversations (JSON)
- **Conformité réglementaire** :
  - AI Act 2024 art. 50 — disclosure « assistant automatisé »
  - RGPD art. 17 — bouton de suppression complète des conversations
  - RGPD art. 20 — export JSON des conversations (portabilité)
- **Model Card intégrée** (alignée Mitchell et al. 2019)
- **Accessibilité** RGAA / WCAG 2.1 AA partielle

## Architecture

Pipeline NLP **hybride symbolique + ML** :

```
User → normalize_text (accents + casse + correction fuzzy 16 mots-clés métier)
     → TF-IDF (n-grams 1-2)
     → CalibratedClassifierCV(LinearSVC)
     → Override règles (top N, titre détecté, multi-critères)
     → Réponse contextualisée
```

**Backend données** : SQLite (avec fallback CSV automatique). 36 formations, 19 intentions, 373 phrases d'entraînement, F1 macro 0.72 sur test set indépendant.

## Démarrer en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-username>/formabot.git
cd formabot

# 2. Créer un environnement virtuel
python -m venv .venv
# Linux/Mac :
source .venv/bin/activate
# Windows :
.venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. (Optionnel) Construire la base SQLite à partir du CSV
python build_sqlite_db.py

# 5. Lancer l'application
streamlit run app_formabot.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Évaluation

Tous les scripts d'évaluation sont dans `evaluation/` :

- `evaluate.py` — comparaison de 4 modèles sklearn sur test set indépendant
- `evaluate_robustness.py` — mesure de la robustesse au bruit (typos, accents, casse, mots parasites)
- `cv.py` — cross-validation 3-fold
- `run_distilbert.py` — comparaison optionnelle avec DistilBERT (requiert `transformers` + `torch`)
- `EVALUATION_REPORT.md` — rapport complet
- `ROBUSTNESS_REPORT.md` — rapport de robustesse
- `ACCESSIBILITE.md` — audit WCAG 2.1 AA

```bash
cd evaluation
python evaluate.py
python evaluate_robustness.py
```

## Structure du projet

```
.
├── app_formabot.py              # Application Streamlit principale
├── formations_adn.csv           # Catalogue ADN Potentiel (36 formations)
├── formations_training_corpus.csv  # Corpus d'entraînement (373 phrases / 19 intentions)
├── formabot.db                  # Base SQLite générée
├── formabot.sql                 # Dump SQL (pour livrable mémoire)
├── build_sqlite_db.py           # Script de migration CSV → SQLite
├── requirements.txt             # Dépendances Python
├── .streamlit/config.toml       # Configuration thème + serveur
├── evaluation/                  # Scripts et rapports d'évaluation
│   ├── evaluate.py
│   ├── evaluate_robustness.py
│   ├── cv.py
│   ├── run_distilbert.py
│   ├── test_set_formations.csv
│   ├── EVALUATION_REPORT.md
│   ├── ROBUSTNESS_REPORT.md
│   └── ACCESSIBILITE.md
└── DEPLOIEMENT.md               # Guide de déploiement Streamlit Cloud
```

## Identifiants de test

Aucune authentification : l'application est ouverte au public. Aucune donnée personnelle n'est demandée ni stockée côté serveur. Les conversations sont stockées **localement côté client** (fichier JSON sur la machine de l'utilisateur).

## Licence

Code source sous licence MIT pour la partie applicative.
Catalogue de formations : propriété d'ADN Potentiel, utilisé avec autorisation pour ce mémoire.

## Auteur

**Glenn Mboga** — Étudiant M2 Chef de projet Data & IA, Nexa Digital School
Promotion 2025-2026 — Soutenance juin 2026

## Liens

- 🌐 **Application en ligne** : https://formabot-mboga.streamlit.app/ (à activer après déploiement)
- 🏢 **ADN Potentiel** : https://adnpotentiel.com
- 📜 **Certification RNCP 37137** : https://www.francecompetences.fr/recherche/rncp/37137/
