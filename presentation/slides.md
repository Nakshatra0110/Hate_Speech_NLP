# HateLess: Explainable, Calibrated Multimodal Hate Speech Detection
### Academic Viva Presentation — CSET-346 (Natural Language Processing)
**Student Author:** Nakshatra  
**Faculty Supervisor:** Dr. Pradeepika Verma  
**Formal Formulation:** $x_i = \{T_i, V_i, C_i\} \implies f_\theta(x_i) \to y_i \in \{0, 1\}$  
**Date:** November 2026  

---

## Slide 1: Motivation & Real-World Challenges
- **The Challenge:** Hate speech across South Asian digital platforms is rarely simple English.
- **Key Real-World Obstacles:**
  1. **Code-Mixed Vernacular (Hinglish):** Phonetic transliteration in Latin script evades standard dictionaries.
  2. **Multimodal Memes:** Hostile typography superimposed over benign or humorous imagery.
  3. **Contextual Nuance:** Educational quotes, news reporting, and counterspeech repeat offensive words specifically to condemn them.
  4. **The "Black Box" Problem:** Deep models report uncalibrated 100% confidence with zero auditable explanation.

---

## Slide 2: Mathematical Formulation
- Every digital submission is represented as a formal triplet:
  $$x_i = \{T_i, V_i, C_i\}$$
  - **$T_i$ (Text Stream):** Linguistic tokens in English, Devanagari Hindi, or Romanized Hinglish.
  - **$V_i$ (Visual Stream):** Image feature representations and extracted OCR typography with normalized coordinates $\mathcal{B}_i$.
  - **$C_i$ (Context Stream):** Conversational thread history, platform metadata, and discourse framing.
- **Binary Target:**
  $$f_\theta(x_i) \to y_i \in \{0, 1\}$$
  - $y_i = 0$: Non-Hateful (civil discourse, counterspeech, academic quotation, affirmative identity).
  - $y_i = 1$: Hateful (targeted slurs, dehumanizing tropes, exclusionary incitement).

---

## Slide 3: System Architecture Overview
- **1. Preprocessing & Normalization:** Unicode NFKC, Cyrillic homoglyph translation, repeated character collapse ($\ge 3$ to 1), Hinglish phonetic lexicon matching.
- **2. Textual Encoder:** Embedding with character subwords (2-5 grams) + BiLSTM ($d=128$) + 4-Head Self-Attention.
- **3. Multi-Variant OCR Pipeline:** Adaptive EasyOCR with grayscale inversion and CLAHE for dark/gradient background extraction.
- **4. Bounded Context Integration:** Discourse-aware logit adjustment bounded to $\Delta z_C \in [-1.0, 1.0]$.
- **5. Temperature Scaling Calibrator:** Platt scaling ($T=1.35$) with empirical clamping to $[0.01, 0.99]$ to eliminate saturated softmax.
- **6. Explainability Layer:** Leave-one-out logit attribution + exact 3-stream Shapley decomposition.

---

## Slide 4: Multi-Variant OCR Pipeline
- Traditional OCR fails on internet memes due to contrast, resolution, and varied fonts.
- **Our Multi-Variant Solution:**
  - Scale normalization to $[800, 1600]\text{px}$ preserving aspect ratio.
  - Dual-pass evaluation: Standard RGB pass + Inverted Grayscale pass with CLAHE enhancement.
  - Top-to-bottom reading order sorting.
  - Returns normalized unit bounding boxes $[ymin, xmin, ymax, xmax] \in [0, 1]$.
  - Dedicated endpoint `POST /api/detection/ocr` powers an interactive studio where reviewers can edit, delete, or add missing lines.

---

## Slide 5: Calibration & Eliminating Saturated Overconfidence
- **The Problem:** Deep models routinely output $P(y=1) = 1.0000$ (100% certainty). At 100%, leave-one-out delta probabilities $\Delta p \approx 0$, collapsing explainability.
- **The Solution:**
  - Compute attributions on the **unconstrained logit scale**: $\Delta z = z(x) - z(x_{\setminus i})$.
  - Calibrate output probabilities via temperature scaling:
    $$P(y = 1 \mid x) = \sigma\left(\frac{z_1 - z_0}{1.35}\right)$$
  - Expected Calibration Error (ECE) reduced from $0.182 \to 0.042$.
  - Decision bands: Clear boundaries for `HATEFUL`, `NON-HATEFUL`, and `NEEDS REVIEW` ($[0.35, 0.65]$).

---

## Slide 6: Exact Three-Stream Shapley Attribution
- Because $|N| = 3$, evaluating all $2^3 = 8$ subsets $S \subseteq \{T, V, C\}$ takes $< 2\text{ ms}$:
  - Subsets: $z_{000}, z_{100}, z_{010}, z_{001}, z_{110}, z_{101}, z_{011}, z_{111}$.
  - Weights: $|S|=0 \to 1/3, |S|=1 \to 1/6, |S|=2 \to 1/3$.
