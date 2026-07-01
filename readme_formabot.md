# FormaBot — Assistant ADN Potentiel

> Chatbot de recommandation de formations professionnelles pour les dirigeants de TPE du BTP.

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://formabot-glenn-mboga.streamlit.app/)
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

> **Note sur le dépôt Git** : la mise à disposition d'un dépôt Git public est **facultative** selon le guide d'évaluation Nexa. Le code source complet est fourni dans le ZIP de livrables (`MBOGA_GLENN_LIVRABLES.zip`, dossier `code/`). Un dépôt GitHub pourra être créé après la soutenance officielle si ADN Potentiel souhaite poursuivre le projet en V2.

```bash
# 1. Se placer dans le dossier extrait du ZIP
cd MBOGA_GLENN_LIVRABLES/code

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

- 🌐 **Application en ligne** : https://formabot-glenn-mboga.streamlit.app/ (**en ligne**)
- 🏢 **ADN Potentiel** : https://adnpotentiel.com
- 📜 **Certification RNCP 37137** : https://www.francecompetences.fr/recherche/rncp/37137/

---

# Pour l'évaluateur (Plan de Déploiement et de Reprise / PDR)

Cette section est destinée au jury de soutenance et aux membres du jury chargés de la reproductibilité du projet.

## Accès rapide

| Type d'accès | URL | Identifiants |
|---|---|---|
| Application en ligne | https://formabot-glenn-mboga.streamlit.app/ | Aucun (application ouverte au public) |
| Dépôt GitHub | https://github.com/GlennMbg/formabot | Public (lecture seule) |
| Documentation technique | Ce README + dossier `evaluation/` | — |

**Aucune authentification requise** : conformément au principe RGPD de minimisation, l'application ne demande aucune information personnelle et ne stocke rien côté serveur. Les conversations restent locales (fichier `conversations_formabot.json` côté client).

## Contenu du ZIP de remise

| Fichier / dossier | Description | Source |
|---|---|---|
| `app_formabot.py` | Application Streamlit principale (1400+ lignes) | Code production |
| `formations_adn.csv` | Catalogue ADN Potentiel : 36 formations | Source de vérité |
| `formations_training_corpus.csv` | Corpus d'entraînement : 373 phrases / 19 intentions | Manuel |
| `formabot.db` | Base SQLite générée (60 Ko) | Construite par `build_sqlite_db.py` |
| `formabot.sql` | Dump SQL de la base (28 Ko) | Construit par `build_sqlite_db.py` |
| `build_sqlite_db.py` | Script de migration CSV → SQLite + benchmark | Outillage |
| `requirements.txt` | Dépendances Python pinnées | Production |
| `.streamlit/config.toml` | Thème et configuration serveur Streamlit | Production |
| `.gitignore` | Exclusion des données utilisateur (RGPD) | Production |
| `README.md` | Ce document (présentation + PDR) | Documentation |
| `DEPLOIEMENT.md` | Procédure de déploiement Streamlit Cloud pas-à-pas | Documentation |
| `evaluation/` | Scripts et rapports d'évaluation | Validation |
| `evaluation/test_set_formations.csv` | Jeu de test indépendant : 91 phrases | Validation |
| `evaluation/EVALUATION_REPORT.md` | Comparaison de 4 baselines sklearn | Validation |
| `evaluation/ROBUSTNESS_REPORT.md` | Mesure de la robustesse au bruit | Validation |
| `evaluation/ACCESSIBILITE.md` | Audit WCAG 2.1 AA / RGAA 4.1 | Validation |
| `evaluation/PROBLEMATIQUES_TECHNIQUES.csv` | Tableau de suivi des incidents techniques (15 entrées) | Suivi projet |
| `evaluation/results/` | Matrices de confusion, plots, tableaux comparatifs | Validation |

## Restauration depuis le dump SQL

Si la base `formabot.db` est corrompue ou absente, elle peut être reconstruite intégralement à partir du dump SQL :

```bash
# Méthode 1 : depuis le dump SQL (recommandée pour le jury)
rm -f formabot.db
sqlite3 formabot.db < formabot.sql

# Méthode 2 : depuis le CSV (régénère DB + indexes + dump + benchmark)
python build_sqlite_db.py
```

Les deux méthodes produisent une base strictement identique (vérifié par comparaison de hash SHA-256 lors du build).

## Procédure d'installation complète (machine vierge)

**Prérequis** : Python 3.10 ou supérieur, ~200 Mo d'espace disque.

```bash
# 1. Cloner le dépôt depuis GitHub
git clone https://github.com/GlennMbg/formabot.git
cd formabot

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows PowerShell

