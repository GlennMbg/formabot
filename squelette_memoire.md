# Squelette du mémoire — M2 Nexa Digital School

**Certification** : Chef de projet Data et Intelligence Artificielle — RNCP 37137
**Fichier final** : `MBOGA_GLENN_THESE.pdf`
**Deadline officielle** : 1er juillet 2026 23h59 (Teams)
**Deadline interne** : 15 juin pour V1 (soutenance blanche fin juin)

## Cadre imposé par le guide Nexa

- **50 pages ± 10 %** hors annexes
- **Police** : Times New Roman 12 / Arial 11 / Calibri 12
- **Marges** : 2,5 cm
- **Interligne** : 1,5 maximum
- **Pages numérotées**, titres cohérents
- **Logo Nexa Digital School** sur la page de présentation

## Livrables ZIP à joindre
- URL publique de l'application (obligatoire — déploiement requis)
- URL du dépôt Git (facultatif)
- Code source complet
- **Fichier SQL d'export (dump)** ← migration depuis CSV requise
- Fichiers de configuration
- README/PDR : prérequis, étapes d'installation, identifiants de test, accès admin
- Support de présentation séparé : `MBOGA_GLENN_PREZ.pdf`

## Cadre du projet

**Projet** : *FormaBot* (nom provisoire — à valider), assistant conversationnel de recommandation de formations professionnelles pour les **dirigeants de TPE du secteur BTP**.

**Entreprise** : **ADN Potentiel**, cabinet de formation, de conseil et de coaching spécialisé dans l'accompagnement des dirigeants de TPE du secteur BTP (entreprise réelle, ton activité).

**Mission** : aider les dirigeants à identifier et choisir la formation la plus adaptée à leur besoin parmi le catalogue d'ADN Potentiel, à travers une interface conversationnelle accessible, transparente et conforme aux exigences réglementaires (AI Act, RGPD).

**Périmètre fonctionnel** : deux grandes thématiques :
- **Management & Leadership** : communication d'équipe, recrutement, délégation, gestion de conflits, posture de dirigeant, conduite du changement
- **Gestion & Pilotage TPE** : tableaux de bord, lecture du bilan comptable, trésorerie, marges chantier, fiscalité, pilotage financier

## Organisation des fichiers du projet

Le dossier mémoire contient **deux applications Python** :

- **`app_formabot.py`** — c'est le projet qui fait l'objet du mémoire (livré au jury). Charge `formations_adn.csv` et `formations_training_corpus.csv`. Historique des conversations dans `conversations_formabot.json`. Toute la rédaction et les évaluations doivent se baser sur ce fichier.
- **`app.py`** — projet AniReco (assistant anime), préservé tel quel à des fins de poursuite personnelle après la soutenance. **Ne pas mentionner dans le mémoire.**

Les fichiers de données associés à FormaBot :
- `formations_adn.csv` — catalogue ADN Potentiel (à remplacer par le vrai catalogue dès que dispo, version placeholder de 17 formations fournie)
- `formations_training_corpus.csv` — 223 phrases d'entraînement sur 19 intentions
- `evaluation/test_set_formations.csv` — 91 phrases de test indépendantes
- `conversations_formabot.json` — historique généré à l'exécution (n'existe pas tant que le bot n'a pas reçu de message)

---

## Plan détaillé (50 pages)

| Section | Pages | Jour |
|---|---|---|
| Page de présentation + sommaire | 3 | J17 |
| 1. Descriptif de l'entreprise (ADN Potentiel) | 5 | J12 |
| 2. Étude de marché et analyse concurrentielle | 6 | J13 |
| 3. Problématique et définition du besoin | 3 | J14 |
| 4. Gestion de projet | 9 | J14 |
| 5. Exploitation des données | 13 | J15 |
| 6. Développement de l'application | 9 | J16 |
| 7. Conclusion | 2 | J17 |
| **Total** | **50** | |
| Annexes (hors comptage) | 5-8 | J17 |

---

## 1. Descriptif de l'entreprise (~5 pages) — ADN Potentiel

