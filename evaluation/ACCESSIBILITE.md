# Rapport d'accessibilité — FormaBot

*Mémoire M2 Nexa RNCP 37137 — sprint 6 de la roadmap — Glenn Mboga*

> **Objectif** : matière prête pour la section 6.6 « Accessibilité aux personnes en situation de handicap » du mémoire (exigence guide Nexa). Couvre les 4 principes du référentiel WCAG 2.1 AA / RGAA 4.1.

## 1. Cadre réglementaire et choix du niveau de conformité

- **WCAG 2.1 niveau AA** (World Wide Web Consortium, 2018) : standard international de l'accessibilité numérique. Le niveau AA est celui exigé en France pour les services publics et fortement recommandé pour les services privés s'adressant au grand public.
- **RGAA 4.1** (Référentiel Général d'Amélioration de l'Accessibilité, version 4.1, DINUM 2021) : transposition française de WCAG, applicable obligatoirement aux services publics en France et à tout service privé > 250 employés depuis la loi du 11 février 2005, renforcée par la loi du 7 octobre 2016 et le décret 2019-768.

FormaBot vise le niveau **WCAG 2.1 AA** (équivalent RGAA 4.1), en cohérence avec une diffusion auprès de dirigeants de TPE BTP susceptibles d'inclure des personnes en situation de handicap (vision, motricité, cognition).

## 2. Mesures implémentées par principe WCAG

### 2.1 Perceptible (l'information doit être présentable de plusieurs manières)

| Critère WCAG | État | Mesure dans FormaBot |
|---|---|---|
| 1.1.1 Contenu non textuel | ✅ | Aucune image porteuse d'information critique. Les éventuelles images décoratives ont un caption descriptif. |
| 1.3.1 Information et relations | ✅ | Structure HTML sémantique générée par Streamlit (h1, h2, h3, button, label). Sections explicites dans la sidebar (`st.header`). |
| 1.3.3 Caractéristiques sensorielles | ✅ | Les instructions ne dépendent pas d'une caractéristique sensorielle (position, forme, son). |
| 1.4.1 Utilisation de la couleur | ✅ | Aucune information transmise par la couleur seule. Badges textuels : `CPF eligible`, `Qualiopi`, etc. (pas de pastilles colorées sans texte). |
| 1.4.3 Contraste minimum | ✅ | Contraste vérifié sur thème Streamlit par défaut : ratio ≥ 4.5:1 sur le texte normal, ≥ 3:1 sur le grand texte. |
| 1.4.4 Redimensionnement | ✅ | Texte redimensionnable jusqu'à 200% via zoom navigateur sans perte de fonctionnalité. |
| 1.4.10 Reflow | ⚠️ Partiel | Layout Streamlit responsive jusqu'à ~600px, dégradation possible en dessous. |
| 1.4.11 Contraste des composants | ✅ | Contour focus visible sur tous les composants interactifs (natif Streamlit). |

### 2.2 Utilisable (les composants de l'interface doivent être utilisables)

| Critère WCAG | État | Mesure dans FormaBot |
|---|---|---|
| 2.1.1 Clavier | ✅ | Toute fonctionnalité accessible au clavier : Tab/Shift+Tab pour les contrôles, Enter pour activer un bouton ou envoyer un message, Espace pour les checkboxes. |
| 2.1.2 Pas de piège au clavier | ✅ | Vérifié manuellement : sortie possible de tous les composants (input chat, boutons sidebar, onglets, expanders). |
| 2.2.1 Réglage du délai | ✅ | Aucune limite de temps imposée à l'utilisateur. |
| 2.4.1 Contourner des blocs | ⚠️ Partiel | Pas de skip-link natif Streamlit. À documenter comme limite. |
| 2.4.2 Titre de page | ✅ | `page_title="FormaBot - ADN Potentiel"` défini dans `st.set_page_config`. |
| 2.4.3 Parcours du focus | ✅ | Ordre du focus logique : sidebar puis contenu principal puis onglets puis chat. |
| 2.4.4 Fonction du lien | ✅ | Chaque bouton porte un label explicite + un `help` tooltip qui décrit la conséquence de l'action. |
| 2.4.7 Visibilité du focus | ✅ | Halo de focus visible sur tous les composants interactifs (par défaut Streamlit). |
| 2.5.3 Étiquette dans le nom | ✅ | Le label visible correspond au nom accessible des composants. |

### 2.3 Compréhensible (l'information et l'utilisation doivent être compréhensibles)

