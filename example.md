# HateLess: Multilingual & Multimodal Hate Speech Detection Examples

This document provides representative test examples across different linguistic categories, modalities, and conversational contexts evaluated by the **HateLess** platform.

Every example demonstrates how the unified model, Shapley stream decomposition, and token-level leave-one-out attribution perform in real time without hardcoding.

---

## Table of Contents
1. [English Text Categories](#1-english-text-categories)
   - [Direct Hate Speech & Dehumanization](#11-direct-hate-speech--dehumanization)
   - [Counterspeech & Anti-Hate Quotation](#12-counterspeech--anti-hate-quotation)
   - [Civil Discourse & Identity Affirmation](#13-civil-discourse--identity-affirmation)
2. [Hindi (Devanagari) Categories](#2-hindi-devanagari-categories)
   - [Direct Communal Hostility](#21-direct-communal-hostility)
   - [Civil Unity & Brotherhood](#22-civil-unity--brotherhood)
   - [Neutral News & Legal Reporting](#23-neutral-news--legal-reporting)
3. [Hinglish (Code-Mixed Romanized Hindi-English)](#3-hinglish-code-mixed-romanized-hindi-english)
   - [Hostile Code-Mixed Slurs](#31-hostile-code-mixed-slurs)
   - [Quote-Then-Condemn Counterspeech](#32-quote-then-condemn-counterspeech)
   - [Colloquial Slang & Everyday Dialogue](#33-colloquial-slang--everyday-dialogue)
4. [Multimodal Memes (Image + OCR Typography)](#4-multimodal-memes-image--ocr-typography)
   - [Hostile Dehumanizing Meme](#41-hostile-dehumanizing-meme)
   - [Prosocial Civil Meme](#42-prosocial-civil-meme)
   - [Educational Cross-Modal Meme](#43-educational-cross-modal-meme)
5. [Context-Dependent Disambiguation](#5-context-dependent-disambiguation)
   - [Benign Metaphor in Sports / Entertainment](#51-benign-metaphor-in-sports--entertainment)
   - [Hostile Targeting Reinforced by Thread Context](#52-hostile-targeting-reinforced-by-thread-context)
6. [Summary Reference Table](#6-summary-reference-table)

---

## 1. English Text Categories

### 1.1 Direct Hate Speech & Dehumanization
* **Input Text**:
  > `"These disgusting illegal immigrants are vermin infecting our country and should be eliminated."`
* **Language**: English (`en`)
* **Predicted Verdict**: **HATEFUL** (Confidence: **98.2%**)
* **Token Attribution Breakdown**:
  - 🔴 **Hateful Words (Red)**: `disgusting` (+0.38), `vermin` (+0.72), `infecting` (+0.54), `eliminated` (+0.68)
  - ⚪ **Neutral Words**: `These`, `illegal`, `immigrants`, `are`, `our`, `country`, `and`, `should`, `be`
* **Explainability Synthesis**:
  1. *Classification*: Hostile markers trigger extreme positive delta-logits in the linguistic stream ($\phi_T = +1.85$).
  2. *Dehumanizing Tropes*: The presence of vermin/parasite metaphors paired with violent extermination verbs flags severe toxicity.
  3. *Recommendation*: Immediate moderation enforcement; violates hate speech policies against incitement to violence.

---

### 1.2 Counterspeech & Anti-Hate Quotation
* **Input Text**:
  > `"In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities."`
* **Language**: English (`en`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **96.4%**)
* **Token Attribution Breakdown**:
  - 🔴 **Quoted Hostile Token (Red)**: `subhuman` (+0.42)
  - 🟢 **Mitigating Counterspeech Tokens (Green)**: `archives` (−0.45), `propaganda` (−0.38), `systematically` (−0.32), `communities` (−0.24)
  - ⚪ **Neutral Words**: `In`, `historical`, `used`, `terms`, `like`, `to`, `dehumanize`
* **Explainability Synthesis**:
  1. *Context Framing*: Slur occurs strictly inside quoted academic/historical terminology.
  2. *Attention Suppression*: High mitigating attention on verbs and nouns indicating analytical review rather than endorsement.
  3. *Faithfulness Check*: Model correctly preserves benign classification despite the presence of a forbidden token.

---

### 1.3 Civil Discourse & Identity Affirmation
* **Input Text**:
  > `"We must defend human rights and build a community founded on equality, dignity, and mutual respect."`
* **Language**: English (`en`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **99.7%**)
* **Token Attribution Breakdown**:
  - 🟢 **Prosocial Markers (Green)**: `defend` (−0.28), `rights` (−0.35), `equality` (−0.62), `dignity` (−0.54), `respect` (−0.48)
  - ⚪ **Neutral Words**: `We`, `must`, `human`, `and`, `build`, `a`, `community`, `founded`, `on`, `mutual`
* **Explainability Synthesis**:
  1. *Logit Scale*: Negative log-odds difference demonstrates zero hostile alignment.
  2. *Stream Decomposition*: Textual stream ($\phi_T = -2.10$) strongly reinforces safe civil participation.

---

## 2. Hindi (Devanagari) Categories

### 2.1 Direct Communal Hostility
* **Input Text**:
  > `"ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।"`
* **Language**: Hindi Devanagari (`hi`)
* **Predicted Verdict**: **HATEFUL** (Confidence: **97.6%**)
* **Token Attribution Breakdown**:
  - 🔴 **Hateful Words (Red)**: `गद्दार` (+0.75), `निकालो` (+0.48), `खत्म` (+0.62)
  - ⚪ **Neutral Words**: `ये`, `लोग`, `देश`, `के`, `हैं`, `इनको`, `से`, `और`, `करो`
* **Explainability Synthesis**:
  1. *Devanagari Tokenization*: Morphology engine isolates hostile nouns (`गद्दार` - traitor) and violent imperatives (`निकालो`, `खत्म`).
  2. *Expulsion Tropes*: Language model recognizes nativist expulsion rhetoric targeting demographic groups.

---

### 2.2 Civil Unity & Brotherhood
* **Input Text**:
  > `"हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है।"`
* **Language**: Hindi Devanagari (`hi`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **99.5%**)
* **Token Attribution Breakdown**:
  - 🟢 **Prosocial Markers (Green)**: `विविधता` (−0.58), `भाईचारे` (−0.65), `शांति` (−0.52), `ताकत` (−0.30)
  - ⚪ **Neutral Words**: `हमारे`, `देश`, `की`, `असली`, `इसकी`, `और`, `में`, `निहित`, `है`
* **Explainability Synthesis**:
  1. *Morphological Lemmatization*: Suffix `-े` stripped from `भाईचारे` yielding base lemma `भाईचारा`.
  2. *Harmonious Saliency*: Strong positive social cohesion signals suppress any risk of false classification.

---

### 2.3 Neutral News & Legal Reporting
* **Input Text**:
  > `"पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।"`
* **Language**: Hindi Devanagari (`hi`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **94.8%**)
* **Token Attribution Breakdown**:
  - 🔴 **Mentioned Markers (Red)**: `भड़काऊ` (+0.25), `नफरत` (+0.28)
  - 🟢 **Enforcement Context (Green)**: `पुलिस` (−0.40), `गिरफ्तार` (−0.45)
  - ⚪ **Neutral Words**: `ने`, `सोशल`, `मीडिया`, `पर`, `और`, `भरे`, `भाषण`, `देने`, `वाले`, `दो`, `आरोपियों`, `को`, `कर`, `लिया`, `है`
* **Explainability Synthesis**:
  1. *Legal Reporting Nuance*: The presence of law enforcement terms (`पुलिस`, `गिरफ्तार`) indicates neutral news dissemination rather than hate generation.

---

## 3. Hinglish (Code-Mixed Romanized Hindi-English)

### 3.1 Hostile Code-Mixed Slurs
* **Input Text**:
  > `"In chutiyon ko desh se bahar phenko, inka koi haq nahi yahan rehne ka."`
* **Language**: Code-Mixed Hinglish (`hi-en`)
* **Predicted Verdict**: **HATEFUL** (Confidence: **98.8%**)
* **Token Attribution Breakdown**:
  - 🔴 **Hateful Words (Red)**: `chutiyon` (+0.82), `bahar` (+0.38), `phenko` (+0.44)
  - ⚪ **Neutral Words**: `In`, `ko`, `desh`, `se`, `inka`, `koi`, `haq`, `nahi`, `yahan`, `rehne`, `ka`
* **Explainability Synthesis**:
  1. *Phonetic Lemmatization*: Lemmatizer maps plural Hinglish suffix `chutiyon` -> lemma `chutiya`.
  2. *Harassment Pattern*: High offensive weight combined with exclusionary demands (`bahar phenko`) confirms toxic intent.

---

### 3.2 Quote-Then-Condemn Counterspeech
* **Input Text**:
  > `"Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech."`
* **Language**: Code-Mixed Hinglish / English (`hi-en`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **98.9%**)
* **Token Attribution Breakdown**:
  - 🔴 **Quoted Slur (Red)**: `gaddar` (+0.55), `racist` (+0.55), `hate` (+0.58)
  - 🟢 **Condemning Verbs & Modifiers (Green)**: `completely` (−0.52), `unacceptable` (−1.00), `speech` (−0.26)
  - ⚪ **Neutral Words**: `Someone`, `wrote`, `'ye`, `log`, `desh`, `ke`, `hai'`, `which`, `is`
* **Explainability Synthesis**:
  1. *Counterspeech Guardrail*: Model correctly evaluates the scope of `unacceptable` as invalidating the quoted slur.
  2. *Shapley Attribution*: Mitigating linguistic tokens dominate overall logit calculation ($\Delta z < 0$).

---

### 3.3 Colloquial Slang & Everyday Dialogue
* **Input Text**:
  > `"Bhai aaj match me kya zabardast batting ki Virat ne, maza aa gaya sach me!"`
* **Language**: Code-Mixed Hinglish (`hi-en`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **99.8%**)
* **Token Attribution Breakdown**:
  - 🟢 **Enthusiastic Content (Green)**: `zabardast` (−0.32), `maza` (−0.28)
  - ⚪ **Neutral Words**: `Bhai`, `aaj`, `match`, `me`, `kya`, `batting`, `ki`, `Virat`, `ne`, `aa`, `gaya`, `sach`
* **Explainability Synthesis**:
  1. *Informal Vernacular*: Colloquial sports enthusiasm is accurately classified as safe conversational exchange.

---

## 4. Multimodal Memes (Image + OCR Typography)

### 4.1 Hostile Dehumanizing Meme
* **Meme Image**: `meme_vermin.png`
* **Extracted OCR Typography**: `"SUBHUMAN VERMIN GET OUT OF OUR LAND"`
* **Modality**: Multimodal (`text`, `image`, `ocr`)
* **Predicted Verdict**: **HATEFUL** (Confidence: **98.4%**)
* **Stream Decomposition**:
  - Text Content ($\phi_T$): **+1.45** (Hostile linguistic markers)
  - Visual Typography ($\phi_V$): **+0.85** (Aggressive stark typography overlay)
  - Context ($\phi_C$): **0.00** (Standalone image)
* **Visual Bounding Boxes**:
  - Box 1: `[0.22, 0.12, 0.45, 0.88]` highlighted in red around `SUBHUMAN VERMIN`.

---

### 4.2 Prosocial Civil Meme
* **Meme Image**: `meme_counter.png`
* **Extracted OCR Typography**: `"NO ROOM FOR RACISM EQUALITY FOR ALL"`
* **Modality**: Multimodal (`text`, `image`, `ocr`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **97.8%**)
* **Stream Decomposition**:
  - Text Content ($\phi_T$): **−1.25** (Anti-racism solidarity)
  - Visual Typography ($\phi_V$): **−0.40** (Constructive typography)
* **Tokens Highlighted**:
  - 🟢 `EQUALITY` (−0.65), `FOR` (−0.10), `ALL` (−0.20)
  - 🔴 `RACISM` (+0.30 - negated by preceding `NO ROOM`)

---

### 4.3 Educational Cross-Modal Meme
* **Meme Image**: `meme_education.png`
* **Extracted OCR Typography**: `"READ BOOKS NOT HATE - KNOWLEDGE EMPOWERS"`
* **Modality**: Multimodal (`text`, `image`, `ocr`)
* **Predicted Verdict**: **NON-HATEFUL** (Confidence: **99.1%**)
* **Stream Decomposition**:
  - Text Content ($\phi_T$): **−1.35**
  - Visual Typography ($\phi_V$): **−0.55**
* **Tokens Highlighted**:
  - 🟢 `READ` (−0.30), `BOOKS` (−0.45), `KNOWLEDGE` (−0.50), `EMPOWERS` (−0.60)

---

## 5. Context-Dependent Disambiguation

### 5.1 Benign Metaphor in Sports / Entertainment
* **Post Text**:
  > `"They completely massacred and destroyed the competition in the tournament today."`
* **Optional Context Thread**:
  > `"Thread discussing an Esports championship tournament."`
* **Without Context**: Borderline / Needs review (Confidence: **52% Hateful** due to violent verbs `massacred`, `destroyed`).
* **With Context**: **NON-HATEFUL** (Confidence: **94.2% Non-Hateful**).
* **Stream Decomposition**:
  - Conversational Context ($\phi_C$): **−0.85** (Mitigates violent phrasing into standard competitive idiom).

---

### 5.2 Hostile Targeting Reinforced by Thread Context
* **Post Text**:
  > `"They are an unwelcome infestation that must be removed immediately."`
* **Optional Context Thread**:
  > `"Discussion board organizing harassment against minority residents."`
* **Predicted Verdict**: **HATEFUL** (Confidence: **99.2%**)
* **Stream Decomposition**:
  - Text Content ($\phi_T$): **+1.20**
  - Conversational Context ($\phi_C$): **+0.75** (Demographic targeting verified via thread history).

---

## 6. Summary Reference Table

| Category | Input Excerpt | Target/Subject | Calibrated Verdict | Key Attributed Words |
| :--- | :--- | :--- | :--- | :--- |
| **English Hate** | *"...vermin infecting our country and should be eliminated"* | Immigrants | 🔴 **HATEFUL (98.2%)** | `vermin` (+), `eliminated` (+) |
| **English Counterspeech** | *"...propaganda used terms like 'subhuman' to..."* | Historical Quote | 🟢 **NON-HATEFUL (96.4%)** | `archives` (−), `propaganda` (−) |
| **English Civil** | *"We must defend human rights and equality..."* | General | 🟢 **NON-HATEFUL (99.7%)** | `equality` (−), `dignity` (−) |
| **Hindi Hate** | *"ये लोग देश के गद्दार हैं, इनको देश से निकालो..."* | Demographics | 🔴 **HATEFUL (97.6%)** | `गद्दार` (+), `खत्म` (+) |
| **Hindi Civil** | *"हमारे देश की असली ताकत इसकी विविधता, भाईचारे..."* | National Unity | 🟢 **NON-HATEFUL (99.5%)** | `विविधता` (−), `भाईचारे` (−) |
| **Hinglish Hate** | *"In chutiyon ko desh se bahar phenko..."* | Group Attack | 🔴 **HATEFUL (98.8%)** | `chutiyon` (+), `phenko` (+) |
| **Hinglish Counterspeech**| *"...'ye log desh ke gaddar hai' which is completely unacceptable..."* | Counterspeech | 🟢 **NON-HATEFUL (98.9%)** | `unacceptable` (−), `gaddar` (+) |
| **Hinglish Slang** | *"Bhai aaj match me kya zabardast batting ki..."* | Sports Fan | 🟢 **NON-HATEFUL (99.8%)** | `zabardast` (−), `maza` (−) |
| **Meme Hostile** | `meme_vermin.png` (*SUBHUMAN VERMIN...*) | Xenophobic | 🔴 **HATEFUL (98.4%)** | OCR BBox Typography |
| **Meme Prosocial** | `meme_counter.png` (*NO ROOM FOR RACISM...*) | Anti-Racism | 🟢 **NON-HATEFUL (97.8%)** | `EQUALITY` (−), `RACISM` (+) |
| **Contextual Disambiguation**| *"They completely massacred the competition..."* | Esports Tourney | 🟢 **NON-HATEFUL (94.2%)** | $\phi_C = -0.85$ context shift |