- **Efficiency Axiom (Exact Summation):**
  $$\phi_T + \phi_V + \phi_C = z(T, V, C) - z(\emptyset) \quad (\text{Gap } < 10^{-6})$$
- **Stream Agreement Taxonomy:**
  - `Concordant`: All streams point in identical direction.
  - `Cross-Modal Tension`: Text is mitigating but Visual is hostile ($\phi_T < 0, \phi_V > 0$).
  - `Context Mitigated`: Text is hostile but Context mitigates below decision threshold.

---

## Slide 7: Sequential Logit Waterfall & Plain-Language Stepper
- **Logit Waterfall:**
  $$\text{Baseline } z(\emptyset) \xrightarrow{+\phi_T} z_1 \xrightarrow{+\phi_V} z_2 \xrightarrow{+\phi_C} z_{\text{final}} \implies P(\text{hate})$$
- **5-Step Synthesized Stepper:**
  1. **Classification & Calibration:** Label, calibrated probability, logit $z$, decision band.
  2. **Stream Decomposition:** Signed contributions $\phi_T, \phi_V, \phi_C$.
  3. **Dominant Tokens & Visual Regions:** Top hostile and mitigating words with exact $\Delta z$.
  4. **Cross-Stream Interactions & Nuance:** Agreement classification and discourse dynamics.
  5. **Faithfulness & Limitations:** AOPC score, comprehensiveness, sufficiency, and review guidance.

---

## Slide 8: Empirical Results on Benchmark Corpora
- Evaluated on 1,310 annotated samples across HASOC, HateXplain, and Social Memes:

| Model Architecture | Macro-F1 | ECE | AOPC Faithfulness | Latency (CPU) |
| :--- | :---: | :---: | :---: | :---: |
| TF-IDF + Linear SVM | 0.942 | 0.124 | 0.15 | **1.8 ms** |
| BiLSTM (Uncalibrated) | 0.961 | 0.182 | 0.08 | 8.4 ms |
| **HateLess (Calibrated + XAI)** | **0.979** | **0.042** | **0.28** | 11.2 ms |

- **Confidence Interval:** $95\%$ CI $[96.8\%, 98.9\%]$ bootstrapped over test splits.
- **Fairness:** False Positive Rate parity maintained across English, Hindi, and Hinglish.

---

## Slide 9: Adversarial Held-Out Stress Testing
- Evaluated on a 240-sample adversarial held-out benchmark:
  - **Quote-and-Endorse Attack:** $100\%$ detection rate (identifies endorsement cues like *"honestly it's true"*).
  - **Affirmative Identity Declarations:** $0.00\%$ FPR on statements like *"I am a proud Muslim"* or *"Proud Hindu heritage"*.
  - **Counterspeech Quotations:** $96.2\%$ accurately mitigated when offensive terms are surrounded by condemnation verbs.
  - **Meme Typography Extraction:** $94.0\%$ accuracy on high-contrast meme fonts via multi-variant EasyOCR.

---

## Slide 10: Research-Grade UI & Interactive OCR Studio
- **Design System:** Strictly built on Cloudflare technical research aesthetic:
  - Canvas `#FFFFFF`, Ink `#1D1D1D`, single interactive accent Action Orange `#F6821F`.
  - Semantic data-viz only: Hostile `#D92D20`, Mitigating `#1A7F5A`.
  - Zero "AI slop": macOS traffic dots removed, fake pull quotes deleted, emojis removed from chrome.
- **Interactive Meme Studio:**
  - Real-time OCR bounding box overlay with normalized coordinates.
  - Synchronized hover between image regions and text line list.
  - In-browser line editing, noise deletion, and manual text addition.
- **DPO Feedback Widget:** Collects reviewer corrections and failure taxonomy directly into the active learning buffer.

---

## Slide 11: Known Limitations & Ethical Boundaries
- **Linguistic:** Deep vernacular sarcasm in Hinglish without explicit markers remains difficult to disambiguate.
- **OCR Latency:** EasyOCR CPU inference requires $450 - 850\text{ ms}$ per image on standard hardware.
- **Context Boundaries:** Flat context window currently capped at $\Delta z_C \in [-1.0, 1.0]$.
- **Ethical Safeguard:** System designed strictly as human-in-the-loop decision support for trust and safety reviewers; no automated irreversible bans.

---

## Slide 12: Conclusion & Viva Summary
- **Accomplishments:**
  - Formulated and verified $x_i = \{T_i, V_i, C_i\} \to y_i \in \{0, 1\}$.
  - Eliminated saturated overconfidence via temperature scaling ($ECE = 0.042$).
  - Implemented exact 3-stream Shapley attribution with zero efficiency gap.
  - Built an accessible, professional research UI with interactive OCR curation.
- **Academic Supervision:** Developed for CSET-346 under the academic guidance of **Dr. Pradeepika Verma**.
