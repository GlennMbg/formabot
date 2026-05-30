"""
FormaBot - Assistant conversationnel de recommandation de formations
Domaine : formations pour dirigeants TPE BTP (ADN Potentiel)

Memoire M2 Nexa - RNCP 37137 Chef de projet Data & IA
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import string
import json
import os
import re
import uuid
import unicodedata
import random
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix, classification_report

# Fuzzy matching : rapidfuzz prefere, fallback fuzzywuzzy
try:
    from rapidfuzz import process as _fuzz_process
    _FUZZ_BACKEND = "rapidfuzz"
except ImportError:
    from fuzzywuzzy import process as _fuzz_process
    _FUZZ_BACKEND = "fuzzywuzzy"


def _fuzz_extract_one(query, choices):
    """Wrapper unifie : (match_str, score 0-100) quelle que soit la lib."""
    result = _fuzz_process.extractOne(query, choices)
    if result is None:
        return None, 0
    return result[0], result[1]


# Detection de langue (optionnelle)
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 42
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

# -----------------------------------------------------------------------------
# 1. Configuration de la page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FormaBot - ADN Potentiel",
    page_icon="\U0001F393",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Constantes
# -----------------------------------------------------------------------------
DATASET_FILE = "formations_adn.csv"     # Fallback / source de verite si la DB est absente
SQLITE_DB_FILE = "formabot.db"          # Source preferee (cree par build_sqlite_db.py)
TRAINING_CORPUS_FILE = "formations_training_corpus.csv"
HISTORY_FILE = "conversations_formabot.json"
DEFAULT_TOP_N = 10
MAX_TOP_N = 30
RECENT_MEMORY_SIZE = 8

DEFAULT_SYSTEM_PROMPT = (
    "Tu es FormaBot, l'assistant conversationnel d'ADN Potentiel, "
    "cabinet de formation et de coaching specialise dans l'accompagnement des dirigeants de TPE du BTP. "
    "Tu reponds de maniere concise, bienveillante et factuelle. "
    "Tu t'appuies uniquement sur le catalogue de formations fourni."
)


# -----------------------------------------------------------------------------
# 2. Utilitaires : normalisation & detection langue
# -----------------------------------------------------------------------------
def strip_accents(text):
    if not isinstance(text, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


# Mots cles metier sensibles aux typos (le BTP ecrit vite sur mobile)
# Les variantes les plus proches sont corrigees automatiquement avant classification
_TYPO_TARGETS = ["formation", "formations", "manager", "management", "leadership",
                 "communication", "coaching", "delegation", "stress",
                 "commercial", "commerciale", "commerce", "conference",
                 "conferences", "conseil", "consulting"]


def _correct_typo(word, targets=_TYPO_TARGETS, min_len=6, max_len_diff=2, min_score=82):
    """Si `word` est proche d'un mot-cle metier ET de longueur similaire, le corrige.
    Sinon, retourne le mot inchange.
    Contraintes :
    - mot d'au moins min_len caracteres (evite la correction sur 'merci', 'haut', etc.)
    - difference de longueur <= max_len_diff (evite 'merci' -> 'commercial')
    - score similarite >= min_score
    """
    if len(word) < min_len:
        return word
    best_target = None
    best_score = 0
    for target in targets:
        # Filtre prealable : longueur similaire seulement
        if abs(len(word) - len(target)) > max_len_diff:
            continue
        match, score = _fuzz_extract_one(word, [target])
        if score is not None and score > best_score:
            best_score = score
            best_target = match
    if best_score >= min_score and best_target and best_target != word:
        return best_target
    return word


def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = strip_accents(text).lower().strip()
    # Correction des typos sur les mots cles metier (mobilier robustesse au bruit)
    words = text.split()
    corrected = [_correct_typo(w) for w in words]
    return " ".join(corrected)


def detect_language(text):
    if not LANGDETECT_AVAILABLE or not text or len(text.strip()) < 3:
        return "unknown"
    try:
        return detect(text)
    except Exception:
        return "unknown"


# -----------------------------------------------------------------------------
# 3. Historique persistant (JSON)
# -----------------------------------------------------------------------------
def load_conversations():
    if not os.path.exists(HISTORY_FILE):
        return {"conversations": []}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "conversations" not in data:
                data["conversations"] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {"conversations": []}


def save_conversations(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        st.warning(f"Impossible de sauvegarder l'historique : {e}")


def new_conversation_id():
    return str(uuid.uuid4())


def get_conversation(data, conv_id):
    for conv in data["conversations"]:
        if conv["id"] == conv_id:
            return conv
    return None


def upsert_current_conversation():
    if "current_conv_id" not in st.session_state:
        return
    data = load_conversations()
    conv = get_conversation(data, st.session_state.current_conv_id)
    title = "Nouvelle conversation"
    for m in st.session_state.messages:
        if m["role"] == "user":
            title = m["content"][:50] + ("..." if len(m["content"]) > 50 else "")
            break
    payload = {
        "id": st.session_state.current_conv_id,
        "title": title,
        "created_at": st.session_state.get("current_conv_created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "system_prompt": st.session_state.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        "messages": st.session_state.messages,
    }
    if conv is None:
        data["conversations"].insert(0, payload)
    else:
        idx = data["conversations"].index(conv)
        data["conversations"][idx] = payload
    save_conversations(data)


def fresh_context():
    return {"last_title": None, "last_intent": None, "recently_recommended": []}


def start_new_conversation():
    st.session_state.current_conv_id = new_conversation_id()
    st.session_state.current_conv_created_at = datetime.now().isoformat()
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Bonjour ! Je suis FormaBot, l'assistant d'ADN Potentiel. Pose-moi une question sur nos formations ou demande une recommandation."}
    ]
    st.session_state.context = fresh_context()


def load_conversation_into_session(conv_id):
    data = load_conversations()
    conv = get_conversation(data, conv_id)
    if conv is None:
        return
    st.session_state.current_conv_id = conv["id"]
    st.session_state.current_conv_created_at = conv.get("created_at", datetime.now().isoformat())
    st.session_state.messages = conv.get("messages", [])
    st.session_state.system_prompt = conv.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
    st.session_state.context = fresh_context()


def delete_conversation(conv_id):
    data = load_conversations()
    data["conversations"] = [c for c in data["conversations"] if c["id"] != conv_id]
    save_conversations(data)
    if st.session_state.get("current_conv_id") == conv_id:
        start_new_conversation()


# -----------------------------------------------------------------------------
# 4. Chargement du catalogue + corpus (cache)
# -----------------------------------------------------------------------------
def _split_pipe(x):
    if not isinstance(x, str) or not x.strip():
        return []
    return [s.strip() for s in x.split("|") if s.strip()]


def _split_semicolon(x):
    if not isinstance(x, str) or not x.strip():
        return []
    return [s.strip() for s in x.split(";") if s.strip()]


def _load_from_sqlite(db_path):
    """Charge le catalogue depuis la base SQLite. Renvoie un DataFrame ou None."""
    import sqlite3
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM formations", conn)
        conn.close()
        # SQLite stocke les booleens en INTEGER 0/1, on les remet en bool
        if "cpf_eligible" in df.columns:
            df["cpf_eligible"] = df["cpf_eligible"].astype(bool)
        if "qualiopi_certified" in df.columns:
            df["qualiopi_certified"] = df["qualiopi_certified"].astype(bool)
        return df
    except Exception as e:
        st.warning(f"Echec du chargement SQLite ({e}), fallback CSV.")
        return None


def _load_from_csv(csv_path):
    """Charge le catalogue depuis le CSV. Renvoie un DataFrame ou None."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return None
    # Conversion des booleens depuis les strings du CSV
    df["cpf_eligible"] = df.get("cpf_eligible").astype(str).str.lower().isin(["true", "1", "yes", "oui"])
    df["qualiopi_certified"] = df.get("qualiopi_certified").astype(str).str.lower().isin(["true", "1", "yes", "oui"])
    return df


