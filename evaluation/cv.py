"""K-fold cross-validation rapide (k=3) sur les 4 baselines sklearn."""
import re, ast, unicodedata
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.base import clone

HERE = Path("/sessions/busy-stoic-curie/mnt/mémoire/evaluation")
RESULTS = HERE / "results"


def norm(t):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", str(t)) if not unicodedata.combining(c)).lower().strip().split())


src = open(HERE.parent / "app.py").read()
training = ast.literal_eval(re.search(r"training_data = (\[[\s\S]+?\n    \])", src).group(1))
train_df = pd.DataFrame(training, columns=["text", "intent"])
train_df["text_norm"] = train_df["text"].apply(norm)

models = {
    "SVM (production)": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", CalibratedClassifierCV(LinearSVC(dual="auto", random_state=42), cv=2)),
    ]),
    "Naive Bayes": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", MultinomialNB()),
    ]),
    "Logistic Regression": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000, random_state=42)),
    ]),
    "Random Forest": Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
    ]),
}

skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
rows = []
for name, pipe in models.items():
    scores = cross_val_score(clone(pipe), train_df["text_norm"], train_df["intent"], cv=skf, scoring="f1_macro", n_jobs=1)
    rows.append({"Modele": name, "CV F1 macro mean": scores.mean(), "CV F1 macro std": scores.std(), "Folds": list(scores)})
    print(f"  {name:22s} F1m={scores.mean():.3f} +/- {scores.std():.3f}  (folds={[f'{s:.3f}' for s in scores]})")

df = pd.DataFrame(rows)
df["Folds"] = df["Folds"].astype(str)
df.to_csv(RESULTS / "cv_results.csv", index=False, float_format="%.3f")
print(f"\nResultats CV : {RESULTS}/cv_results.csv")
