# Guide de déploiement Streamlit Community Cloud

> Procédure pas-à-pas pour mettre FormaBot en ligne sur une URL publique.
> Temps estimé : 30 minutes à 1 heure pour la première fois.

## Prérequis

- Un compte GitHub (gratuit) : https://github.com/signup
- Un compte Streamlit Community Cloud (gratuit) : https://share.streamlit.io
- Git installé sur ta machine (téléchargeable depuis https://git-scm.com)

## Étape 1 — Préparer le dépôt GitHub local

Depuis le dossier `D:\Users\glenn\Downloads\M2 Nexa\mémoire\` :

```bash
# Vérifier que les fichiers sensibles sont bien ignorés
git init
git status

# Tu devrais voir LISTÉS :
#   app_formabot.py
#   formations_adn.csv
#   formations_training_corpus.csv
#   formabot.db
#   formabot.sql
#   build_sqlite_db.py
#   requirements.txt
#   .streamlit/config.toml
#   README.md
#   evaluation/...
#
# Tu NE dois PAS voir :
#   conversations_formabot.json    ← exclus par .gitignore
#   .venv/                         ← exclus
#   __pycache__/                   ← exclus
#   app.py (AniReco)              ← exclus
```

Si tout est bon, premier commit :

```bash
git add .
git commit -m "FormaBot V1 - mémoire M2 RNCP 37137"
```

## Étape 2 — Créer le dépôt GitHub distant

1. Va sur https://github.com/new
2. Nom du dépôt suggéré : `formabot` ou `formabot-adn-potentiel`
3. Visibilité : **Public** (obligatoire pour Streamlit Cloud gratuit)
4. **Ne coche PAS** "Initialize with README" (on a déjà le nôtre)
5. Clique "Create repository"

GitHub te montre alors les commandes à exécuter. Copie celles de la section *"…or push an existing repository from the command line"* qui ressemblent à :

```bash
git remote add origin https://github.com/<TON_USERNAME>/formabot.git
git branch -M main
git push -u origin main
```

À la première poussée, GitHub te demandera ton nom d'utilisateur et un mot de passe (en réalité un *Personal Access Token*). Si nécessaire :
- https://github.com/settings/tokens
- "Generate new token (classic)" → scope `repo` → coller le token comme mot de passe.

## Étape 3 — Connecter Streamlit Cloud

1. Va sur https://share.streamlit.io
2. Clique "Sign in" → choisis "Continue with GitHub"
3. Autorise Streamlit à accéder à ton compte GitHub
4. Une fois connecté, clique **"Create app"** ou **"New app"**

## Étape 4 — Configurer l'app Streamlit

Dans le formulaire :

| Champ | Valeur |
|---|---|
| **Repository** | `<TON_USERNAME>/formabot` |
| **Branch** | `main` |
| **Main file path** | `app_formabot.py` |
| **App URL** | `formabot-mboga` (ou un nom de ton choix, doit être unique sur Streamlit) |
| **Python version** | `3.11` (recommandé) ou `3.10` |

Puis clique **"Deploy"**.

## Étape 5 — Attendre le build (5-10 minutes)

Streamlit Cloud va :

1. Cloner ton dépôt
2. Détecter `requirements.txt` et installer les dépendances avec `pip`
3. Lancer `streamlit run app_formabot.py`
4. Afficher les logs en direct dans la console

**Si tout se passe bien**, après quelques minutes, ton app sera disponible sur :
```
https://formabot-mboga.streamlit.app
```

## Étape 6 — En cas d'erreur

**Cas fréquents et solutions** :

| Erreur | Cause probable | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'X'` | Module manquant dans `requirements.txt` | Ajouter `X>=version` à `requirements.txt`, commit, push |
| `FileNotFoundError: formations_adn.csv` | Fichier non commité | `git add formations_adn.csv && git commit && git push` |
| `Memory limit exceeded` | Charge mémoire trop grande | Vérifier qu'aucun grand fichier n'a été commité par erreur (`git status`) |
| `Build timeout` | Installation des deps trop longue | Vérifier qu'on n'a pas `transformers` ou `torch` dans `requirements.txt` (ils ne sont pas nécessaires pour l'app) |
| Page blanche | Erreur Python silencieuse | Aller voir les logs : bouton "Manage app" en bas à droite |

## Étape 7 — Mettre à jour l'app en production

Quand tu modifies le code en local :

```bash
git add .
git commit -m "Description du changement"
git push
```

Streamlit Cloud détecte automatiquement le push et redéploie en 1-2 minutes.

## Étape 8 — Pour la remise du mémoire

Une fois l'URL active :

1. **Ajouter l'URL dans le `README.md`** (remplacer la ligne `https://formabot-mboga.streamlit.app/`)
2. **Ajouter l'URL dans le mémoire** (section 6.1 du squelette)
3. **Capture d'écran** de l'app en ligne pour la section "Développement de l'application"
4. **Tester depuis un autre navigateur / appareil** pour vérifier que tout fonctionne

## Limites du tier gratuit Streamlit Cloud

- **Mise en veille** : si l'app est inactive pendant 7 jours, elle est mise en veille (le premier visiteur attend ~30s au réveil)
- **Mémoire** : ~1 Go RAM disponibles → OK pour FormaBot (SVM + corpus léger)
- **Pas de stockage persistant** : `conversations_formabot.json` se réinitialise à chaque redéploiement (acceptable pour une démo)
- **Bandwidth illimité** mais usage raisonnable
- **Toutes les apps sont publiques** : pas d'authentification gratuite

Si besoin de fonctionnalités avancées (private apps, custom domain, more RAM) : Streamlit Teams payant ou auto-hébergement (Docker + serveur dédié, ~5€/mois OVH).

## Sécurité et conformité

Avant de pousser publiquement, vérifier que :

- [x] Aucun mot de passe, clé API, ou secret dans le code
- [x] Aucune donnée personnelle dans le repo (`conversations_formabot.json` ignoré)
- [x] Le `.gitignore` est en place et fonctionnel
- [x] Le bandeau de disclosure AI Act art. 50 est affiché
- [x] Les boutons RGPD art. 17 + 20 sont fonctionnels
- [x] Le Model Card est complet et accessible
- [x] Le catalogue de formations a l'autorisation d'ADN Potentiel pour diffusion publique