| Critère WCAG | État | Mesure dans FormaBot |
|---|---|---|
| 3.1.1 Langue de la page | ✅ | Français par défaut. La page est en français et le bot répond également en anglais si l'utilisateur écrit en anglais (langdetect intégré). |
| 3.2.1 Au focus | ✅ | Aucun changement de contexte automatique au focus. |
| 3.2.2 À la saisie | ✅ | Aucun changement de contexte automatique à la saisie. |
| 3.3.1 Identification des erreurs | ✅ | Messages d'erreur clairs : `Le fichier formations_adn.csv est manquant. Place ton catalogue dans ce dossier.` |
| 3.3.2 Étiquettes ou instructions | ✅ | Tous les boutons ont un `help` tooltip + libellé explicite. Le chat_input a un placeholder « Votre question... ». |
| 3.3.3 Suggestion après erreur | ✅ | Bot de fallback explicite : `Essaie : 'recommande une formation', 'top 5 en management', ou 'prix de Leadership'.` |
| 3.3.4 Prévention des erreurs | ✅ | Action destructrice (suppression de toutes les conversations) protégée par une **confirmation à deux étapes** avec bouton « Annuler ». |

### 2.4 Robuste (le contenu doit être suffisamment robuste pour les agents utilisateurs et technologies d'assistance)

| Critère WCAG | État | Mesure dans FormaBot |
|---|---|---|
| 4.1.1 Analyse syntaxique | ✅ | HTML produit par Streamlit valide W3C. |
| 4.1.2 Nom, rôle, valeur | ✅ | Composants Streamlit natifs avec rôle ARIA implicite correct (button, textbox, tabs). |
| 4.1.3 Messages d'état | ⚠️ Partiel | `st.success`, `st.warning`, `st.error` utilisés mais pas annoncés par tous les lecteurs d'écran de manière fiable selon les implémentations. |

## 3. Tests effectués

- **Navigation clavier complète** : 100% des actions de la sidebar et de l'onglet chat accessibles uniquement avec Tab + Enter + Espace.
- **Lecteur d'écran** : test rapide avec NVDA (Windows). Les libellés des boutons, les en-têtes, les messages sont correctement annoncés. Limite : les tooltips `help` ne sont annoncés que sur certains lecteurs (dépend de l'implémentation Streamlit).
- **Zoom 200%** : layout préservé, scroll horizontal apparaît seulement sur les très grandes tables (Catalogue complet).
- **Contraste** : vérifié sur https://webaim.org/resources/contrastchecker — passe AA sur le thème par défaut.

## 4. Limites connues et perspectives

**Limites assumées (héritées de Streamlit)** :

1. **Pas de personnalisation fine des attributs ARIA** : Streamlit ne permet pas de surcharger `aria-label`, `aria-describedby`, `role`. Le passage en composants custom React/Streamlit Components serait nécessaire pour une conformité RGAA stricte.
2. **Pas de skip-link** : impossible à ajouter sans modifier le runtime Streamlit.
3. **Messages d'état (`st.toast`, `st.success`)** : annonces par lecteur d'écran dépendantes de l'implémentation, pas toujours fiables.

**Perspectives post-soutenance** :

- **Audit RGAA officiel** par un consultant certifié (DINUM ou cabinet privé) pour obtenir un score formel et une déclaration de conformité publique.
- **Migration progressive** vers des composants Streamlit Components custom pour les actions critiques (chat, suppression) permettant un contrôle ARIA total.
- **Tests utilisateurs** avec des personnes en situation de handicap (vision, motricité) pour valider en conditions réelles.
- **Internationalisation** de l'interface (libellés FR/EN/autres) pour répondre aux besoins linguistiques.

## 5. Synthèse

**Score auto-évalué** : conformité **WCAG 2.1 AA partielle**. La majorité des critères de niveau A et AA sont atteints (~85%). Les critères partiellement atteints concernent essentiellement des limites du framework Streamlit (skip-links, ARIA personnalisé, messages d'état).

**Ce qui est défendable en soutenance** : un effort réel et mesurable d'accessibilité, avec une démarche structurée (audit par principe WCAG, tableau de conformité critère par critère, identification honnête des limites, plan d'amélioration). Pour une diffusion réelle commerciale, un audit officiel reste indispensable.

---

**Références** :
- WCAG 2.1 : https://www.w3.org/TR/WCAG21/
- RGAA 4.1 : https://accessibilite.numerique.gouv.fr/
- Documentation Streamlit accessibility : https://docs.streamlit.io/develop/concepts/accessibility
- Outil de vérification contraste : https://webaim.org/resources/contrastchecker
