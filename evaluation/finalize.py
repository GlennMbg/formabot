"""Charge les per_class CSV deja produits, mesure la latence et produit le
tableau comparatif + le plot final. Conçu pour tenir dans 45s."""
import re, unicodedata, ast, time
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

HERE = Path("/sessions/busy-stoic-curie/mnt/mémoire/evaluation")
RESULTS = HERE / "results"


def norm(t):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", str(t)) if not unicodedata.combining(c)).lower().strip().split())


# Charge training + test
src = open(HERE.parent / "app.py").read()
training = ast.literal_eval(re.search(r"training_data = (\[[\s\S]+?\n    \])", src).group(1))
train_df = pd.DataFrame(training, columns=["text", "intent"])
train_df["text_norm"] = train_df["text"].apply(norm)
test_df = pd.read_csv(HERE / "test_set.csv")
test_df["text_norm"] = test_df["text"].apply(norm)

# Modeles
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
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
    ]),
}

# Pour chaque modele : fit + latence + lecture du per_class
def slugify(s):
    return re.sub(r"[^\w]+", "_", s.lower()).strip("_")

results = []
for name, pipe in models.items():
    t0 = time.perf_counter()
    pipe.fit(train_df["text_norm"], train_df["intent"])
    t_fit = time.perf_counter() - t0

    # Latence : 10 phrases x 10 runs
    samples = test_df["text_norm"].tolist()[:10]
    for s in samples[:3]: pipe.predict([s])  # warmup
    durs = []
    for _ in range(10):
        for s in samples:
            t = time.perf_counter()
            pipe.predict([s])
            durs.append((time.perf_counter() - t) * 1000)
    durs = np.array(durs)

    # Lit per_class CSV
    pc = pd.read_csv(RESULTS / f"per_class_{slugify(name)}.csv", index_col=0)
    accuracy = pc.loc["accuracy", "f1-score"]  # convention sklearn
    f1_macro = pc.loc["macro avg", "f1-score"]
    f1_weighted = pc.loc["weighted avg", "f1-score"]

    results.append({
        "Modele": name,
        "Accuracy (test)": accuracy,
        "F1 macro (test)": f1_macro,
        "F1 weighted (test)": f1_weighted,
        "Latence p50 (ms)": float(np.percentile(durs, 50)),
        "Latence p95 (ms)": float(np.percentile(durs, 95)),
        "Temps fit (s)": t_fit,
    })
    print(f"  {name:22s} acc={accuracy:.3f} F1m={f1_macro:.3f} lat_p95={np.percentile(durs,95):.1f}ms")

# Tableau comparatif
cmp = pd.DataFrame(results)
cmp.to_csv(RESULTS / "comparison_table.csv", index=False, float_format="%.3f")
print()
print(cmp.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

# Plot F1 vs latence
fig, ax = plt.subplots(figsize=(8, 5))
for r in results:
    ax.scatter(r["Latence p95 (ms)"], r["F1 macro (test)"], s=120)
    ax.annotate(r["Modele"], (r["Latence p95 (ms)"], r["F1 macro (test)"]),
                xytext=(8, 0), textcoords="offset points", fontsize=10)
ax.set_xscale("log")
ax.set_xlabel("Latence p95 (ms, echelle log)")
ax.set_ylabel("F1 macro (test independant)")
ax.set_title("Compromis performance / latence")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(RESULTS / "f1_vs_latency.png", dpi=120, bbox_inches="tight")
plt.close(fig)

print("\nFichiers produits :")
for f in sorted(RESULTS.glob("*")):
    print(f"  {f.name}")