# 3. Installer les dépendances (peut prendre 2-3 min)
pip install -r requirements.txt

# 4. Vérifier que la base SQLite est présente (sinon la construire)
ls formabot.db || python build_sqlite_db.py

# 5. Lancer l'application
streamlit run app_formabot.py

# L'application s'ouvre sur http://localhost:8501
```

## Identifiants de test, connexion BDD et back office

Conformément au principe de **minimisation des données du RGPD (article 5.1.c)**, l'application FormaBot a été conçue **sans aucune authentification ni back office** :

| Élément exigé par le guide d'évaluation Nexa | Statut FormaBot |
|---|---|
| Identifiants de test (utilisateur) | **Aucun nécessaire** — application publique sans authentification |
| Identifiants de connexion à la base SQL | **Aucun nécessaire** — SQLite local en lecture seule, pas de serveur de BDD distant ni de credentials |
| Identifiants d'accès administrateur back office | **Aucun back office** — toute la configuration est dans le code source versionné (CSV catalogue + corpus + paramètres ML) |

Cette absence est **un choix de conception assumé** : pas de surface d'attaque, pas de fuite de données possible, pas de dérive opérationnelle. Le contenu du catalogue est mis à jour en versionnant le fichier `formations_adn.csv` puis en relançant `build_sqlite_db.py`.

**Aucun identifiant nécessaire** : l'application est ouverte. Les fonctionnalités à tester :

| Fonctionnalité | Comment l'éprouver |
|---|---|
| Recommandation par thème | Tapez : `propose-moi une formation en management` |
| Liste par thème | Tapez : `liste toutes les formations en commerce` |
| Top N | Tapez : `top 5 des formations en soft skills` |
| Info sur une formation | Tapez : `parle-moi de Personal branding` |
| Filtre par durée | Tapez : `une formation courte` |
| Filtre par format | Tapez : `formations en distanciel` |
| Filtre CPF | Tapez : `formations éligibles CPF` |
| Robustesse aux typos | Tapez : `je veux une liste des fotmatiins que vous proposez` |
| RGPD export | Sidebar → bouton 📥 Exporter mes conversations (JSON) |
| RGPD suppression | Sidebar → bouton 🗑️ Supprimer toutes mes conversations (confirmation à 2 étapes) |
| Model Card | Onglet 📋 Model Card (transparence AI Act art. 13) |

## Vérification multi-navigateurs

Application testée sur :

- ✅ Chrome 120+ (Windows, macOS, Linux)
- ✅ Firefox 120+ (Windows, Linux)
- ✅ Safari 17+ (macOS)
- ✅ Edge 120+ (Windows)
- ✅ Mobile : Chrome Android, Safari iOS (layout responsive jusqu'à ~400px)

## Performances mesurées

- **Latence p95** : ~24 ms par requête utilisateur (SVM + TF-IDF + overrides règle)
- **Temps de démarrage à froid** : ~3-5 secondes (chargement du modèle + cache Streamlit)
- **Empreinte mémoire** : ~150 Mo (Python + Streamlit + scikit-learn + données)
- **F1 macro sur test set indépendant** : 0.72 (91 phrases distinctes du training)
- **Robustesse au bruit** : 0% de dégradation sur accents/casse, -13% sur typos (mesure quantifiée dans `evaluation/ROBUSTNESS_REPORT.md`)

## Conformité réglementaire (récap)

| Texte | Article | Implémentation |
|---|---|---|
| AI Act 2024 | Art. 50 (disclosure systèmes interactifs) | Bandeau persistant en haut du chatbot |
| AI Act 2024 | Art. 13 (transparence et information utilisateurs) | Model Card complète dans l'onglet dédié |
| RGPD | Art. 17 (droit à l'oubli) | Bouton "Supprimer toutes mes conversations" avec confirmation 2 étapes |
| RGPD | Art. 20 (portabilité) | Bouton "Exporter mes conversations (JSON)" |
| RGPD | Art. 22 (décision automatisée) | N/A — aucune décision juridique automatisée |
| RGAA 4.1 | Niveau AA (WCAG 2.1 AA) | Conformité ~85%, audit complet dans `evaluation/ACCESSIBILITE.md` |

## Contact technique

En cas de problème de reproductibilité :

- **Auteur** : Glenn Mboga
- **Email** : mbogaglenn@gmail.com
- **Cabinet métier** : ADN Potentiel — contact@adnpotentiel.com — 06 61 15 80 04
- **Issues GitHub** : https://github.com/GlennMbg/formabot/issues (à ouvrir si bug reproductible)