@st.cache_resource
def load_resources():
    """Strategie de chargement :
    1. Tente la base SQLite (formabot.db) - source preferee, plus rapide pour les requetes
    2. Sinon fallback sur le CSV (formations_adn.csv)
    Dans tous les cas le DataFrame en sortie est identique."""
    df = _load_from_sqlite(SQLITE_DB_FILE)
    source = "sqlite"
    if df is None:
        df = _load_from_csv(DATASET_FILE)
        source = "csv"
    if df is None:
        return None, None, None, [], []

    # Parse champs structures (objectives ; et target_audience |)
    df["target_audience"] = df.get("target_audience", "").apply(_split_pipe)
    df["objectives"] = df.get("objectives", "").apply(_split_semicolon)

    # Typage numerique
    df["duration_hours"] = pd.to_numeric(df.get("duration_hours"), errors="coerce")
    df["price_eur_ht"] = pd.to_numeric(df.get("price_eur_ht"), errors="coerce")
    df["id"] = pd.to_numeric(df.get("id"), errors="coerce")

    for col in ["title", "theme", "subtheme", "description", "prerequisites", "format",
                "duration_label", "session_type", "level", "certification", "url"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
    if "next_session" in df.columns:
        df["next_session"] = df["next_session"].fillna("Non communique").astype(str)

    df = df.drop_duplicates(subset="title")
    df = df[df["title"] != ""].copy()
    # Memorise la source pour affichage dans l'UI
    df.attrs["source"] = source

    available_themes = sorted({t for t in df["theme"].tolist() if t})
    available_formats = sorted({f for f in df["format"].tolist() if f})

    try:
        train_df = pd.read_csv(TRAINING_CORPUS_FILE)
    except FileNotFoundError:
        return df, None, None, available_themes, available_formats

    train_df["text_norm"] = train_df["text"].apply(normalize_text)

    svc = LinearSVC(dual="auto", random_state=42)
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("svm", CalibratedClassifierCV(svc, cv=2))
    ])
    clf.fit(train_df["text_norm"], train_df["intent"])

    return df, clf, train_df, available_themes, available_formats


df, clf, train_df, AVAILABLE_THEMES, AVAILABLE_FORMATS = load_resources()


# -----------------------------------------------------------------------------
# 5. Index de recherche de titres
# -----------------------------------------------------------------------------
@st.cache_resource
def build_title_index(_df):
    if _df is None or _df.empty:
        return {}, []
    index = {}
    for _, row in _df.iterrows():
        canonical = row["title"]
        if not canonical or len(canonical) < 3:
            continue
        index.setdefault(canonical, canonical)
        sub = row.get("subtheme", "")
        if isinstance(sub, str) and len(sub) >= 4:
            index.setdefault(sub, canonical)
    return index, list(index.keys())


TITLE_INDEX, TITLE_KEYS = build_title_index(df)


# -----------------------------------------------------------------------------
# 6. Fonctions logiques (chatbot)
# -----------------------------------------------------------------------------
def extract_title(text, dataframe, min_score=78):
    if dataframe is None or not TITLE_KEYS:
        return None
    cleaned = text.translate(str.maketrans("", "", string.punctuation)).strip().lower()
    words = cleaned.split()
    if not words:
        return None
    seen = set()
    candidates = []
    for i in range(len(words)):
        for j in range(i + 1, min(i + 7, len(words)) + 1):
            cand = " ".join(words[i:j])
            if len(cand) >= 4 and cand not in seen:
                seen.add(cand)
                candidates.append(cand)
    best_canonical = None
    best_score = 0
    for cand in candidates:
        match, score = _fuzz_extract_one(cand, TITLE_KEYS)
        if score >= 95:
            return TITLE_INDEX.get(match)
        if score > best_score and score >= min_score:
            best_score = score
            best_canonical = TITLE_INDEX.get(match)
    return best_canonical


# Mots-cles -> theme canonique (alignes sur le catalogue ADN Potentiel V15)
THEME_KEYWORDS = {
    # Management
    "management": "Management",
    "manager": "Management",
    "leadership": "Management",
    "leader": "Management",
    "delegation": "Management",
    "deleguer": "Management",
    "marque employeur": "Management",
    "fideliser": "Management",
    "entretien professionnel": "Management",
    "entretien annuel": "Management",
    "entretien d evaluation": "Management",
    "evaluation": "Management",
    "pnl": "Management",
    "neurosciences": "Management",
    "manageriale": "Management",
    "manageriaux": "Management",
    # Soft skills
    "soft skills": "Soft skills",
    "communication non violente": "Soft skills",
    "cnv": "Soft skills",
    "stress": "Soft skills",
    "emotions": "Soft skills",
    "emotion": "Soft skills",
    "intelligence emotionnelle": "Soft skills",
    "prise de parole": "Soft skills",
    "personal branding": "Soft skills",
    "confiance en soi": "Soft skills",
    "voix": "Soft skills",
    "discours": "Soft skills",
    "argumentation": "Soft skills",
    "relaxation": "Soft skills",
    "meditation": "Soft skills",
    "personnalites difficiles": "Soft skills",
    "personnalite difficile": "Soft skills",
    "intelligence artificielle": "Soft skills",
    "ia": "Soft skills",
    "ai": "Soft skills",
    "cohesion": "Soft skills",
    "travailler en equipe": "Soft skills",
    # Commerce
    "commerce": "Commerce",
    "commercial": "Commerce",
    "commerciaux": "Commerce",
    "vente": "Commerce",
    "vendre": "Commerce",
    "prospection": "Commerce",
    "prospecter": "Commerce",
    "experience client": "Commerce",
    "relation client": "Commerce",
    "accueil client": "Commerce",
    "clients difficiles": "Commerce",
    "linkedin": "Commerce",
    "social selling": "Commerce",
    "negociation": "Commerce",
    "fidelisation": "Commerce",
    "appels d offres": "Commerce",
    "appel d offres": "Commerce",
    # Coaching
    "coaching": "Coaching",
    "coach": "Coaching",
    "coaching executif": "Coaching",
    "coaching individuel": "Coaching",
    "coaching collectif": "Coaching",
    # Conseil & Consulting
    "conseil": "Conseil & Consulting",
    "consulting": "Conseil & Consulting",
    "audit": "Conseil & Consulting",
    "rps": "Conseil & Consulting",
    "risques psychosociaux": "Conseil & Consulting",
    "duerp": "Conseil & Consulting",
    "document unique": "Conseil & Consulting",
    "restructuration": "Conseil & Consulting",
    "transformation": "Conseil & Consulting",
    "strategie rh": "Conseil & Consulting",
    "politique rh": "Conseil & Consulting",
    # Conferences
    "conference": "Conférences",
    "conferences": "Conférences",
    "engagement": "Conférences",
}


def extract_theme(user_input_norm, available_themes=None):
    for key in sorted(THEME_KEYWORDS.keys(), key=len, reverse=True):
        if key in user_input_norm:
            cand = THEME_KEYWORDS[key]
            if available_themes is None or cand in available_themes:
                return cand
    if available_themes:
        for t in sorted(available_themes, key=len, reverse=True):
            if normalize_text(t) in user_input_norm:
                return t
    return None


