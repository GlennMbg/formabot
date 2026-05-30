"""Genere 'feuille de route.pdf' v4 : pivot vers FormaBot (ADN Potentiel).

Usage :
    pip install reportlab
    python generate_roadmap.py
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
)
from datetime import date

OUTPUT = str(Path(__file__).parent / "feuille de route.pdf")

ACCENT = HexColor("#2E5BBA")
ACCENT_LIGHT = HexColor("#E8F0FE")
TEXT = HexColor("#222222")
MUTED = HexColor("#666666")
HIGH = HexColor("#C0392B")
MED = HexColor("#D68910")
LOW = HexColor("#27AE60")
CODE_COLOR = HexColor("#1D6F42")
WRITE_COLOR = HexColor("#8B4513")
PIVOT_COLOR = HexColor("#7D3C98")

styles = getSampleStyleSheet()

style_title = ParagraphStyle("T", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=22, textColor=ACCENT, spaceAfter=4, alignment=TA_LEFT)
style_subtitle = ParagraphStyle("ST", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=10.5, textColor=MUTED, spaceAfter=14)
style_h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=14, textColor=ACCENT, spaceBefore=12, spaceAfter=6, leading=17)
style_h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=11, textColor=TEXT, spaceBefore=8, spaceAfter=3, leading=14)
style_body = ParagraphStyle("B", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=10, textColor=TEXT, alignment=TA_JUSTIFY, leading=13, spaceAfter=5)
style_bullet = ParagraphStyle("Bul", parent=style_body, leftIndent=14, spaceAfter=2)
style_callout = ParagraphStyle("C", parent=style_body, leftIndent=10, rightIndent=10,
    spaceBefore=4, spaceAfter=6, fontSize=9.5)


def bullets(items):
    return [Paragraph(f"&bull;&nbsp;&nbsp;{t}", style_bullet) for t in items]


def day_block(num, day_label, title, eff, ctype, is_done=False, is_pivot=False):
    color = CODE_COLOR if ctype == "code" else WRITE_COLOR
    type_label = "CODE" if ctype == "code" else "REDACTION"
    badges = []
    if is_done:
        badges.append("<font color='#27AE60'><b>[FAIT]</b></font> ")
    if is_pivot:
        badges.append(f"<font color='{PIVOT_COLOR.hexval()}'><b>[PIVOT]</b></font> ")
    badge_str = "".join(badges)
    data = [[
        Paragraph(f"<font color='{color.hexval()}'><b>J{num} &middot; {day_label}</b></font>", style_body),
        Paragraph(f"{badge_str}<b>{title}</b>", style_body),
        Paragraph(f"<font color='{color.hexval()}'><b>{type_label}</b></font>", style_body),
        Paragraph(f"~{eff}", style_body),
    ]]
    t = Table(data, colWidths=[3.4*cm, 8.5*cm, 2.0*cm, 1.6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=1.8*cm, rightMargin=1.8*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    title="Feuille de route v4 - pivot FormaBot",
    author="Glenn Mboga",
)

story = []

story.append(Paragraph("Feuille de route", style_title))
story.append(Paragraph(
    f"v4 &mdash; Pivot vers FormaBot (ADN Potentiel) &middot; mis &agrave; jour le {date.today().strftime('%d %B %Y')}",
    style_subtitle,
))

story.append(Paragraph(
    "<b>Projet</b> : FormaBot &mdash; assistant conversationnel de recommandation de formations pour "
    "les dirigeants TPE BTP, d&eacute;velopp&eacute; pour <b>ADN Potentiel</b> (cabinet de formation, "
    "conseil et coaching). Probl&eacute;matique inchang&eacute;e (NLP robuste, multilingue, conforme).",
    style_callout,
))

# Synthese
story.append(Paragraph("Synth&egrave;se du nouveau plan", style_h1))
story.append(Paragraph(
    "Pivot d&eacute;cid&eacute; le 29 mai : passage du domaine anime au domaine formation/coaching BTP TPE. "
    "L'architecture technique reste identique (SVM + TF-IDF + fuzzy + conformit&eacute;). Le travail d&eacute;j&agrave; "
    "fait sur la conformit&eacute; (J1) est r&eacute;utilisable tel quel. Le surco&ucirc;t pivot (~4.5 jours) est absorb&eacute; "
    "en compressant les sprints non-critiques.",
    style_body,
))

date_data = [
    ["Date", "Echeance"],
    ["Dim. 15 juin",  "V1 du PDF + ZIP livrables &mdash; objectif interne (avant soutenance blanche)"],
    ["Fin juin",      "Soutenance blanche (date exacte &agrave; confirmer)"],
    ["Mar. 1er juillet 23h59", "Remise officielle via Teams"],
]
d_rows = [[Paragraph(c, style_body) for c in r] for r in date_data]
d_table = Table(d_rows, colWidths=[4.0*cm, 12.0*cm])
d_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
    ("TEXTCOLOR", (0, 0), (-1, 0), white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 0.4, MUTED),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ACCENT_LIGHT]),
]))
story.append(d_table)

# Etat actuel apres pivot
story.append(Paragraph("Point apr&egrave;s d&eacute;cision de pivot (29 mai)", style_h1))
story.extend(bullets([
    "<b>Architecture technique</b> : 100% r&eacute;utilisable (SVM + TF-IDF + fuzzy + m&eacute;moire + conformit&eacute;).",
    "<b>J1 d&eacute;j&agrave; livr&eacute;</b> : disclosure bot + export RGPD (texte &agrave; reformuler pour FormaBot, structure inchang&eacute;e).",
    "<b>Corpus pr&ecirc;t</b> : 223 phrases d'entrainement sur 19 intentions formation (formations_training_corpus.csv).",
    "<b>Test set pr&ecirc;t</b> : 91 phrases ind&eacute;pendantes (evaluation/test_set_formations.csv).",
    "<b>Squelette m&eacute;moire</b> ajust&eacute; pour ADN Potentiel et march&eacute; formation BTP TPE.",
    "<b>En attente</b> : ton export CSV du catalogue ADN Potentiel pour basculer l'app.",
]))

story.append(PageBreak())

# === Phase 1 : Code (29 mai -> 8 juin, 11 jours) ===
story.append(Paragraph("Phase 1 &mdash; Code et livrables techniques (J1 &agrave; J11)", style_h1))

story.append(day_block(1, "Ven. 29 mai", "Conformite 1/2 : disclosure bot + export RGPD", "3-4h", "code", is_done=True))
story.append(day_block(2, "Sam. 30 mai", "Conformite 2/2 : delete all + page Model Card", "4-5h", "code"))
story.append(Paragraph(
    "Plus une mise &agrave; jour du texte du bandeau disclosure pour mentionner FormaBot et ADN Potentiel au lieu d'AnimeBot.",
    style_body,
))

story.append(day_block(3, "Dim. 31 mai", "Migration SQLite + integration vrai catalogue ADN", "5-6h", "code", is_pivot=True))
story.append(Paragraph(
    "Fichier de travail : <code>app_formabot.py</code> (le projet AniReco <code>app.py</code> reste intact). "
    "D&egrave;s reception de ton vrai <code>formations_adn.csv</code> : (1) remplacement du placeholder de 17 lignes, "
    "(2) cr&eacute;ation du schema SQL <code>formations</code> avec indexes, "
    "(3) g&eacute;n&eacute;ration du dump <code>formabot.sql</code>, "
    "(4) adaptation de <code>load_resources()</code> pour charger depuis SQLite plut&ocirc;t que CSV.",
    style_body,
))

story.append(day_block(4, "Lun. 1er juin", "Test & tuning du classifieur sur le vrai catalogue", "4-5h", "code", is_pivot=True))
story.append(Paragraph(
    "Note : la structure d'<code>app_formabot.py</code> est d&eacute;j&agrave; pr&ecirc;te (load depuis "
    "<code>formations_training_corpus.csv</code>, 19 intentions impl&eacute;ment&eacute;es : recommend_by_theme, "
    "list_by_theme, search_by_format/duration/audience/certification, ask_info/price/duration/format/objectives, etc.). "
    "Ce jour : enrichir le corpus d'entrainement si certains intents ont une confiance faible sur les vraies requ&ecirc;tes, "
    "ajuster les overrides regex, tester avec des dirigeants TPE BTP si possible.",
    style_body,
))

story.append(day_block(5, "Mar. 2 juin", "Robustesse au bruit + nouvelle evaluation comparative", "4h", "code"))
story.append(Paragraph(
    "G&eacute;n&eacute;rateur de variantes bruit&eacute;es du test set formation. "
    "Run complet : 4 baselines sklearn sur le nouveau corpus + matrice de confusion + plot F1/latence. "
    "Mise a jour du rapport d'evaluation.",
    style_body,
))

story.append(day_block(6, "Mer. 3 juin", "Accessibilite RGAA / WCAG 2.1 AA", "3-4h", "code"))
story.append(day_block(7, "Jeu. 4 juin", "DistilBERT en local + integration au rapport", "2-3h", "code"))

story.append(day_block(8, "Ven. 5 juin", "Deploiement Streamlit Cloud + URL publique", "3-4h", "code"))
story.append(Paragraph(
    "D&eacute;p&ocirc;t GitHub public, lien Streamlit Cloud, secrets, v&eacute;rification de l'URL publique. "
    "<b>Bloquant</b> &mdash; exig&eacute; par le guide.",
    style_body,
))

story.append(day_block(9, "Sam. 6 juin", "README/PDR + tableau probleamtiques + freeze code", "3-4h", "code"))
story.append(day_block(10, "Dim. 7 juin", "Buffer technique + ajustements finaux", "0-4h", "code"))
story.append(day_block(11, "Lun. 8 juin", "Buffer / debut redaction si avance", "0-4h", "code"))

story.append(PageBreak())

# === Phase 2 : Redaction V1 (9-15 juin, 7 jours) ===
story.append(Paragraph("Phase 2 &mdash; R&eacute;daction V1 du m&eacute;moire (J12 &agrave; J18)", style_h1))
story.append(Paragraph(
    "Cible : <b>50 pages</b> hors annexes. Structure d&eacute;taill&eacute;e dans <i>squelette_memoire.md</i> (mis &agrave; jour pour ADN Potentiel). "
    "Format : Times New Roman 12 / Arial 11 / Calibri 12, marges 2.5 cm, interligne 1.5 max, pages num&eacute;rot&eacute;es. "
    "Fichier final : <code>MBOGA_GLENN_THESE.pdf</code>.",
    style_body,
))

story.append(day_block(12, "Mar. 9 juin", "Page presentation + Descriptif ADN Potentiel (entreprise reelle)", "~5 pages", "redaction", is_pivot=True))
story.append(Paragraph(
    "Storytelling ADN, valeurs, missions, environnement &eacute;co/techno/donn&eacute;es. <b>Avantage du pivot</b> : "
    "tout est r&eacute;el, plus de cadre fictif &agrave; justifier.",
    style_body,
))

story.append(day_block(13, "Mer. 10 juin", "Etude marche + concurrents (CCCA-BTP, CAPEB, Bpifrance)", "~6 pages", "redaction", is_pivot=True))
story.append(Paragraph(
    "Sources INSEE / Centre Inffo / FFB pour les chiffres marche formation BTP TPE. "
    "3 concurrents minimum, m&ecirc;me trame pour chacun (PAS en tableau).",
    style_body,
))

story.append(day_block(14, "Jeu. 11 juin", "Problematique + Gestion de projet (Gantt, budget, veille, risques, charte)", "~12 pages", "redaction"))
story.append(day_block(15, "Ven. 12 juin", "Exploitation des donnees (sources, dictionnaire, manipulation, ML)", "~13 pages", "redaction"))
story.append(day_block(16, "Sam. 13 juin", "Developpement app + conformite + accessibilite", "~9 pages", "redaction"))
story.append(day_block(17, "Dim. 14 juin", "Conclusion + abstract + biblio + table matieres + mise en page", "~5 pages", "redaction"))
story.append(day_block(18, "Lun. 15 juin", "Generation PDF V1 + assemblage ZIP &mdash; livrable soutenance blanche", "&mdash;", "redaction"))

# === Phase 3 : Polish + prepa soutenance ===
story.append(Paragraph("Phase 3 &mdash; Polish + pr&eacute;pa soutenance blanche (16 &agrave; 28 juin)", style_h1))
story.extend(bullets([
    "<b>Support de pr&eacute;sentation</b> <code>MBOGA_GLENN_PREZ.pdf</code> &mdash; 30 min, ~25-30 diapos.",
    "<b>R&eacute;p&eacute;tition orale chronom&eacute;tr&eacute;e</b> &mdash; viser 28 min pour marge.",
    "<b>Pr&eacute;paration jeu de r&ocirc;le 30 min</b> &mdash; sc&eacute;narios client, questions/objections sur le contexte ADN/BTP.",
    "<b>Soutenance blanche</b> &mdash; prendre les retours du jury.",
    "<b>Ajustements m&eacute;moire</b> selon retours.",
    "<b>Compl&eacute;tion bibliographie</b> (cible 25-30 r&eacute;f&eacute;rences).",
]))

# === Phase 4 : Remise ===
story.append(Paragraph("Phase 4 &mdash; Finalisation et remise (29 juin au 1er juillet)", style_h1))
story.extend(bullets([
    "Corrections finales suite soutenance blanche.",
    "G&eacute;n&eacute;ration finale PDF + ZIP.",
    "V&eacute;rification compatibilit&eacute; multi-navigateurs.",
    "Remise sur Teams le <b>1er juillet avant 23h59</b>.",
]))

# === Coupes ===
story.append(Paragraph("Ce qui reste coupe", style_h1))
story.extend(bullets([
    "<b>Recherche s&eacute;mantique</b> (sentence-transformers sur descriptions de formations) &mdash; perspective dans la conclusion.",
    "<b>Docker</b> &mdash; Streamlit Cloud suffit.",
    "<b>Tableau de bord d'usage</b> &mdash; perspective.",
    "<b>Multi-langue au-del&agrave; FR/EN</b> &mdash; perspective.",
    "<b>Int&eacute;gration CRM ADN Potentiel</b> &mdash; perspective d'industrialisation post-soutenance.",
]))

# === En attente de ta part ===
story.append(Paragraph("En attente de ta part (URGENT pour J3)", style_h1))
story.extend(bullets([
    "<b>Export CSV du catalogue ADN Potentiel</b> &mdash; fichier <code>formations_adn.csv</code> dans le dossier memoire, avec les colonnes d&eacute;finies dans le schema partage en chat.",
    "Sans ce fichier le J3 ne peut pas d&eacute;marrer &mdash; pr&eacute;voir donc de le produire d'ici samedi 30 mai au plus tard.",
    "Si certaines colonnes sont indisponibles, indique-le explicitement &mdash; on adaptera (placeholder, ou retrait de l'attribut concern&eacute;).",
]))

doc.build(story)
print(f"PDF genere : {OUTPUT}")
