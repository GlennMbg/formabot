# Rapport de robustesse au bruit — FormaBot

*Mémoire M2 Nexa — RNCP 37137 — sprint 3 de la roadmap*

## Méthodologie

Le test set indépendant (91 phrases distinctes du training set) est passé par quatre générateurs de bruit déterministes (seed=42 pour reproductibilité) :

- **`typos`** : 1 à 2 modifications de caractères par mot (swap, delete, duplicate, substitute) sur 30% des mots de longueur ≥ 5 chars
- **`accents`** : retrait complet des accents (simule un clavier mobile sans IME)
- **`case`** : casse mélangée aléatoire caractère par caractère
- **`parasites`** : insertion de 1-2 mots parasites typiques de l'oral/chat ("euh", "bah", "stp", "svp", "du coup", "en fait", "ben", "tu vois")
- **`all`** : cumul des 4 bruits, simulant le pire des cas

Le classifieur reste **strictement identique** à celui de production (SVM + TF-IDF + `CalibratedClassifierCV` + couches de normalisation et correction fuzzy intégrées dans `normalize_text`).

## Résultats

| variant   |   accuracy |   f1_macro |   f1_weighted |   n |   delta_f1_macro_pct |
|:----------|-----------:|-----------:|--------------:|----:|---------------------:|
| clean     |      0.725 |      0.719 |         0.729 |  91 |                0.000 |
| typos     |      0.648 |      0.626 |         0.649 |  91 |              -13.010 |
| accents   |      0.725 |      0.719 |         0.729 |  91 |                0.000 |
| case      |      0.725 |      0.719 |         0.729 |  91 |                0.000 |
| parasites |      0.681 |      0.681 |         0.686 |  91 |               -5.290 |
| all       |      0.560 |      0.548 |         0.557 |  91 |              -23.810 |

## Lecture

- **`typos`** : F1 macro 0.626 (Δ -13.0% vs clean) — impact modéré.
- **`accents`** : F1 macro 0.719 (Δ 0.0% vs clean) — impact négligeable.
- **`case`** : F1 macro 0.719 (Δ 0.0% vs clean) — impact négligeable.
- **`parasites`** : F1 macro 0.681 (Δ -5.3% vs clean) — impact modéré.
- **`all`** : F1 macro 0.548 (Δ -23.8% vs clean) — impact significatif.

## Rôle de la couche de normalisation

La fonction `normalize_text()` du pipeline applique trois opérations avant la vectorisation TF-IDF :

1. **`strip_accents()`** — retire tous les diacritiques via `unicodedata.normalize("NFKD")`. Cela annule complètement l'impact de la variante `accents`.
2. **`lower()`** — uniformise la casse. Cela annule complètement l'impact de la variante `case`.
3. **`_correct_typo()`** — correcteur fuzzy ciblé sur 16 mots-clés métier (Levenshtein, seuil score ≥ 82, contrôle de longueur ±2 chars). Cela atténue significativement l'impact des typos sur le vocabulaire métier.

Les mots parasites ("euh", "stp") ne sont **pas** filtrés explicitement, mais leur impact reste modéré car le SVM + TF-IDF avec n-grams 1-2 reste centré sur les unigrammes les plus discriminants. Pour un futur sprint, on pourrait ajouter une liste de stopwords métier dans le `TfidfVectorizer`.

## Limites de cette évaluation

- **Taille du test set** : 91 phrases, donc une variation de F1 de 0.01 correspond à environ 1 phrase mal classée. Les écarts sub-0.05 sont à interpréter avec prudence.
- **Bruit synthétique** : les variantes générées ne reproduisent pas parfaitement les patterns réels d'un dirigeant TPE BTP. Une vraie validation nécessiterait un corpus de requêtes naturelles collectées sur la version déployée.
- **Pas de mesure d'effet sur la sélection de formation** : on évalue uniquement la classification d'intention, pas la qualité de la formation recommandée in fine.

## Fichiers produits

- `evaluation/test_set_formations.csv`
- `evaluation/results/test_set_noisy_typos.csv`
- `evaluation/results/test_set_noisy_accents.csv`
- `evaluation/results/test_set_noisy_case.csv`
- `evaluation/results/test_set_noisy_parasites.csv`
- `evaluation/results/test_set_noisy_all.csv`
- `evaluation/results/robustness_table.csv`
- `evaluation/results/robustness_plot.png`
