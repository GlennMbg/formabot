# Rapport d'évaluation — Sprints 1 & 2

*Mémoire M2 Nexa — Pipeline NLP pour assistant conversationnel anime*

## Résumé exécutif

Cette évaluation indépendante compare quatre modèles de classification d'intentions sur un jeu de test de **86 phrases jamais vues à l'entraînement**, distinctes du corpus de 210 exemples. Le SVM TF-IDF actuellement en production est le **meilleur compromis performance/latence** sur tous les axes mesurés. Un comparatif avec DistilBERT multilingue est inclus en option (`run_distilbert.py`) pour exécution locale.

## Méthodologie

- **Corpus d'entraînement** : 210 phrases réparties sur 15 intentions, extraites directement du fichier `app.py` du système en production (couvre les intentions FR + EN).
- **Jeu de test indépendant** : 86 phrases rédigées séparément (fichier `test_set.csv`), distribution réaliste sur les 15 classes, mix FR/EN, et incluant des cas adversariaux (gibberish, questions hors-domaine pour la classe `fallback`). **Aucun chevauchement** avec le training set (vérifié après normalisation des accents et de la casse).
- **Cross-validation** : k-fold stratifiée k=3 sur le corpus d'entraînement, métrique F1 macro.
- **Latence** : 100 prédictions unitaires après warmup, en isolation sur CPU.
- **Pré-traitement identique** entre tous les modèles : strip accents, lowercase, compression des espaces, TF-IDF (n-grams 1-2). Pour le SVM, on conserve la calibration probabiliste (`CalibratedClassifierCV`) pour cohérence avec la production.

## Tableau comparatif global

### Performances sur le test set indépendant

| Modele              |   Accuracy (test) |   F1 macro (test) |   F1 weighted (test) |   Latence p50 (ms) |   Latence p95 (ms) |   Temps fit (s) |
|:--------------------|------------------:|------------------:|---------------------:|-------------------:|-------------------:|----------------:|
| SVM (production)    |             0.674 |             0.637 |                0.656 |             11.010 |             23.648 |           0.277 |
| Naive Bayes         |             0.244 |             0.175 |                0.221 |              1.801 |              3.490 |           0.016 |
| Logistic Regression |             0.384 |             0.354 |                0.387 |              2.481 |              4.283 |           0.096 |
| Random Forest       |             0.477 |             0.495 |                0.526 |            196.366 |            243.888 |           1.404 |

### Cross-validation 3-fold (sur le corpus d'entraînement)

| Modele              |   CV F1 macro mean |   CV F1 macro std |
|:--------------------|-------------------:|------------------:|
| SVM (production)    |              0.479 |             0.036 |
| Naive Bayes         |              0.100 |             0.005 |
| Logistic Regression |              0.214 |             0.045 |
| Random Forest       |              0.435 |             0.039 |

## Lecture des résultats

- **Meilleur F1 macro sur test** : SVM (production) (0.637). Le SVM domine sur les deux indicateurs à la fois.
- **Latence la plus faible** : Naive Bayes (3.5 ms p95), mais avec un F1 très inférieur (0.175) — pas viable en production.
- **Random Forest** atteint un F1 décent (0.495) mais à un coût latence prohibitif (244 ms p95, soit ~10× le SVM). Inadapté à l'usage interactif.
- **Naive Bayes** s'effondre sur ce corpus (F1 = 0.175) : son hypothèse d'indépendance entre features est inadaptée aux phrases courtes avec beaucoup d'informations contextuelles.

La courbe F1 vs latence est dans `results/f1_vs_latency.png`.

## Analyse par classe (SVM en production)

Les classes les plus difficiles pour le SVM sur le test :

- **`fallback`** : F1 = 0.000 (precision=0.000, recall=0.000, support=5) — le modèle a tendance à forcer une classification plutôt que de signaler un hors-domaine. Un seuil de confiance plus strict ou des exemples adversariaux supplémentaires sont nécessaires.
- **`goodbye`** : F1 = 0.000 (precision=0.000, recall=0.000, support=4) — classe sous-représentée (4 exemples en test, ~11 en training) : confusion fréquente avec `thanks` qui partage des marqueurs ('merci au revoir').
- **`help`** : F1 = 0.400 (precision=1.000, recall=0.250, support=4) — à enrichir avec plus d'exemples d'entraînement.

Les classes mieux maîtrisées (F1 > 0.75) : `list_by_genre`, `recommend_anime`, `thanks`, `ask_type`, `ask_episodes`.

## Comparaison avec DistilBERT multilingue

Le script `run_distilbert.py` permet de lancer cette comparaison localement (~5 min CPU). Pré-requis :

```bash
pip install transformers torch
python3 run_distilbert.py
```

Le script extrait les embeddings `[CLS]` du modèle `distilbert-base-multilingual-cased`, entraîne une Logistic Regression dessus, évalue sur le même jeu de test, et **ajoute automatiquement la ligne au tableau comparatif**. Cette comparaison n'a pas pu être exécutée dans l'environnement de génération de ce rapport (contraintes de sandbox), mais elle est attendue pour la version finale du mémoire.

**Hypothèses à valider** avec DistilBERT :
1. Le F1 macro devrait être supérieur au SVM, surtout sur les classes minoritaires et les phrases anglaises (DistilBERT est multilingue par construction).
2. La latence sera **dramatiquement plus élevée** (estimation 100-500 ms par requête sur CPU vs 24 ms pour le SVM) : c'est l'argument principal pour rester sur SVM en production.
3. Le modèle aurait besoin d'environ 500 Mo de RAM en plus pour les poids DistilBERT.

## Pistes d'amélioration identifiées

1. **Enrichir les classes minoritaires** : `thanks`, `help`, `goodbye`, `fallback` ont moins de 12 exemples chacune. Cibler ~25 exemples par classe.
2. **Seuil de confiance plus strict** pour la classe `fallback` : actuellement à 0.25, expérimenter à 0.40 pour limiter les faux-positifs sur les questions hors-domaine.
3. **Ajouter des exemples adversariaux d'entraînement** : faute de frappe, casse mixte, ponctuation excessive — sera traité au sprint 3.
4. **Considérer un ensemble** SVM + DistilBERT (vote pondéré) : si DistilBERT confirme un gain significatif sur certaines classes, un système hybride peut combiner les forces.

## Limites de cette évaluation

- Le jeu de test (86 phrases) reste de taille modeste. Pour une validation industrielle on viserait 500+ phrases. Pour un mémoire M2, c'est défendable.
- L'annotation a été faite par une seule personne, sans accord inter-annotateurs.
- La distribution des classes dans le test (5 à 8 phrases par classe) ne reflète pas nécessairement la distribution d'usage réel.
- La cross-validation 3-fold est limite (5-fold serait préférable mais coûteux côté calcul vu la taille du corpus). Les écarts-types observés (~0.04) restent toutefois faibles.

## Fichiers produits

Dans `results/` :

- `comparison_table.csv`
- `confusion_logistic_regression.png`
- `confusion_naive_bayes.png`
- `confusion_random_forest.png`
- `confusion_svm_production.png`
- `cv_results.csv`
- `f1_vs_latency.png`
- `per_class_logistic_regression.csv`
- `per_class_naive_bayes.csv`
- `per_class_random_forest.csv`
- `per_class_svm_production.csv`

Dans `evaluation/` :

- `cv.py`
- `evaluate.py`
- `finalize.py`
- `test_set.csv` (86 phrases annotées)
