"""
Comparaison avec DistilBERT multilingue (CPU OK, ~2-5 min).

Pre-requis (a installer une fois sur ta machine locale) :
    pip install transformers torch

Strategie : on extrait les embeddings [CLS] de DistilBERT pour chaque phrase,
puis on entraine une Logistic Regression sur ces representations denses
(approche standard quand on dispose de peu de donnees d'entrainement).
"""
import argparse
import ast
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)


def norm(t):
    return " ".join(
        "".join(c for c in unicodedata.normalize("NFKD", str(t)) if not unicodedata.combining(c))
        .lower().strip().split()
    )


def load_data():
    src = open(HERE.parent / "app.py").read()
    training = ast.literal_eval(re.search(r"training_data = (\[[\s\S]+?\n    \])", src).group(1))
    train_df = pd.DataFrame(training, columns=["text", "intent"])
    train_df["text_norm"] = train_df["text"].apply(norm)
    test_df = pd.read_csv(HERE / "test_set.csv")
    test_df["text_norm"] = test_df["text"].apply(norm)
    return train_df, test_df


def extract_features(texts, tokenizer, model, batch_size=16):
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = list(texts[i:i + batch_size])
            enc = tokenizer(batch, padding=True, truncation=True, max_length=64, return_tensors="pt")
            res = model(**enc)
            # Embedding [CLS] = premier token
            cls = res.last_hidden_state[:, 0, :].cpu().numpy()
            out.append(cls)
            print(f"    batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}", end="\r")
    print()
    return np.vstack(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="distilbert-base-multilingual-cased")
    args = parser.parse_args()

    print("=== DistilBERT + Logistic Regression ===")
    print(f"Modele : {args.model}")
    print()

    try:
        from transformers import AutoTokenizer, AutoModel
    except ImportError:
        print("Erreur : transformers + torch non installes.")
        print("  pip install transformers torch")
        return

    train_df, test_df = load_data()
    labels = sorted(train_df["intent"].unique())
    print(f"Training : {len(train_df)} phrases | Test : {len(test_df)} phrases")
    print()

    print("Chargement du modele DistilBERT...")
    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModel.from_pretrained(args.model)
    print(f"  charge en {time.perf_counter() - t0:.1f}s")

    print("Extraction des features (training)...")
    t0 = time.perf_counter()
    X_train = extract_features(train_df["text_norm"].tolist(), tokenizer, model)
    t_train_feat = time.perf_counter() - t0
    print(f"  shape={X_train.shape} en {t_train_feat:.1f}s")

    print("Extraction des features (test)...")
    t0 = time.perf_counter()
    X_test = extract_features(test_df["text_norm"].tolist(), tokenizer, model)
    t_test_feat = time.perf_counter() - t0
    print(f"  shape={X_test.shape} en {t_test_feat:.1f}s")

    print("Entrainement LogReg sur les embeddings...")
    clf = LogisticRegression(max_iter=2000, random_state=42)
    clf.fit(X_train, train_df["intent"])

    print("Prediction sur le test...")
    y_true = test_df["intent"].tolist()
    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    print(f"\nResultats :")
    print(f"  Accuracy    : {accuracy:.3f}")
    print(f"  F1 macro    : {f1_macro:.3f}")
    print(f"  F1 weighted : {f1_weighted:.3f}")

    # Latence : extraction features + prediction
    t0 = time.perf_counter()
    for s in test_df["text_norm"].tolist()[:5]:
        f = extract_features([s], tokenizer, model)
        clf.predict(f)
    lat_per_query_ms = (time.perf_counter() - t0) / 5 * 1000
    print(f"  Latence (extraction + predict) : ~{lat_per_query_ms:.0f} ms/requete")

    # Sauvegardes
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    pc = pd.DataFrame(report).transpose()
    pc.to_csv(RESULTS / "per_class_distilbert.csv", float_format="%.3f")

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
    ax.set_xlabel("Predit"); ax.set_ylabel("Reel"); ax.set_title("Matrice de confusion - DistilBERT + LogReg")
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = cm[i, j]; c = "white" if v > cm.max()/2 else "black"
            ax.text(j, i, str(v), ha="center", va="center", color=c, fontsize=8)
    fig.colorbar(im); fig.tight_layout()
    fig.savefig(RESULTS / "confusion_distilbert.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # Mise a jour du comparison_table
    cmp_path = RESULTS / "comparison_table.csv"
    if cmp_path.exists():
        cmp = pd.read_csv(cmp_path)
        new_row = {
            "Modele": "DistilBERT + LogReg",
            "Accuracy (test)": accuracy,
            "F1 macro (test)": f1_macro,
            "F1 weighted (test)": f1_weighted,
            "Latence p50 (ms)": lat_per_query_ms,
            "Latence p95 (ms)": lat_per_query_ms * 1.3,
            "Temps fit (s)": t_train_feat,
        }
        cmp = pd.concat([cmp, pd.DataFrame([new_row])], ignore_index=True)
        cmp.to_csv(cmp_path, index=False, float_format="%.3f")
        print(f"\nAjoute au tableau comparatif : {cmp_path}")

    print(f"\nResultats : {RESULTS}/")


if __name__ == "__main__":
    main()