FORMAT_KEYWORDS = {
    "presentiel": "Présentiel", "en presentiel": "Présentiel",
    "in person": "Présentiel", "in-person": "Présentiel",
    "in classroom": "Présentiel", "classroom": "Présentiel", "salle": "Présentiel",
    "distanciel": "Distanciel", "a distance": "Distanciel", "distance": "Distanciel",
    "remote": "Distanciel", "online": "Distanciel", "en ligne": "Distanciel",
    "ligne": "Distanciel", "visio": "Distanciel", "visioconference": "Distanciel",
    "hybride": "Hybride", "hybrid": "Hybride",
    "e-learning": "Distanciel", "elearning": "Distanciel",
}


def extract_format(user_input_norm, available_formats=None):
    for key in sorted(FORMAT_KEYWORDS.keys(), key=len, reverse=True):
        if key in user_input_norm:
            cand = FORMAT_KEYWORDS[key]
            if available_formats is None or cand in available_formats:
                return cand
    return None


def extract_duration_filter(user_input_norm):
    short_kw = ["courte", "court ", "rapide", "express", "short", "half-day",
                "demi-journee", "demi journee", "une journee"]
    long_kw = ["longue", "long ", "long format", "intensif", "plusieurs jours",
               "multi-day", "multi day", "semaine"]
    is_short = any(k in user_input_norm for k in short_kw)
    is_long = any(k in user_input_norm for k in long_kw)
    m_less = re.search(r"moins de (\d+)\s*(heure|h|jour|j)", user_input_norm)
    m_more = re.search(r"plus de (\d+)\s*(heure|h|jour|j)", user_input_norm)
    m_under = re.search(r"under (\d+)\s*(hour|day)", user_input_norm)
    if m_less:
        n, unit = int(m_less.group(1)), m_less.group(2)
        threshold = n if unit.startswith("h") else n * 7
        return lambda d: d[d["duration_hours"] <= threshold]
    if m_more:
        n, unit = int(m_more.group(1)), m_more.group(2)
        threshold = n if unit.startswith("h") else n * 7
        return lambda d: d[d["duration_hours"] >= threshold]
    if m_under:
        n, unit = int(m_under.group(1)), m_under.group(2)
        threshold = n if unit.startswith("h") else n * 7
        return lambda d: d[d["duration_hours"] <= threshold]
    if is_short and not is_long:
        return lambda d: d[d["duration_hours"] <= 7]
    if is_long and not is_short:
        return lambda d: d[d["duration_hours"] >= 14]
    return None


def extract_audience_filter(user_input_norm):
    audience_kw = {
        "dirigeant": "Dirigeant", "patron": "Dirigeant", "chef d entreprise": "Dirigeant",
        "owner": "Dirigeant", "executive": "Dirigeant",
        "manager": "Manager", "managers": "Manager",
        "artisan": "Dirigeant TPE BTP", "tpe btp": "TPE BTP", "btp tpe": "TPE BTP",
    }
    matched = None
    for k, v in sorted(audience_kw.items(), key=lambda x: -len(x[0])):
        if k in user_input_norm:
            matched = v
            break
    if not matched:
        return None

    def _f(d):
        return d[d["target_audience"].apply(
            lambda lst: any(matched.lower() in a.lower() for a in lst) if isinstance(lst, list) else False
        )]
    return _f


def extract_certification_filter(user_input_norm):
    if any(k in user_input_norm for k in ["cpf", "compte formation", "compte personnel"]):
        return lambda d: d[d["cpf_eligible"] == True], "CPF"
    if "qualiopi" in user_input_norm:
        return lambda d: d[d["qualiopi_certified"] == True], "Qualiopi"
    if "rncp" in user_input_norm or "certifiant" in user_input_norm or "certified" in user_input_norm:
        return lambda d: d[d["qualiopi_certified"] == True], "certifiante"
    return None, None


def extract_top_n(user_input_norm, default=DEFAULT_TOP_N, maximum=MAX_TOP_N):
    m = re.search(r"\btop\s*(\d+)", user_input_norm)
    if m:
        return max(1, min(maximum, int(m.group(1))))
    m = re.search(r"\b(\d+)\s+(?:meilleur(?:e?s?)|best|formations?|programmes?)", user_input_norm)
    if m:
        return max(1, min(maximum, int(m.group(1))))
    return default


def pick_formation(subset_df, recently_recommended):
    if subset_df is None or subset_df.empty:
        return None
    fresh = subset_df[~subset_df["title"].isin(recently_recommended)]
    if fresh.empty:
        if len(subset_df) > 1 and recently_recommended:
            last = recently_recommended[-1]
            fresh = subset_df[subset_df["title"] != last]
            if fresh.empty:
                fresh = subset_df
        else:
            fresh = subset_df
    return fresh.sample(1, random_state=random.randint(0, 10**9)).iloc[0]


def remember_recommendation(context, title):
    if not title:
        return
    rec = context.setdefault("recently_recommended", [])
    if title in rec:
        rec.remove(title)
    rec.append(title)
    if len(rec) > RECENT_MEMORY_SIZE:
        del rec[0]
    context["last_title"] = title


def fmt_price(p):
    """ADN Potentiel : prix sur devis pour la plupart des formations (0 = sur demande)."""
    if pd.isna(p) or p == 0:
        return "prix sur devis"
    try:
        return f"{int(p)} EUR HT"
    except (ValueError, TypeError):
        return str(p)


def fmt_duration(row):
    label = row.get("duration_label", "")
    if isinstance(label, str) and label:
        return label
    h = row.get("duration_hours")
    if pd.notna(h):
        try:
            return f"{int(h)}h"
        except (ValueError, TypeError):
            pass
    return "non precise"


def format_formation_short(row):
    return (f"- **{row['title']}** &mdash; {row['theme']} &middot; {fmt_duration(row)} &middot; "
            f"{row.get('format','?')} &middot; {fmt_price(row.get('price_eur_ht'))}")


def format_formation_list(formations_df, max_items=10):
    if formations_df is None or formations_df.empty:
        return ""
    lines = [format_formation_short(row) for _, row in formations_df.head(max_items).iterrows()]
    extra = ""
    if len(formations_df) > max_items:
        extra = f"\n\n*...et {len(formations_df) - max_items} autres.*"
    return "\n".join(lines) + extra


def filter_by_theme(dataframe, theme):
    return dataframe[dataframe["theme"] == theme]


def filter_by_format(dataframe, fmt):
    return dataframe[dataframe["format"] == fmt]


