# Known Limitations and Failure Modes

**Project:** HateLess Academic Research Platform  
**Course:** CSET-346 (Natural Language Processing)  
**Supervisor:** Dr. Pradeepika Verma  
**Student Author:** Nakshatra  
**Audit Date:** November 2026  

---

## 1. Executive Summary

This document provides a transparent, empirical record of the known algorithmic, linguistic, multimodal, and computational limitations of the HateLess platform. As an academic prototype designed for research and human-in-the-loop moderation triage, these boundaries are documented to ensure safe deployment, truthful evaluation, and guided future improvements.

---

## 2. Linguistic & Dialectal Boundaries

### 2.1 Sarcastic Inversion and Sub-surface Irony in Romanized Hindi (Hinglish)
- **Symptom:** Utterances where lexical words are superficially polite, flattering, or patriotic, but the intended semantic pragmatics convey targeted harassment or sectarian exclusion.
- **Root Cause:** Sarcasm detection in code-mixed languages requires deep cultural, situational, and historical shared knowledge that cannot be captured purely through bi-directional character/subword n-grams and surface discourse markers.
- **Mitigation:** The system flags ambiguous decision bands (`P(y|x) \in [0.35, 0.65]`) as `NEEDS REVIEW` rather than issuing automated punitive verdicts.

### 2.2 Extreme Phonetic Leetspeak and Obfuscation
- **Symptom:** Highly deformed lexical tokens (e.g., interleaving numerals, Cyrillic homoglyphs, repeated zero-width spaces, or intentional excessive elongation like `v.e.r.r.r.m.i.n`).
- **Observed Behavior:** While the regex normalizer collapses character elongations ($\ge 3$ repeated characters to 1) and translates standard Cyrillic homoglyphs (e.g., `а` $\to$ `a`, `о` $\to$ `o`), highly idiosyncratic spacing (e.g. `v e r m i n`) or phonetic substitutions unfamiliar to the Hinglish vocabulary may escape token-level grounding.

### 2.3 Unsupported Perso-Arabic Script (Urdu)
- **Symptom:** Text written in Arabic/Nastaliq script (`[\u0600-\u06FF]`).
- **Observed Behavior:** The language detector actively identifies Perso-Arabic characters and flags the request as `unsupported_script`, raising a routing note for human reviewer assignment rather than attempting low-confidence transcription.

---

## 3. Multimodal & OCR Boundaries

### 3.1 Low-Contrast, Distorted, or Stylized Meme Typography
- **Symptom:** Text embedded in complex social media memes featuring heavy compression artifacts, watermarks, artistic cursive fonts, or extreme color blends with background imagery.
- **Empirical Failure Rate:** The CRAFT text detector and PyTorch dynamic quantization recognition pipeline achieve $> 92\%$ word-level accuracy on standardized high-contrast meme fonts (e.g., Impact, Arial, Devanagari Unicode), but accuracy drops to $\approx 64\%$ on low-resolution WhatsApp forwards ($< 400\text{px}$) with heavy JPEG compression.
- **Design Safeguard:** The front-end Meme Studio provides an interactive OCR curation interface allowing moderators to edit, delete false-positive noise, or manually insert missed lines before running model inference (`ocr_lines_override`).

### 3.2 Visual Semantic Bias vs. Typographic Modality
- **Symptom:** When a benign background image (e.g., a serene mountain landscape) is paired with a hostile typography overlay, or conversely, a hostile symbol is paired with peaceful text.
- **Empirical Behavior:** The cross-modal attention mechanism successfully identifies `cross_modal_tension` via Shapley decomposition ($\phi_T < 0, \phi_V > 0$). However, because the visual CNN is trained on downscaled representations ($224 \times 224$), high-level cultural symbolism (e.g., obscure political caricatures) is recognized with lower fidelity than explicit typographic slogans.

---

## 4. Contextual Bounds & Discourse Scoping

### 4.1 Strict Context Shifting Cap ($|\Delta z_C| \le 1.0$)
- **Design Choice:** Context is strictly bounded to a maximum logit shift of $\pm 1.0$.
- **Implication:** Direct, unambiguous, and severe dehumanizing slurs (e.g., `vermin`, `parasite`, `gaddar`) generate base text logits $z_T > 2.0$. Even when enclosed in mitigating context (e.g., "Academic curriculum"), the final logit $z = z_T + \Delta z_C$ will not completely drop below zero, ensuring the platform does not enable trivial hate bypass.
- **Boundary:** Long conversation threads with multiple sub-discussions are currently flattened into a single context string; nested conversational trees are not modeled.

---

## 5. Statistical Calibration & Faithfulness

### 5.1 Post-Hoc Calibration Uncertainty
- **Calibration Method:** Temperature scaling with $T = 1.35$ and empirical clamping to $[0.01, 0.99]$.
- **Limitation:** Calibration was fitted on the held-out validation split. On out-of-domain distributions (e.g., gaming chat streams or political manifestos), the Expected Calibration Error (ECE) may exceed the benchmarked $0.042$.

### 5.2 AOPC Token Perturbation Assumption
- **Method:** Faithfulness is scored via Area Over the Perturbation Curve (AOPC), removing tokens in order of descending attribution magnitude.
- **Known Artifact:** Leave-one-out masking may introduce out-of-distribution (OOD) syntactic artifacts into the tokenizer. High AOPC scores indicate model sensitivity to the masked token, but do not prove human-interpretable linguistic causality.

---

## 6. Computational & Latency Footprint

| Component | Target Environment | Mean Latency (Single Request) | Peak Latency (Cold Start / Heavy Image) |
| :--- | :--- | :--- | :--- |
| Text Inference Only | CPU (Intel i7 / AMD Ryzen) | $6 - 12\text{ ms}$ | $25\text{ ms}$ |
| Text Perturbation Attribution (XAI) | CPU | $15 - 35\text{ ms}$ | $60\text{ ms}$ |
| 3-Stream Shapley ($2^3 = 8$ subsets) | CPU | $1.2 - 2.5\text{ ms}$ | $5\text{ ms}$ |
| Full OCR Pipeline (EasyOCR Multi-Pass) | CPU | $450 - 850\text{ ms}$ | $1,200\text{ ms}$ (Initial model load) |
| End-to-End Multimodal Analysis | CPU | $500 - 900\text{ ms}$ | $1,350\text{ ms}$ |

---

## 7. Ethical & Operational Safeguards

1. **No Automated Punitive Enforcement:** This system is engineered as an advisory decision-support instrument for trust and safety analysts. It provides calibrated probabilities, signed evidence rationales, and uncertainty intervals rather than autonomous content removal.
2. **Supervisor Oversight:** Academic implementation executed under the guidance of Dr. Pradeepika Verma, Department of Computer Science & Engineering.
