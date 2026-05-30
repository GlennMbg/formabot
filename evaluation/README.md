# Évaluation — Sprints 1 & 2

Évaluation rigoureuse du pipeline NLP du chatbot. Matière du chapitre "Évaluation et méthodologie" du mémoire.

## Contenu

| Fichier | Rôle |
|---|---|
| `test_set.csv` | Jeu de test indépendant, 86 phrases annotées, distinct du training |
| `evaluate.py` | Script d'évaluation principal (4 baselines sklearn, test set, latence) |
| `cv.py` | Cross-validation 3-fold stratifiée sur les 4 baselines |
| `finalize.py` | Recalcule la latence et regénère le tableau comparatif à partir des per-class CSV |
| `run_distilbert.py` | Comparaison avec DistilBERT (à exécuter en local — voir ci-dessous) |
| `EVALUATION_REPORT.md` | Rapport synthétique pour le mémoire |
| `results/` | Tableaux, matrices de confusion, plots |

## Exécution

### Évaluation sklearn (test set + latence)

```bash
cd evaluation/
python3 evaluate.py --no-cv --no-bert
```

Produit `results/comparison_table.csv`, `results/per_class_*.csv`, `results/confusion_*.png`, `results/f1_vs_latency.png`.

### Cross-validation

```bash
python3 cv.py
```

Produit `results/cv_results.csv`.

### DistilBERT (optionnel, ~5 min CPU)

Pré-requis (à installer une fois) :

```bash
pip install transformers torch
```

Puis :

```bash
python3 run_distilbert.py
```

Le script télécharge `distilbert-base-multilingual-cased` (~500 Mo, mise en cache locale), extrait les embeddings, entraîne une Logistic Regression sur ces features, évalue sur le test set et **ajoute automatiquement la ligne dans le tableau comparatif** (`results/comparison_table.csv`). La matrice de confusion DistilBERT est produite dans `results/confusion_distilbert.png`.

## Résultats principaux

Sur le test set indépendant (86 phrases) :

| Modèle | Accuracy | F1 macro | F1 weighted | Latence p95 |
|---|---|---|---|---|
| **SVM (production)** | **0.674** | **0.637** | **0.656** | 23.6 ms |
| Random Forest | 0.477 | 0.495 | 0.526 | 243.9 ms |
| Logistic Regression | 0.384 | 0.354 | 0.387 | 4.3 ms |
| Naive Bayes | 0.244 | 0.175 | 0.221 | 3.5 ms |

Cross-validation 3-fold (F1 macro moyen sur les folds, sur le corpus d'entraînement) :

| Modèle | F1 macro | Écart-type |
|---|---|---|
| SVM (production) | 0.479 | 0.036 |
| Random Forest | 0.435 | 0.039 |
| Logistic Regression | 0.214 | 0.045 |
| Naive Bayes | 0.100 | 0.005 |

Le SVM domine sur tous les indicateurs et offre le meilleur compromis avec la latence. Voir `EVALUATION_REPORT.md` pour la discussion complète.