### 1.1 Storytelling (~1 page)
- Date de création, contexte (réponse aux besoins d'accompagnement des TPE BTP face à la complexification réglementaire et économique)
- Parcours du fondateur
- Évolutions clés depuis la création

### 1.2 Valeurs et missions (~1 page)
- Mission : accompagner les dirigeants TPE BTP dans le développement de leur entreprise et de leurs compétences
- Valeurs : proximité terrain, pédagogie pragmatique, accompagnement individualisé
- Engagement Qualiopi (à vérifier — à mentionner si applicable)

### 1.3 Activité principale (~1 page)
- 3 piliers : formation professionnelle, conseil opérationnel, coaching individuel
- Cibles : dirigeants TPE BTP, conjoints collaborateurs, artisans en croissance
- Format dominant : présentiel + distanciel selon besoin

### 1.4 Environnement économique et sociétal (~1 page)
- Le secteur BTP représente XX% du PIB français (source INSEE — à actualiser)
- Crise de la main-d'œuvre, difficulté à recruter, besoin de fidéliser
- Plan France 2030 et transition énergétique = nouveaux besoins de formation
- Démographie des dirigeants TPE : âge moyen, taux de transmission, etc.

### 1.5 Environnement technologique (~0.5 page)
- Outils CRM, gestion de planning formation, plateforme LMS éventuelle
- Présence digitale : site web, réseaux pros (LinkedIn)

### 1.6 Environnement de données (~0.5 page)
- Catalogue des formations (cœur du projet AnimeBot)
- Données clients (hors scope du projet IA — pas de traitement de données personnelles)
- Sources externes envisagées pour benchmark : catalogue CPF, Bpifrance Université

---

## 2. Étude de marché et analyse concurrentielle (~6 pages)

### 2.1 Analyse de marché (~3 pages)

**Sources OBLIGATOIRES** : INSEE, Credoc, sites gouvernementaux, max 5 ans. Citations en notes de bas de page.

À couvrir :
- **Dynamique du marché de la formation professionnelle** en France
- **Spécificités du marché BTP TPE** : 600 000 entreprises BTP dont >95% TPE
- **Marché de la formation continue dirigeants** : taux d'accès, freins identifiés (temps, coût, pertinence)
- **Évolution post-réforme** "Avenir professionnel" 2018 et impact CPF
- **Réglementation** : Qualiopi (obligatoire depuis 2022), AI Act 2024, RGPD

Sources à creuser :
- INSEE — entreprises du BTP (édition annuelle)
- Credoc — Pratiques de formation des dirigeants TPE/PME
- Centre Inffo / France Compétences — chiffres formation pro
- DARES (ministère du Travail) — données formation continue
- Fédération Française du Bâtiment (FFB) — études secteur

### 2.2 Analyses concurrentielles (~3 pages, 3 concurrents minimum)

**Format imposé** : *les unes à la suite des autres*, **pas en tableau**, même trame pour chaque.

**Concurrent direct 1 : CCCA-BTP**
- Présentation : organisme paritaire national de formation BTP
- Offre : formations métiers et management dédiées BTP
- Forces : maillage territorial, certification reconnue, financement OPCO
- Faiblesses : catalogue généraliste, peu de personnalisation pour le dirigeant

**Concurrent direct 2 : CAPEB / FFB formations**
- Présentation : formations proposées par les organisations professionnelles BTP
- Offre : formations techniques, gestion, juridique pour artisans
- Forces : connaissance terrain, tarifs préférentiels adhérents
- Faiblesses : interface vieillissante, pas de recommandation guidée

**Concurrent indirect : Bpifrance Université / CCI Formations**
- Présentation : offres de formation continue généralistes pour dirigeants PME
- Forces : reconnaissance, financements multiples, catalogue large
- Faiblesses : pas sectorielles BTP, expérience utilisateur de recherche médiocre

**Conclusion comparative (~0.5 page)**
- Différenciateur d'ADN Potentiel + FormaBot : conversation naturelle + spécialisation TPE BTP + recommandation contextuelle vs simple moteur de recherche
- Lacune comblée : aucun concurrent ne propose d'interface conversationnelle pour orienter le dirigeant vers la bonne formation parmi un catalogue spécialisé

---

## 3. Problématique et définition du besoin (~3 pages)

### 3.1 Genèse de la solution (~1 page)
- Constat : un dirigeant TPE BTP qui cherche une formation ne sait pas toujours formuler son besoin de manière catalogable
  - Il dit "j'ai du mal à recruter" plutôt que "formation gestion RH avancée"
  - Il dit "mes équipes ne sont pas motivées" plutôt que "formation leadership transformationnel"
- Le langage métier (BTP) et le langage formation ne coïncident pas
- Hypothèse : un assistant conversationnel intelligent peut traduire le besoin naturel en proposition pertinente
- Pourquoi pas un LLM ? Coût d'usage, opacité, non-explicabilité — contredit la conformité réglementaire

### 3.2 Problématique (~0.5 page)
Citer textuellement :

> *« Comment concevoir et déployer un pipeline NLP robuste capable de comprendre des requêtes multilingues, bruitées et hétérogènes dans un contexte métier réel (la recommandation de formations pour dirigeants TPE BTP), tout en garantissant performance, explicabilité, conformité réglementaire et intégration fluide dans une application web supervisée ? »*

### 3.3 Description fonctionnelle de la solution (~1.5 page)
- Le dirigeant dialogue en langage naturel avec FormaBot
- Le bot comprend 19 types d'intentions (recommandation, listing, recherche par format/durée/public/certif, infos sur une formation précise)
- Réponses contextualisées avec mémoire conversationnelle
- Transparence : confiance affichée pour chaque réponse
- Conformité : disclosure, export, suppression des données
- Filtres clés : éligibilité CPF, certification Qualiopi, format (présentiel/distanciel/hybride)

---

## 4. Gestion de projet (~9 pages)

### 4.1 Pilotage du projet et planification (~4 pages)

Sections imposées :
- **Méthode** : Scrum adapté en mode solo, sprints de 1 semaine, daily standup auto-administré
- **Rétroplanning** : Gantt visuel sur la période avril → juillet 2026
- **Outil** : présenter le Gantt (Excel, Plaky, Notion ou Trello)
- **Tableaux de bord** : capture du suivi (taux de tâches livrées par sprint)
- **Budget prévisionnel** :
  - Coût RH : ~40 jours-homme × TJM junior 250€ = 10 000€
  - Hébergement Streamlit Cloud : 0€ (free tier)
  - Domaine éventuel : ~15€/an
  - Licences logicielles : 0€ (tout open source)
  - Total : ~10 015€ pour un POC interne

### 4.2 Veille technologique, sectorielle et réglementaire (~2 pages)

**Format imposé** : tableau avec colonnes obligatoires.

| Source | Type | Fréquence | Outil |
|---|---|---|---|
| Hugging Face Papers | Technologique (modèles NLP) | Hebdo | RSS / Feedly |
| Arxiv cs.CL | Technologique | Hebdo | Arxiv Sanity |
| EUR-Lex (AI Act, RGPD) | Réglementaire | Mensuel | Alerte mail |
| CNIL — Actualités IA | Réglementaire | Bimensuel | RSS |
| Centre Inffo | Sectorielle (formation pro) | Bimensuel | Newsletter |
| France Compétences | Réglementaire/sectorielle | Mensuel | Site officiel |
| FFB Actualités | Sectorielle (BTP) | Hebdo | RSS |
| Capeb Actualités | Sectorielle (artisanat BTP) | Hebdo | RSS |
| Streamlit Releases | Technologique (outillage) | Mensuel | GitHub |

### 4.3 Cartographie des risques (~3 pages)

Sections imposées :

**4.3.1 Risques qualité/sécurité des données (~1 page)**
- Risque : exposition du catalogue ADN Potentiel à des tiers → mitigation : déploiement contrôlé, possibilité de basculer en authentification si commercialisation
- Risque : injection d'inputs malveillants → mitigation : normalisation, longueur max, pas d'exécution de code utilisateur
- Risque : fuite de conversations utilisateur → mitigation : stockage 100% local côté client, aucune télémétrie serveur

**4.3.2 Déviances éthiques (~0.75 page)**
- Risque : biais de recommandation favorisant systématiquement les formations les plus rentables → mitigation : algorithme transparent basé sur la pertinence et l'aléatoire pondéré, pas sur la marge
- Risque : enfermement dans une seule thématique (filter bubble) → mitigation : composante de découverte aléatoire systématique
- Risque : promesse implicite d'efficacité de la formation → mitigation : disclaimer clair "le bot oriente, ne garantit pas le résultat pédagogique"

**4.3.3 Enjeux environnementaux et sociétaux (~0.5 page)**
- Empreinte carbone : inference SVM ~10⁻⁶ fois celle d'un LLM → choix éthique défendable
- Modèle déployé sur Streamlit Community Cloud, hébergement mutualisé
- Accessibilité : engagement WCAG 2.1 AA, démarche inclusion handicap

**4.3.4 Charte éthique du projet (~0.75 page)**
Texte court (10-15 points). Exemples :
- Transparence sur la nature automatisée
- Respect des données utilisateur
- Non-discrimination dans les recommandations
- Documentation publique des limites du modèle
- Possibilité d'exercer les droits RGPD
- Pas de manipulation commerciale dissimulée
- Information sur les financements possibles (CPF, OPCO Constructys, etc.)

---

## 5. Exploitation des données (~13 pages)

### 5.1 Identification des sources de données (~4 pages)

**5.1.1 Sources sélectionnées (~1 page)**
- Source primaire : catalogue interne ADN Potentiel (~XX formations — à compléter une fois l'export CSV livré)
- Source d'enrichissement potentielle : extracts du catalogue Mon Compte Formation pour benchmark concurrentiel
- Format : CSV (un des trois formats acceptés ✓)

**5.1.2 Volumétrie et typographie (~1.5 page)**
- Tableau colonne par colonne (titre, thème, format, durée, prix, etc.) avec type et exemples
- ~19 colonnes prévues dans le schéma cible

**5.1.3 Dictionnaire de données (~1 page)**
Tableau exhaustif (à finaliser après réception du CSV) :

| Colonne | Type | Description | Utilisé par |
|---|---|---|---|
| `id` | int | Identifiant unique | PK base SQL |
| `title` | str | Titre de la formation | classifieur + UI |
| `theme` | str | Management ou Gestion | filtre theme |
| `format` | str | Présentiel/Distanciel/Hybride | filtre format |
| `duration_hours` | int | Durée en heures | filtre durée |
| `price_eur_ht` | int | Prix HT | filtre prix |
| ... | ... | ... | ... |

**5.1.4 Réglementation sur la collecte (~0.5 page)**
- Catalogue ADN Potentiel : données propriétaires, autorisation interne
- Pas de données personnelles utilisateur
- Conformité RGPD : la base ne contient aucune information identifiante

### 5.2 Manipulation des tables et analyse (~9 pages)

**5.2.1 Installation de la base SQLite (~1 page)**
- Capture d'écran de la base
- Schéma SQL : table `formations` avec PK, indexes sur (theme, format, certification)
- Capture résultat `SELECT * FROM formations LIMIT 5`

**5.2.2 Analyse des valeurs manquantes (~1.5 page)**
- Pour chaque colonne, % de NaN dans le catalogue ADN
- Stratégies adoptées : "Non précisé" pour catégorielles, NaN conservé pour numériques avec gestion `na_position`

**5.2.3 Sécurisation des données (~1 page)**
- Stockage local de conversations.json
- Aucun envoi externe
- Suppression à la demande (RGPD art. 17)
- Pas d'identification utilisateur

**5.2.4 Analyse avec algorithmes ML supervisés (~3 pages)**
- Split train/test : 223 phrases training / 91 phrases test (~71/29 ✓ respecte le 70/30 minimum)
- **Plusieurs algorithmes testés** : SVM (production), Naive Bayes, Logistic Regression, Random Forest, DistilBERT + LogReg
- Pour chacun : description, hyperparamètres, raison de la comparaison
- Commentaires du code source (scripts entraînement et test)

**5.2.5 Évaluation des performances (~1.5 page)**
- Indicateur **imposé** (classification) : Accuracy ✓
- + précision, rappel, F1 macro et weighted
- Comparaison temps requête SQLite avec/sans index
- Tableau comparatif + matrice de confusion + plot F1 vs latence
- Adapté du sprint 1-2 anime, refait avec le corpus formation

**5.2.6 Documentation technique du modèle (~0.5 page)**
- SVM + TF-IDF + CalibratedClassifierCV
- Justification : latence, explicabilité, performance, alignement avec la conformité

**5.2.7 Mesures éthiques (~0.5 page)**
- Anti-répétition des recommandations
- Affichage de la confiance pour transparence
- Pas de scoring "agressif" qui pousse les formations les plus chères

**5.2.8 Tableau de suivi des problématiques techniques (~1 page)**
| # | Date | Problématique | Date résolution | Solution |
|---|---|---|---|---|
| 1 | 11 mai | Confusion "top 5 anime de sport" → recommend_by_genre | 11 mai | Override regex `top N` + enrichissement corpus |
| 2 | 11 mai | Recherche fuzzy de titre > 45 s | 11 mai | Skip extract_title hors info_intents + rapidfuzz |
| 3 | 29 mai | Pivot domaine anime → formation BTP | 29 mai | Refonte corpus, schéma SQL, UI |
| ... | ... | ... | ... | ... |

À enrichir au fur et à mesure.

---

## 6. Développement de l'application incorporant un algorithme d'apprentissage supervisé (~9 pages)

### 6.1 URL et hébergement (~0.5 page)
- URL publique : `https://formabot-mboga.streamlit.app/` (à déployer)
- Hébergement : Streamlit Community Cloud (gratuit, mutualisé)
- Captures d'écran de l'app en ligne

### 6.2 Développement front (~2 pages)
- Architecture Streamlit : sidebar + 3 onglets (Chatbot, Exploration, Performance)
- Captures de chaque onglet
- Composants utilisés : `chat_input`, `chat_message`, `download_button`, `tabs`, `expander`

### 6.3 Intégration backend de l'algorithme (~2 pages)
- Architecture du pipeline NLP : normalize → TF-IDF → SVM → context
- Schéma fonctionnel (diagramme)
- Extrait commenté de `get_bot_response`

### 6.4 Tests et déploiement (~2 pages)
- Cas de test types (~15 cas)
- Procédure de déploiement Streamlit Cloud (étapes + captures)
- Versionning Git

### 6.5 Conformité réglementaire (~1.5 page)
- AI Act art. 50 : capture du bandeau disclosure
- RGPD art. 17 : capture du bouton suppression
- RGPD art. 20 : capture du bouton export JSON
- Model card : capture de la page model card
- Aucune donnée personnelle collectée

### 6.6 Accessibilité aux personnes en situation de handicap (~1 page)
- Conformité WCAG 2.1 niveau AA visée
- Navigation au clavier fonctionnelle (Streamlit natif)
- Tooltips/labels descriptifs sur tous les boutons
- Contraste de couleurs vérifié
- Police lisible (>= 14 pt body)
- Pas de dépendance à la couleur seule

---

## 7. Conclusion (~2 pages)

### 7.1 Bilan : contraintes, risques, enjeux (~1 page)
- Bilan technique : F1 macro (à mesurer sur corpus formation), latence, gain pour le dirigeant
- Bilan organisationnel : tenue du planning, défis (pivot anime → formation à mi-parcours)
- Bilan éthique : ce qui est couvert vs perspectives

### 7.2 Évolutions possibles (~1 page)
- Recherche sémantique sur les descriptions de formations (sentence-transformers)
- Intégration directe avec le CRM ADN Potentiel pour booker en direct
- Recommandations personnalisées basées sur l'historique du dirigeant
- Ajout d'un module de suivi post-formation (mesure d'impact)
- Évaluation A/B en production avec vrais utilisateurs

---

## Annexes (~5-8 pages, hors comptage)

- A. Liste exhaustive des 19 intentions avec exemples
- B. Schéma d'architecture global
- C. Rapport d'évaluation complet
- D. Captures d'écran complètes
- E. Tableau de suivi des problématiques techniques
- F. Charte éthique
- G. Bibliographie complète

---

## Bibliographie cible (25-30 références)

### NLP & ML
- [ ] Pedregosa et al., *Scikit-learn*, JMLR 2011
- [ ] Manning & Schütze, *Foundations of Statistical NLP*, 1999
- [ ] Sanh et al., *DistilBERT*, 2019
- [ ] Reimers & Gurevych, *Sentence-BERT*, 2019

### Évaluation
- [ ] Sokolova & Lapalme, *A systematic analysis of performance measures*, 2009

### Réglementation & éthique
- [ ] Règlement UE 2024/1689 (AI Act) — texte officiel
- [ ] Règlement UE 2016/679 (RGPD) — texte officiel
- [ ] Mitchell et al., *Model Cards*, 2019
- [ ] CNIL — Guide pour les acteurs de l'IA

### Marché formation professionnelle / BTP TPE
- [ ] INSEE — Les entreprises en France (édition annuelle BTP)
- [ ] Credoc — Pratiques de formation TPE/PME
- [ ] Centre Inffo / France Compétences — chiffres formation pro
- [ ] DARES — Formation continue en France
- [ ] FFB — Statistiques du bâtiment
- [ ] CAPEB — Observatoire de l'artisanat du bâtiment
- [ ] Constructys (OPCO BTP) — études secteur

### Réglementation formation
- [ ] Loi Avenir Professionnel (2018)
- [ ] Décret Qualiopi (2022)

### Études de cas / chatbots
- [ ] Bocklisch et al., *Rasa NLU*, 2017
- [ ] Documentation Streamlit officielle
- [ ] Documentation rapidfuzz

À compléter en parallèle (30 min/jour).

---

## Astuces pour tenir le calendrier

1. **Démarre la rédaction par les sections les plus simples** (descriptif ADN, biblio) pour mettre la machine en route.
2. **Écris d'abord en mode "déversement"** : pas de relecture pendant le premier jet.
3. **Insère les figures et tableaux au fur et à mesure**, pas à la fin.
4. **Note tes TODOs en gras dans le texte** pour ne pas perdre le fil.
5. **Sauvegarde en versions datées** : `MBOGA_GLENN_THESE_v01_J12.docx`.
6. **Imprime un brouillon au J17** pour la relecture finale.