def get_bot_response(user_input, dataframe, model, context=None,
                     system_prompt=None, available_themes=None, available_formats=None):
    if dataframe is None:
        return ("Erreur : catalogue introuvable.", None, "unknown", context)
    if model is None:
        return ("Erreur : modele d'intention introuvable.", None, "unknown", context)

    if context is None:
        context = fresh_context()
    context.setdefault("recently_recommended", [])

    user_input_clean = user_input.rstrip("!?.,;: ").strip()
    if not user_input_clean:
        return "Je n'ai pas compris, peux-tu reformuler ?", None, "unknown", context

    lang = detect_language(user_input_clean)
    user_input_norm = normalize_text(user_input_clean)

    proba = model.predict_proba([user_input_norm])[0]
    classes = model.classes_
    conf_data = pd.DataFrame({"Intention": classes, "Confiance": proba}) \
        .sort_values(by="Confiance", ascending=False)

    intent = conf_data.iloc[0]["Intention"]
    top_conf = float(conf_data.iloc[0]["Confiance"])
    if top_conf < 0.25:
        intent = "fallback"

    if re.search(r"\btop\s*\d+\b", user_input_norm):
        intent = "list_top"
    elif re.search(r"\b(les\s+)?meilleur(?:e?s?)\s+formations?\b", user_input_norm) and intent != "list_top":
        intent = "list_top"

    # === Override : titre precis detecte => privilege ask_info ===
    # Si l'utilisateur mentionne explicitement une formation par son nom
    # (detecte par extract_title), c'est probablement une demande d'info detaillee,
    # pas une recherche generique. On bascule sauf si une action explicite est
    # presente dans la phrase ('prix', 'duree', 'objectifs', 'format', ou 'top').
    # === Override : titre precis detecte => privilege ask_info ===
    # On detecte un titre, puis on verifie qu'au moins un *mot significatif* du
    # titre apparait textuellement dans la phrase de l'utilisateur (apres
    # normalisation). Cela evite les faux positifs fuzzy ('coaching' qui
    # matcherait 'Reveillez le leader qui sommeille en vous').
    info_intents = ["ask_info", "ask_price", "ask_duration", "ask_format", "ask_objectives"]
    detected_title = extract_title(user_input_clean, dataframe)

    def _title_significantly_in_input(title, user_norm):
        """Renvoie True si un mot significatif (>= 4 chars, non vide) du titre
        est present dans la phrase utilisateur normalisee."""
        if not title:
            return False
        title_norm = normalize_text(title)
        # Mots du titre suffisamment significatifs
        STOP = {"avec","dans","pour","sur","sa","ses","et","ou","le","la","les","une","un","de","du","des","aux","au","en"}
        for w in title_norm.split():
            if len(w) >= 4 and w not in STOP and w in user_norm:
                return True
        return False

    if (detected_title and intent not in info_intents and intent != "list_top"
            and _title_significantly_in_input(detected_title, user_input_norm)):
        not_info_signals = ["prix", "coute", "cost", "tarif",
                            "duree", "duration", "combien d", "how long",
                            "format", "presentiel", "distanciel",
                            "objectif", "objective", "competence"]
        if not any(s in user_input_norm for s in not_info_signals):
            intent = "ask_info"

    requested_theme = extract_theme(user_input_norm, available_themes)
    requested_format = extract_format(user_input_norm, available_formats)
    duration_filter = extract_duration_filter(user_input_norm)
    audience_filter = extract_audience_filter(user_input_norm)
    cert_filter_tuple = extract_certification_filter(user_input_norm)
    cert_filter = cert_filter_tuple[0] if cert_filter_tuple else None
    cert_label = cert_filter_tuple[1] if cert_filter_tuple else None

    # === Override : phrases multi-criteres mal classees ===
    # Cas typique : "une formation en distanciel sur le management pour un nouveau patron"
    # Le classifieur peut hesiter entre search_by_audience/duration/format et recommend_by_theme.
    # Si la confiance est < 50%, qu'un theme est detecte, et que l'intent est un search_by_*,
    # on bascule sur recommend_by_theme. C'est generalement ce que l'utilisateur veut quand
    # plusieurs criteres se croisent autour d'un theme principal.
    search_intents = ["search_by_format", "search_by_duration", "search_by_audience", "search_by_certification"]
    if (intent in search_intents and top_conf < 0.50 and requested_theme
            and "formation" in user_input_norm):
        intent = "recommend_by_theme"

    response = "Desole, je n'ai pas compris."

    if intent == "greeting":
        response = ("Hi! I'm FormaBot, ADN Potentiel's assistant. Ask me about our trainings."
                    if lang == "en" else
                    "Bonjour ! Je suis FormaBot, l'assistant d'ADN Potentiel.")
    elif intent == "goodbye":
        response = "See you soon !" if lang == "en" else "A bientot !"
    elif intent == "thanks":
        response = "You're welcome !" if lang == "en" else "Avec plaisir !"
    elif intent == "help":
        if lang == "en":
            response = ("I can help with:\n"
                        "- Recommendations (general or by theme)\n"
                        "- Listing trainings in a theme\n"
                        "- Filtering by format / duration / audience / CPF / Qualiopi\n"
                        "- Details on a specific training (price, duration, objectives, format)\n"
                        "- Top N best-rated trainings")
        else:
            response = ("Je peux t'aider sur :\n"
                        "- des recommandations (au hasard ou par theme)\n"
                        "- la liste de toutes les formations d'un theme\n"
                        "- des filtres par format / duree / public / CPF / Qualiopi\n"
                        "- des infos detaillees sur une formation (prix, duree, objectifs, format)\n"
                        "- le top N des formations")
    elif intent == "fallback":
        response = ("I'm not sure I understand. Try: 'recommend a training', 'top 5 in management', or 'price of Manager une equipe'."
                    if lang == "en" else
                    "Je ne suis pas sur de comprendre. Essaie : 'recommande une formation', 'top 5 en management', ou 'prix de Manager une equipe'.")

    if intent == "ask_available_themes":
        if available_themes:
            themes_str = ", ".join(available_themes)
            response = (f"I cover **{len(available_themes)} themes** : {themes_str}."
                        if lang == "en" else
                        f"Je couvre **{len(available_themes)} themes** : {themes_str}.")
        else:
            response = "Aucun theme charge."

    # info_intents deja defini plus haut pour l'override 'titre detecte'
    # On reutilise detected_title (deja calcule) pour eviter un double appel a extract_title
    title = None
    used_memory = False
    if intent in info_intents:
        title = detected_title
        if not title and context.get("last_title") and not requested_theme:
            title = context["last_title"]
            used_memory = True

    if intent in info_intents:
        if not title:
            response = ("I couldn't find a training title. Can you specify?"
                        if lang == "en" else
                        "Je n'ai pas identifie de formation dans ta phrase. Peux-tu preciser le titre ?")
        else:
            row = dataframe[dataframe["title"].str.lower() == title.lower()]
            if len(row) == 0:
                row = dataframe[dataframe["title"].str.contains(title, case=False, regex=False)]
            if len(row) == 0:
                response = "Je ne trouve pas cette formation dans notre catalogue."
            else:
                row = row.iloc[0]
                memory_hint = " *(d'apres notre echange precedent)*" if used_memory else ""
                if intent == "ask_info":
                    obj_md = ""
                    if isinstance(row['objectives'], list) and row['objectives']:
                        obj_md = "\n\n**Objectifs** :\n" + "\n".join(f"- {o}" for o in row['objectives'])
                    cert_badge = (" &middot; CPF eligible" if row.get("cpf_eligible") else "") + \
                                 (" &middot; Qualiopi" if row.get("qualiopi_certified") else "")
                    response = (f"\U0001F393 **{row['title']}**{memory_hint}\n\n"
                                f"*{row['theme']} &middot; {row.get('subtheme','')}*\n\n"
                                f"{row['description']}\n\n"
                                f"**Format** : {row['format']} &middot; **Duree** : {fmt_duration(row)} &middot; "
                                f"**Prix** : {fmt_price(row['price_eur_ht'])}{cert_badge}{obj_md}")
                elif intent == "ask_price":
                    cpf_str = " (eligible CPF)" if row.get("cpf_eligible") else ""
                    response = f"La formation **{row['title']}**{memory_hint} coute **{fmt_price(row['price_eur_ht'])}**{cpf_str}."
                elif intent == "ask_duration":
                    h_str = f"{int(row['duration_hours'])}h" if pd.notna(row['duration_hours']) else "?h"
                    response = f"La formation **{row['title']}**{memory_hint} dure **{fmt_duration(row)}** ({h_str})."
                elif intent == "ask_format":
                    response = f"La formation **{row['title']}**{memory_hint} est dispensee en **{row['format']}** (modalite : {row.get('session_type','non precise')})."
                elif intent == "ask_objectives":
                    if isinstance(row['objectives'], list) and row['objectives']:
                        obj_str = "\n".join(f"- {o}" for o in row['objectives'])
                        response = f"**Objectifs de {row['title']}**{memory_hint} :\n\n{obj_str}"
                    else:
                        response = f"Pas d'objectifs detailles pour {row['title']}."
                context["last_title"] = row['title']

    if intent == "recommend_formation":
        subset = dataframe.copy()
        if requested_theme: subset = filter_by_theme(subset, requested_theme)
        if requested_format: subset = filter_by_format(subset, requested_format)
        if duration_filter: subset = duration_filter(subset)
        if audience_filter: subset = audience_filter(subset)
        if cert_filter: subset = cert_filter(subset)
        form = pick_formation(subset, context.get("recently_recommended", []))
        if form is None:
            response = "Je n'ai trouve aucune formation correspondant a ces criteres."
        else:
            response = f"Je te recommande : **{form['title']}** &mdash; {form['theme']} &middot; {fmt_duration(form)} &middot; {fmt_price(form['price_eur_ht'])}."
            remember_recommendation(context, form['title'])

    if intent == "recommend_by_theme":
        if requested_theme:
            subset = filter_by_theme(dataframe, requested_theme)
            form = pick_formation(subset, context.get("recently_recommended", []))
            if form is None:
                response = f"Aucune formation en {requested_theme}."
            else:
                response = f"En {requested_theme}, je te propose : **{form['title']}** &middot; {fmt_duration(form)} &middot; {fmt_price(form['price_eur_ht'])}."
                remember_recommendation(context, form['title'])
        else:
            response = f"Quel theme t'interesse ? Disponibles : {', '.join(available_themes) if available_themes else 'aucun'}."

    if intent == "list_by_theme":
        if requested_theme:
            # Liste filtree par theme
            subset = filter_by_theme(dataframe, requested_theme)
            if subset.empty:
                response = f"Aucune formation en {requested_theme}."
            else:
                subset = subset.sort_values(by="title")
                listing = format_formation_list(subset, max_items=15)
                response = f"**{len(subset)} formation(s) en {requested_theme}** :\n\n{listing}"
        else:
            # Pas de theme detecte -> on affiche le catalogue complet groupe par theme
            # (cas typique : 'liste de toutes les formations', 'vos formations', etc.)
            lines = []
            total = 0
            for theme in (available_themes or sorted(dataframe["theme"].unique())):
                subset_theme = filter_by_theme(dataframe, theme).sort_values(by="title")
                if subset_theme.empty:
                    continue
                lines.append(f"**{theme}** ({len(subset_theme)}) :")
                for _, row in subset_theme.head(8).iterrows():
                    lines.append(f"  - {row['title']} &middot; {fmt_duration(row)} &middot; {row.get('format','?')}")
                if len(subset_theme) > 8:
                    lines.append(f"  *(+ {len(subset_theme) - 8} autres dans ce theme)*")
                lines.append("")
                total += len(subset_theme)
            response = (f"Voici l'integralite de notre catalogue : **{total} formations et accompagnements** "
                        f"repartis sur {len(available_themes or [])} thematiques.\n\n" + "\n".join(lines))

    if intent == "list_top":
        top_n = extract_top_n(user_input_norm)
        subset = dataframe.copy()
        scope_parts = []
        if requested_theme:
            subset = filter_by_theme(subset, requested_theme)
            scope_parts.append(f"en {requested_theme}")
        if requested_format:
            subset = filter_by_format(subset, requested_format)
            scope_parts.append(f"format {requested_format}")
        scope_label = " " + " ".join(scope_parts) if scope_parts else ""
        if subset.empty:
            response = f"Aucune formation{scope_label}."
        else:
            subset = subset.sort_values(
                by=["qualiopi_certified", "cpf_eligible", "price_eur_ht", "title"],
                ascending=[False, False, False, True]
            ).head(top_n)
            actual_n = len(subset)
            if actual_n == 1:
                row = subset.iloc[0]
                response = f"\U0001F3C6 La formation la plus complete{scope_label} est **{row['title']}** &mdash; {fmt_duration(row)} &middot; {fmt_price(row['price_eur_ht'])}."
                remember_recommendation(context, row['title'])
            else:
                listing = format_formation_list(subset, max_items=top_n)
                response = f"\U0001F3C6 **Top {actual_n} des formations{scope_label}** :\n\n{listing}"

    if intent == "search_by_format":
        if requested_format:
            subset = filter_by_format(dataframe, requested_format)
            if subset.empty:
                response = f"Aucune formation en {requested_format}."
            else:
                listing = format_formation_list(subset, max_items=10)
                response = f"**{len(subset)} formation(s) en {requested_format}** :\n\n{listing}"
        else:
            response = "Quel format souhaites-tu ? (Presentiel, Distanciel, Hybride)"

    if intent == "search_by_duration":
        if duration_filter:
            subset = duration_filter(dataframe)
            if subset.empty:
                response = "Aucune formation ne correspond a cette duree."
            else:
                listing = format_formation_list(subset, max_items=10)
                response = f"**{len(subset)} formation(s)** :\n\n{listing}"
        else:
            response = "Precise la duree : 'formation courte', 'moins de 2 jours', 'plus de 3 jours', etc."

    if intent == "search_by_audience":
        if audience_filter:
            subset = audience_filter(dataframe)
            if subset.empty:
                response = "Aucune formation pour ce public."
            else:
                listing = format_formation_list(subset, max_items=10)
                response = f"**{len(subset)} formation(s) pour ce public** :\n\n{listing}"
        else:
            response = "Precise le public : 'pour dirigeant', 'pour manager', etc."

    if intent == "search_by_certification":
        if cert_filter:
            subset = cert_filter(dataframe)
            if isinstance(subset, pd.DataFrame) and not subset.empty:
                listing = format_formation_list(subset, max_items=10)
                response = f"**{len(subset)} formation(s) {cert_label}** :\n\n{listing}"
            else:
                response = f"Aucune formation {cert_label or 'avec cette certification'}."
        else:
            response = "Precise la certification : 'eligible CPF', 'Qualiopi', 'RNCP', etc."

    context["last_intent"] = intent
    return response, conf_data, lang, context


# -----------------------------------------------------------------------------
# 7. Initialisation session_state
# -----------------------------------------------------------------------------
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
if "context" not in st.session_state:
    st.session_state.context = fresh_context()
else:
    st.session_state.context.setdefault("recently_recommended", [])
if "current_conv_id" not in st.session_state:
    start_new_conversation()


# -----------------------------------------------------------------------------
# 8. Interface Streamlit
# -----------------------------------------------------------------------------
if df is None:
    st.error(f"Le fichier '{DATASET_FILE}' est manquant. Place ton catalogue de formations dans ce dossier.")
elif clf is None:
    st.error(f"Le fichier '{TRAINING_CORPUS_FILE}' est manquant. Impossible d'entrainer le classifieur.")
else:
    with st.sidebar:
        st.header("ADN Potentiel")
        st.caption(
            "**Cabinet de formation, conseil et coaching** "
            "specialise dans l'accompagnement des dirigeants de TPE du secteur BTP. "
            "Base a Lille, intervient en France et en Belgique."
        )
        st.caption("🏅 Certifie **Qualiopi** &middot; Reference OPCO **Constructys**")
        st.caption("📞 [06 61 15 80 04](tel:+33661158004) &middot; ✉️ contact@adnpotentiel.com")
        st.markdown("---")
        st.header("Historique")
        if st.button("Nouvelle conversation", use_container_width=True,
                     help="Demarre une nouvelle conversation vierge avec FormaBot. L'ancienne reste accessible dans la liste ci-dessous."):
            upsert_current_conversation()
            start_new_conversation()
            st.rerun()

        data = load_conversations()
        conversations = data.get("conversations", [])

        if not conversations:
            st.caption("Aucune conversation enregistree.")
        else:
            st.caption(f"{len(conversations)} conversation(s) enregistree(s)")
            for conv in conversations[:15]:
                is_current = conv["id"] == st.session_state.current_conv_id
                label_prefix = "(actif) " if is_current else ""
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.button(
                        f"{label_prefix}{conv['title']}",
                        key=f"load_{conv['id']}",
                        use_container_width=True,
                        disabled=is_current,
                        help=f"Recharger la conversation '{conv['title']}' dans la fenetre de chat",
                    ):
                        upsert_current_conversation()
                        load_conversation_into_session(conv["id"])
                        st.rerun()
                with col_b:
                    if st.button("X", key=f"del_{conv['id']}", help="Supprimer"):
                        delete_conversation(conv["id"])
                        st.rerun()

        # RGPD art. 20 (portabilite)
        if conversations:
            upsert_current_conversation()
            export_payload = load_conversations()
            export_bytes = json.dumps(export_payload, ensure_ascii=False, indent=2).encode("utf-8")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button(
                label="📥 Exporter mes conversations (JSON)",
                data=export_bytes,
                file_name=f"formabot_conversations_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
                help="RGPD article 20 : portabilite de vos donnees.",
            )

        # === RGPD article 17 - droit a l'effacement ===
        # Confirmation a 2 etapes via session_state pour eviter une suppression
        # accidentelle d'un simple clic.
        if conversations:
            confirm_key = "_delete_all_confirm"
            if not st.session_state.get(confirm_key):
                if st.button(
                    "🗑️ Supprimer toutes mes conversations",
                    use_container_width=True,
                    help="RGPD article 17 : droit a l'oubli. Action irreversible.",
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning("⚠️ Toutes vos conversations vont etre supprimees definitivement. Confirmer ?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Oui, supprimer", use_container_width=True, type="primary",
                                 help="Confirme la suppression definitive de toutes vos conversations (RGPD article 17)"):
                        # Purge effective du fichier d'historique
                        try:
                            if os.path.exists(HISTORY_FILE):
                                os.remove(HISTORY_FILE)
                        except OSError as e:
                            st.error(f"Erreur lors de la suppression : {e}")
                        # Reset complet de la session conversationnelle
                        st.session_state[confirm_key] = False
                        if "current_conv_id" in st.session_state:
                            del st.session_state["current_conv_id"]
                        if "messages" in st.session_state:
                            del st.session_state["messages"]
                        if "context" in st.session_state:
                            del st.session_state["context"]
                        start_new_conversation()
                        st.success("Toutes vos conversations ont ete supprimees.")
                        st.rerun()
                with col_no:
                    if st.button("Annuler", use_container_width=True,
                                 help="Annule la demande de suppression. Vos conversations restent intactes."):
                        st.session_state[confirm_key] = False
                        st.rerun()

        st.markdown("---")
        st.header("Catalogue")
        st.subheader("Formation phare")
        flagship = df.sort_values(
            by=["qualiopi_certified", "price_eur_ht"], ascending=[False, False]
        ).iloc[0]
        st.markdown(f"**{flagship['title']}**")
        st.caption(f"{flagship['theme']} | {fmt_duration(flagship)} | {fmt_price(flagship['price_eur_ht'])}")
        with st.expander("Voir le descriptif"):
            desc = str(flagship['description'])
            st.write(desc[:400] + ("..." if len(desc) > 400 else ""))

        st.markdown("---")
        st.subheader("Decouverte aleatoire")
        if st.button("Surprends-moi !",
                     help="Affiche une formation au hasard du catalogue ADN Potentiel"):
            st.session_state["random_formation"] = df.sample(1).iloc[0]
        if "random_formation" in st.session_state:
            rf = st.session_state["random_formation"]
            st.markdown(f"**{rf['title']}**")
            st.caption(f"{rf['theme']} | {fmt_duration(rf)} | {fmt_price(rf['price_eur_ht'])}")

    st.title("\U0001F393 FormaBot - Assistant ADN Potentiel")

    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chatbot",
        "📊 Exploration Catalogue",
        "⚙️ Performance Modele",
        "📋 Model Card",
    ])

    with tab1:
        st.header("Discute avec FormaBot")
        st.caption(f"Catalogue : **{len(df)} formations** | **{len(AVAILABLE_THEMES)} themes** | **{len(AVAILABLE_FORMATS)} formats**")

        st.info(
            "**Vous discutez avec un assistant automatise.** "
            "FormaBot est un chatbot construit pour ADN Potentiel afin d'aider les dirigeants de TPE BTP "
            "a identifier la formation, le coaching ou l'accompagnement adapte a leur besoin parmi notre catalogue. "
            "Il s'appuie sur un classifieur d'intentions entraine sur ~220 phrases. "
            "Il peut se tromper et **ne stocke aucune donnee personnelle** : vos conversations restent uniquement sur votre machine. "
            "Conformement a l'AI Act 2024 (article 50) et au RGPD (articles 17, 20, 22).",
            icon="ℹ️",
        )

        ctx = st.session_state.context
        if ctx.get("last_title") or ctx.get("last_intent"):
            cols_mem = st.columns(2)
            cols_mem[0].caption(f"Derniere formation : **{ctx.get('last_title') or '-'}**")
            cols_mem[1].caption(f"Derniere intention : **{ctx.get('last_intent') or '-'}**")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Votre question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Analyse..."):
                resp, conf_data, lang, new_ctx = get_bot_response(
                    prompt, df, clf,
                    context=st.session_state.context,
                    system_prompt=st.session_state.system_prompt,
                    available_themes=AVAILABLE_THEMES,
                    available_formats=AVAILABLE_FORMATS,
                )
                st.session_state.context = new_ctx
            st.session_state.messages.append({"role": "assistant", "content": resp})
            with st.chat_message("assistant"):
                st.markdown(resp)
                if conf_data is not None:
                    with st.expander("Voir la confiance du modele"):
                        lang_display = {"fr": "Francais", "en": "Anglais",
                                        "es": "Espagnol", "de": "Allemand",
                                        "unknown": "Indeterminee"}.get(lang, lang)
                        if not LANGDETECT_AVAILABLE:
                            st.caption("langdetect non installe - detection desactivee. pip install langdetect")
                        else:
                            st.caption(f"Langue detectee : **{lang_display}**")
                        fig_conf = px.bar(
                            conf_data, x="Confiance", y="Intention",
                            orientation='h', text_auto='.1%',
                            title="Probabilite par intention",
                            color="Confiance", color_continuous_scale="Blues"
                        )
                        fig_conf.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
                        st.plotly_chart(fig_conf, use_container_width=True)
                        top = conf_data.iloc[0]
                        st.caption(
                            f"Intention detectee : **{top['Intention']}** avec **{top['Confiance']*100:.1f}%** de certitude."
                        )
            upsert_current_conversation()

    with tab2:
        st.header("Exploration du catalogue ADN Potentiel")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total formations", len(df))
        col2.metric("Themes distincts", len(AVAILABLE_THEMES))
        col3.metric("Eligibles CPF", int(df["cpf_eligible"].sum()))
        col4.metric("Certifiees Qualiopi", int(df["qualiopi_certified"].sum()))

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            theme_counts = df["theme"].value_counts().reset_index()
            theme_counts.columns = ["Theme", "Nombre"]
            fig_theme = px.pie(theme_counts, values="Nombre", names="Theme",
                               title="Repartition par theme", hole=0.4)
            st.plotly_chart(fig_theme, use_container_width=True)
        with col_g2:
            format_counts = df["format"].value_counts().reset_index()
            format_counts.columns = ["Format", "Nombre"]
            fig_format = px.bar(format_counts, x="Format", y="Nombre",
                                title="Formations par format", color="Nombre",
                                color_continuous_scale="Blues")
            st.plotly_chart(fig_format, use_container_width=True)

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            fig_d = px.histogram(df, x="duration_hours", nbins=10,
                                  title="Distribution des durees (h)")
            st.plotly_chart(fig_d, use_container_width=True)
        with col_h2:
            fig_p = px.histogram(df, x="price_eur_ht", nbins=10,
                                  title="Distribution des prix (EUR HT)")
            st.plotly_chart(fig_p, use_container_width=True)

        st.markdown("---")
        st.subheader("Catalogue complet")
        display_cols = ["title", "theme", "subtheme", "format", "duration_label",
                        "price_eur_ht", "cpf_eligible", "qualiopi_certified"]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)

    with tab3:
        st.header("Performance du classifieur d'intentions (SVM)")
        st.info(
            f"Modele : SVM + TF-IDF entraine sur {len(train_df)} phrases reparties sur "
            f"{train_df['intent'].nunique()} intentions. Voir evaluation/ pour l'evaluation sur test set independant."
        )
        y_true = train_df["intent"]
        y_pred = clf.predict(train_df["text_norm"])
        labels = sorted(list(set(y_true)))
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            st.subheader("Matrice de Confusion (training set)")
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            fig_cm = px.imshow(
                cm, text_auto=True,
                labels=dict(x="Prediction", y="Vraie Intention", color="Nombre"),
                x=labels, y=labels, color_continuous_scale="Blues"
            )
            fig_cm.update_layout(height=600)
            st.plotly_chart(fig_cm, use_container_width=True)
        with col_p2:
            st.subheader("Rapport de Classification")
            report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            report_df = pd.DataFrame(report).transpose()
            st.dataframe(report_df.style.highlight_max(axis=0), use_container_width=True)
        st.markdown("---")
        st.subheader("Distribution du corpus d'entrainement")
        intent_counts = train_df["intent"].value_counts().reset_index()
        intent_counts.columns = ["Intention", "Nombre d'exemples"]
        fig_intent = px.bar(intent_counts, x="Intention", y="Nombre d'exemples",
                            title="Repartition par intention", color="Nombre d'exemples",
                            color_continuous_scale="Greens")
        st.plotly_chart(fig_intent, use_container_width=True)

    # ===== TAB 4 : MODEL CARD =====
    with tab4:
        st.header("📋 Model Card — FormaBot")
        st.caption(
            "Cette fiche decrit le modele d'intelligence artificielle utilise par FormaBot. "
            "Format inspire de Mitchell et al. (2019) *Model Cards for Model Reporting* et conforme aux exigences "
            "de l'AI Act 2024 (article 13 — transparence et fourniture d'information aux utilisateurs)."
        )

        # --- Synthese rapide ---
        st.subheader("Synthese")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Type de modele", "SVM + TF-IDF")
        col_m2.metric("Intentions", train_df["intent"].nunique())
        col_m3.metric("Phrases d'entrainement", len(train_df))
        col_m4.metric("Catalogue", f"{len(df)} formations")

        st.markdown("---")

        # --- 1. Details du modele ---
        st.subheader("1. Details du modele")
        st.markdown(f"""
- **Architecture** : pipeline scikit-learn `TfidfVectorizer(ngram_range=(1,2))` puis `CalibratedClassifierCV(LinearSVC, cv=2)`
- **Backend fuzzy matching** : `{_FUZZ_BACKEND}` pour la recherche de titres de formations
- **Pre-traitement** : suppression des accents, mise en minuscule, correction orthographique sur 16 mots-cles metier (formation, management, leadership, coaching, etc.) via distance Levenshtein
- **Detection de langue** : `langdetect` ({'actif' if LANGDETECT_AVAILABLE else 'non installe'})
- **Architecture hybride symbolique + ML** : 3 overrides regle-bases en complement du classifieur statistique :
    1. Override `top N` : regex `\\btop\\s*\\d+\\b` force l'intention `list_top`
    2. Override `titre detecte` : si un titre canonique est extrait avec confiance suffisante ET qu'au moins un mot significatif est present, force `ask_info`
    3. Override `multi-criteres` : si confiance < 50% et qu'un theme est detecte avec un intent search_*, bascule vers `recommend_by_theme`
- **Auteur** : Glenn Mboga (M2 Nexa Digital School — RNCP 37137)
- **Cabinet metier** : ADN Potentiel — formation, conseil et coaching pour dirigeants TPE BTP
- **Date du modele** : entraine a chaud au demarrage de l'application (le modele n'est pas serialise)
        """)

        st.markdown("---")

        # --- 2. Cas d'usage prevus ---
        st.subheader("2. Cas d'usage prevus")
        st.markdown("""
**Usages couverts** : aider un dirigeant de TPE BTP a explorer et choisir une formation ADN Potentiel
adaptee a son besoin via une interface conversationnelle. Le bot peut :
- recommander une formation (au hasard ou par theme metier)
- lister tout ou partie du catalogue (par theme, format, duree, public, certification)
- afficher le top N des formations selon des criteres
- donner les details d'une formation precise (prix, duree, format, objectifs, prerequis)
- lister les themes et formats disponibles

**Usages NON couverts (hors perimetre)** :
- prise de commande / inscription a une formation (renvoi vers le contact ADN Potentiel)
- conseil personnalise au-dela de la recommandation de formation
- traitement de donnees personnelles (RH, sante, etc.)
- usage par des mineurs (le service vise un public dirigeant professionnel)
        """)

        st.markdown("---")

        # --- 3. Donnees d'entrainement ---
        st.subheader("3. Donnees d'entrainement")
        st.markdown(f"""
- **Corpus** : {len(train_df)} phrases types reparties sur {train_df['intent'].nunique()} intentions, fichier `formations_training_corpus.csv`
- **Langues** : francais (~80%) + anglais (~20%)
- **Constitution** : redige manuellement par l'auteur, sans collecte de donnees utilisateur reelles
- **Catalogue formations** : {len(df)} entrees issues du catalogue officiel ADN Potentiel V15 (24 juin 2025), fichier `formations_adn.csv`
- **Themes couverts** : {', '.join(AVAILABLE_THEMES)}
        """)
        st.caption("Distribution detaillee des intentions :")
        dist_df = train_df["intent"].value_counts().reset_index()
        dist_df.columns = ["Intention", "Nombre d'exemples"]
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # --- 4. Performances ---
        st.subheader("4. Performances")
        st.markdown("""
**Sur le training set** (indicatif, voir onglet *Performance Modele*) :
        """)
        from sklearn.metrics import accuracy_score, f1_score
        y_pred_card = clf.predict(train_df["text_norm"])
        acc = accuracy_score(train_df["intent"], y_pred_card)
        f1m = f1_score(train_df["intent"], y_pred_card, average="macro", zero_division=0)
        f1w = f1_score(train_df["intent"], y_pred_card, average="weighted", zero_division=0)
        c1, c2, c3 = st.columns(3)
        c1.metric("Accuracy (train)", f"{acc:.3f}")
        c2.metric("F1 macro (train)", f"{f1m:.3f}")
        c3.metric("F1 weighted (train)", f"{f1w:.3f}")
        st.info(
            "**Limite methodologique** : ces metriques sont calculees sur le training set et sont donc biaisees. "
            "Une evaluation rigoureuse sur jeu de test independant (91 phrases distinctes) est documentee dans "
            "`evaluation/EVALUATION_REPORT.md`. La latence p95 mesuree est de **~24 ms** sur CPU."
        )

        st.markdown("---")

        # --- 5. Limites connues ---
        st.subheader("5. Limites connues")
        st.markdown("""
- **Classes minoritaires** : `thanks`, `help`, `goodbye`, `fallback` ont moins d'exemples (< 12 chacune)
  ce qui les rend statistiquement moins robustes.
- **Phrases multi-criteres complexes** : sur 12 phrasings naturels longs avec sujet en milieu de phrase,
  le classifieur seul atteint 7/12 ; avec les overrides regle-bases, on monte a 10/12 (~83%).
- **Vocabulaire metier** : le modele ne reconnait que les mots-cles inclus dans le corpus
  d'entrainement. Une formation tres specifique avec un vocabulaire inattendu peut tomber en `fallback`.
- **Typos** : couverts pour 16 mots-cles metier via Levenshtein avec garde-fous, mais pas pour les noms
  propres ou les references techniques rares.
- **Multilinguisme** : limite a FR/EN. Une requete en espagnol, allemand ou italien sera mal classee.
- **Pas de contexte multi-tours profond** : le bot retient le dernier titre evoque et la derniere intention
  mais ne suit pas une logique conversationnelle sophistiquee sur plusieurs echanges.
- **Pas de garantie pedagogique** : le bot oriente vers une formation pertinente mais ne garantit pas
  l'atteinte d'un objectif de formation specifique (pour cela, contacter directement ADN Potentiel).
        """)

        st.markdown("---")

        # --- 6. Biais identifies ---
        st.subheader("6. Biais identifies")
        st.markdown("""
- **Biais sectoriel** : le catalogue est centre BTP TPE — les recommandations ne sont pas pertinentes
  pour d'autres secteurs.
- **Biais commercial potentiel** : le tri du `top N` privilegie les formations Qualiopi + CPF-eligibles
  + prix eleve. Cela peut favoriser les formations plus rentables pour le cabinet plutot que les plus
  adaptees au besoin du dirigeant. **Mitigation : tri transparent, code source ouvert, et indication
  explicite des criteres de tri dans la documentation.**
- **Biais geographique** : ADN Potentiel intervient principalement en France et Belgique. Les
  formations en presentiel impliquent un deplacement de formateur.
- **Sous-representation des publics** : le corpus d'entrainement contient majoritairement des phrases
- **Sous-representation des publics** : le corpus d'entrainement contient majoritairement des phrases
  formulees par un public francais ayant des bases de francais ecrit standard. Les requetes tres
  argotiques ou avec une grammaire non-standard peuvent etre mal classees.
        """)

        st.markdown("---")

        st.subheader("7. Mesures ethiques et conformite")
        st.markdown(f"""
- **AI Act (Reglement UE 2024/1689) art. 50** : disclosure obligatoire affichee en haut du chatbot.
- **RGPD art. 17** : bouton "Supprimer toutes mes conversations" dans la sidebar.
- **RGPD art. 20** : bouton "Exporter mes conversations (JSON)" pour portabilite.
- **RGPD art. 22** : pas de decision automatisee individuelle a effet juridique.
- **Stockage local exclusif** : conversations stockees dans un JSON sur la machine, jamais envoyees a un serveur tiers.
- **Pas de telemetrie, pas de tracking** : aucun cookie, aucune analytics.
- **Anti-repetition** : le bot evite de recommander la meme formation deux fois de suite.
        """)

        st.markdown("---")

        # === Section accessibilite WCAG 2.1 AA ===
        st.subheader("8. Accessibilite (RGAA / WCAG 2.1 AA)")
        st.markdown("""
**Engagement** : FormaBot vise la conformite au niveau **WCAG 2.1 AA** (equivalent RGAA 4.1 en France),
conformement a l'exigence du guide Nexa (section 6.6).

**Mesures en place** :

- **Perceptible** :
  - Contraste de couleurs : theme Streamlit par defaut, ratio >= 4.5:1 sur le texte (verifie sur https://webaim.org/resources/contrastchecker).
  - Pas de dependance a la couleur seule : tous les badges sont accompagnes de texte (ex : "CPF eligible" plutot qu'une simple pastille verte).
  - Police lisible : taille de texte par defaut Streamlit >= 14pt, redimensionnable par zoom navigateur.
  - Pas de contenu clignotant ou en mouvement rapide.

- **Utilisable** :
  - Navigation au clavier integrale : Tab/Shift+Tab pour les controles, Enter pour activer, Espace pour les boutons. Garanti par les composants natifs Streamlit.
  - Pas de piege au clavier (verifie : sortie possible de tous les composants).
  - Aide explicite sur chaque bouton via le parametre `help=` (tooltip au survol ET annonce aux lecteurs d'ecran).
  - Suffisamment de temps : aucune limite de temps imposee a l'utilisateur.

- **Comprehensible** :
  - Langue declaree dans l'en-tete HTML (par defaut FR via la page_config).
  - Libelles explicites sur chaque action ("Supprimer toutes mes conversations" plutot que "Suppression").
  - Confirmation a deux etapes pour les actions destructrices (suppression).
  - Messages d'erreur clairs et actionables (ex : "Le fichier formations_adn.csv est manquant").

- **Robuste** :
  - HTML semantique genere par Streamlit (h1, h2, h3, button, label).
  - Compatible navigateurs modernes (Chrome, Firefox, Edge, Safari).

**Limites assumees** :

- **Streamlit ne permet pas** de personnaliser finement les `aria-label` ou d'ajouter des `skip links`.
  Le passage en composants custom (React) serait necessaire pour atteindre une conformite RGAA stricte.
- **Pas d'alternative audio/braille** : le service est uniquement textuel.
- **Pas de mode haut contraste personnalise** : on s'appuie sur le mode sombre/clair natif Streamlit.

**Perspective** : une etape "audit RGAA officiel par un consultant certifie" est prevue dans le plan d'evolution post-soutenance.
        """)

        st.markdown("---")

        st.subheader("9. Contact et responsabilite")
        st.markdown("""
**Pour toute question sur ce modele** :
- Auteur du modele : Glenn Mboga (memoire M2 Nexa Digital School)
- Cabinet metier : ADN Potentiel
  - 06 61 15 80 04
  - contact@adnpotentiel.com
  - 34 Place du general de Gaulle, Bureau 3, 59000 Lille

**Version de la fiche** : 1.1 - 30 mai 2026 (ajout section accessibilite)
        """)
