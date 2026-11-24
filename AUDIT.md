# Comprehensive System Audit: HateLess Codebase & Detection Logic

**Audit Date**: November 24, 2026  
**Auditor**: Senior ML Engineer & Product Designer  
**Repository**: `Nakshatra0110/Hate_Speech_NLP`  
**Supervision Reference**: Academic Project for CSET-346 (Academic Supervisor: Dr. Pradeepika Verma)  
**Active Working Branch**: `feature/logic-ocr-ux`  

---

## Executive Summary

A comprehensive pre-flight investigation of the HateLess platform was conducted across the front-end, API routing, multilingual text classifier, multimodal fusion, OCR pipeline, and explainability subsystems.

While the project features a well-conceived architecture combining text, vision, and context ($x_i = \{T_i, V_i, C_i\}$), empirical probing revealed critical systemic failures:
1. **Rule-overridden classifier**: The "Multilingual Transformer" is actually a BiLSTM with self-attention whose predictions are hard-overridden by arbitrary regex heuristic shifts ($\Delta z = +3.8$ / $-2.5$), causing saturated softmax probabilities ($1.0000$ or $0.0000$).
2. **Context Disconnection**: Context strings ($C_i$) are parsed by `ContextProcessor` but **never passed into the inference model** in `backend/api/detection.py`, having literally $0.0$ impact on prediction probabilities.
3. **Untrained Visual Fusion**: The visual fusion model (`MultimodalDetector`) runs uninitialized random weights, generating ~0.50 noise that is arbitrarily blended ($70\% / 30\%$) with text probabilities.
4. **Bypassed OCR**: `OCRService` checked incoming filenames against a static dictionary of 10 benchmark memes (`BENCHMARK_MEME_CATALOG`). When arbitrary images were uploaded without pre-cached EasyOCR weights or on Windows OpenMP collisions, it returned empty text (`""`).
5. **False Benchmark Perfection**: Benchmarks reported 100% Macro-F1 and 0.000 Equalized Odds Gap due to evaluated synthetic and non-heldout samples.
6. **Hallucinated Attributes & Artifacts**: The UI displayed fabricated quotes attributed to Dr. Pradeepika Verma, uncalibrated "HIGH CERTAINTY (CALIBRATED)" badges, and hard-coded latency figures ($8.4\text{ ms}$, $18.8\text{ ms}$).

---

## 1. Full Code Path Trace (Request Lifecycle)

```
[Browser Client]
  │
  ├── POST /api/detection/detect {text, image_base64, context, explain: true}
  ▼
[backend/api/detection.py]
  │
  ├── 1. Text Normalization: src/preprocessing/text/normalizer.py (NFKC, regex cleaning)
  ├── 2. Language ID: src/language/detector.py (Script detection + Hinglish lexicon)
  ├── 3. Context Processing: src/preprocessing/context/context_processor.py
  │      └── NOTE: ctx_info is generated, BUT NEVER PASSED TO PREDICT()!
  ├── 4. Visual Preprocessing: src/preprocessing/image/image_preprocessor.py
  │      └── Resizes array to [224, 224, 3]
  ├── 5. OCR Extraction: src/multimodal/ocr.py
  │      ├── Intercepts filename in BENCHMARK_MEME_CATALOG (catalog lookup)
  │      └── EasyOCR fallback (fails if EasyOCR uninstalled or OpenMP collision)
  ├── 6. Inference: src/models/transformer_classifier.py (predict())
  │      ├── BiLSTM + Multihead Self-Attention forward pass -> [z0, z1]
  │      └── Regex override: if has_slur: z1 = max(z1, z0 + 3.8)
  ├── 7. Visual Fusion: src/multimodal/fusion.py
  │      └── Untrained Conv2D fusion network: fused_p = 0.70 * p_text + 0.30 * p_mm
  ├── 8. Explainability:
  │      ├── TextAttributionEngine (src/explainability/text_attribution.py): Leave-one-out
  │      ├── VisualAttributionEngine: Maps OCR boxes to token attributions
  │      └── ExplanationSynthesizer (src/explainability/synthesizer.py): Formats 6 points
  └── 9. DB Persistence: SQLite insert into predictions table
```

---

## 2. Empirical Pre-Flight Probe Results (Probes a–j)

All probes were executed against the active classifier checkpoint (`models/checkpoints/multilingual_transformer.pt`) using the existing pipeline.

| Probe ID | Input Text | Context | Label | $P(\text{Hate})$ | Confidence | Raw Logits $[z_0, z_1]$ | Latency | Faithfulness (AOPC) | Key Token Highlights |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **a** | `immigrants are vermin` | None | **HATEFUL** | `1.0000` | `1.0000` | $[-11.71, +5.11]$ | 15.6 ms | 1.000 | `vermin` (+0.818), `immigrants` (+0.000) |
| **b** | `Someone wrote "immigrants are vermin" which is completely unacceptable racist hate speech.` | None | **NON-HATEFUL** | `0.0058` | `0.9942` | $[+1.04, -4.11]$ | 2.15 ms | 1.000 | `wrote` (+0.002), `are` (+0.003) |
| **c** | `Someone wrote "immigrants are vermin" which is completely unacceptable racist hate speech. ... but honestly it's true.` | None | **NON-HATEFUL** *(FAILURE)* | `0.0055` | `0.9945` | $[+1.05, -4.15]$ | 3.12 ms | 1.000 | **Model fooled!** `unacceptable` triggered condemnation regex, ignoring `honestly it's true`. |
| **d** | `ye log desh ke gaddar hai` | None | **HATEFUL** | `1.0000` | `1.0000` | $[-8.47, +3.72]$ | 2.10 ms | 1.000 | `gaddar` (+0.818), `ye` (+0.010) |
| **e** | `ये लोग देश के गद्दार हैं` | None | **HATEFUL** | `1.0000` | `1.0000` | $[-16.25, +7.15]$ | 1.80 ms | 1.000 | `गद्दार` (+0.818), `लोग` (+0.000) |
| **f** | `I am a proud Muslim.` | None | **NON-HATEFUL** | `0.1822` | `0.8178` | $[+0.28, -1.22]$ | 1.60 ms | 0.028 | False attribution: `Muslim` (+0.074) & `proud` (+0.074) flagged as hate-increasing! |
| **g** | `In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.` | Academic curriculum | **NON-HATEFUL** | `0.0000` | `1.0000` | $[+2.12, -8.36]$ | 1.48 ms | 0.308 | `historical` (-0.002), `propaganda` (-0.002); `subhuman` and `dehumanize` unmarked! |
| **h1** | *(Same as g)* | None | **NON-HATEFUL** | `0.0000` | `1.0000` | $[+2.12, -8.36]$ | 2.29 ms | 0.308 | Identical to g (Context has 0.0 effect). |
| **h2** | *(Same as g)* | Hostile context | **NON-HATEFUL** | `0.0000` | `1.0000` | $[+2.12, -8.36]$ | 3.86 ms | 0.308 | Identical to g (Hostile context ignored by model). |
| **i1** | `propaganda used terms like 'subhuman' to systematically dehumanize communities.` | None | **NON-HATEFUL** | `0.0587` | `0.9413` | $[+0.55, -2.22]$ | 5.20 ms | 1.000 | `propaganda` (-0.352), `subhuman` (+0.016). |
| **i2** | `subhuman dehumanize communities` | None | **NON-HATEFUL** *(FAILURE)* | `0.2803` | `0.7197` | $[+0.19, -0.75]$ | 2.26 ms | 1.000 | Direct severe dehumanization missed because framing words were removed. |

### Probe j: OCR Evaluation on 10 Real Memes (`data/raw/images/`)

| Meme Image | Catalog Output (Hardcoded Bypassed) | Actual EasyOCR Raw Output (Without Catalog) | Assessment |
|:---|:---|:---|:---|
| `meme_caste.png` | `KNOW YOUR PLACE AT THE BOTTOM UNCLEAN CASTE` | `KNONYOURPUCEAT THEBDTTON UNCLEANCASTE` | Spacing loss, character degradation (`KNOW` $\to$ `KNON`, `BOTTOM` $\to$ `BDTTON`). |
| `meme_counter.png` | `NO ROOM FOR RACISM EQUALITY FOR ALL` | `NO ROONIFORRACISM EOUALITYFORALL` | Word concatenation, character swap (`ROOM` $\to$ `ROON`, `EQUALITY` $\to$ `EOUALITY`). |
| `meme_cricket.png` | `DESH KI SHAAN TEAMWORK AND PASSION` | `DESH KI SHAAN TEANNORK AlID PASSION` | Partial word separation, `M` misclassified as `NN`. |
| `meme_education.png` | `READ BOOKS NOT HATE KNOWLEDGE EMPOWERS` | `READ BOKSNOT HATE KNIOLEDGEENPDNERS` | Concatenation, character corruption. |
| `meme_kindness.png` | `KINDNESS IS CONTAGIOUS PASS IT ON` | `KINDNESSISCONTAGIOUS PASSITON` | Space collapse across words. |
| `meme_misogyny.png` | `PROPERTY NOT LEADERS SILENCE THEM ALL` | `PROPERTYNOT LEDERS SILENCETHEI ALL` | Concatenation, vowel drops (`LEADERS` $\to$ `LEDERS`). |
| `meme_parasite.png` | `PARASITES INFESTING OUR NATION EXTERMINATE THEM` | `PARASITESINFESTING OUR NATION DTERNIINITETHEN` | Severe corruption of `EXTERMINATE THEM`. |
| `meme_teamwork.png` | `TOGETHER WE ACHIEVE MORE UNITY IN DIVERSITY` | `TOGETHER E:CHIBE MORE UNITYINDIERSITY` | Garbled phrase `ACHIEVE` $\to$ `E:CHIBE`. |
| `meme_vermin.png` | `SUBHUMAN VERMIN GET OUT OF OUR LAND` | `SUBHUIANVERIIIN GETOUTOFOURLAND` | Concatenation, `M` misread as `III` / `UIAN`. |
| `meme_violence.png` | `TIME TO TAKE UP WEAPONS NO MERCY FOR TRAITORS` | `TINETO TAKEUP WEiFONS NO IERDY FOR TRAITORS` | Character substitutions (`TIME` $\to$ `TINETO`, `WEAPONS` $\to$ `WEiFONS`). |

**Conclusion on OCR**: `BENCHMARK_MEME_CATALOG` masked major OCR degradation on noisy font and meme artifacts. EasyOCR requires image contrast enhancement, adaptive thresholding, multi-scale CLAHE, and spacing restoration.

---

## 3. Detailed Answers to Audit Questions (With Code Evidence)

### 3.1. Is the "multilingual transformer" really BiLSTM + self-attention?
* **Evidence**: [src/models/transformer_classifier.py#L13-L23](file:///d:/Coding/Hate_Speech_NLP/src/models/transformer_classifier.py#L13-L23)
```python
class MultilingualAttentionClassifier(nn.Module):
    def __init__(self, vocab_size: int = 15000, embed_dim: int = 128, hidden_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = nn.MultiheadAttention(embed_dim=hidden_dim * 2, num_heads=4, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.dropout = nn.Dropout(0.3)
        self.fc_out = nn.Linear(64, num_classes)
```
* **Findings**: Yes, it is strictly a **BiLSTM with 4-head self-attention**, not a transformer encoder (e.g. BERT/RoBERTa/XLM-R).
* **Training Data**: Trained on `hasoc_hi_en.jsonl` (840 samples) and `subtle_structural_benchmark.jsonl` (210 samples), totaling 1,050 samples.
* **Splits**: Stratified 70/15/15 split via `src/data/splitter.py`. However, vocabulary construction (`build_vocab`, line 64) injects Hinglish lexicon counts artificially (+5), and `predict()` overwrites network logits with regex matching.

### 3.2. Is the "LLM reasoner" a template or an actual model?
* **Evidence**: [src/models/llm_reasoner.py#L71-L150](file:///d:/Coding/Hate_Speech_NLP/src/models/llm_reasoner.py#L71-L150)
* **Findings**: It is **100% a rule-based template engine**. It constructs an internal prompt string (`construct_prompt`), but does not call any LLM, API, or local transformer model. It executes hardcoded list lookups (`hate_lexicon = [...]`) and returns static strings wrapped in an `LLMAnalysisResult` Pydantic model.

### 3.3. Is the "Deep Conv2D visual fusion" trained on real images or synthetic ones? Does $V$ actually change the output?
* **Evidence**: [src/multimodal/fusion.py#L10-L40](file:///d:/Coding/Hate_Speech_NLP/src/multimodal/fusion.py#L10-L40) and [backend/api/detection.py#L35,L174-L185](file:///d:/Coding/Hate_Speech_NLP/backend/api/detection.py#L35)
* **Findings**:
  - `_multimodal_detector = MultimodalDetector(dim=128, text_in_dim=256)` is instantiated with **randomly initialized PyTorch weights**.
  - There is **no checkpoint file** for visual fusion anywhere in `models/checkpoints/` (only `classical_baseline.joblib` and `multilingual_transformer.pt` exist).
  - When test text was run with 3 radically different images (`meme_counter`, `meme_vermin`, `meme_kindness`), the visual network output $P_{\text{visual}}(\text{hate})$ was $0.5044$, $0.4983$, and $0.5116$ respectively—strictly uninformative random Gaussian noise!
  - Yet in `backend/api/detection.py` line 182, this random noise was blended:
    `fused_prob = round(0.70 * pred_res["raw_hateful_probability"] + 0.30 * p_mm_hate, 4)`
    This shifted honest predictions arbitrarily toward 0.15–0.50!

### 3.4. Does $C$ (context) change the output?
* **Evidence**: [backend/api/detection.py#L102-L105,L170-L194](file:///d:/Coding/Hate_Speech_NLP/backend/api/detection.py#L102-L105)
* **Findings**: In the active backend, **context has 0.0 impact**. While `_context_proc.process(req.context)` was called to check `has_context`, the returned context object was **never passed into `transformer_clf.predict()`**! The model received solely `full_text`. Context was passed only into the explanation generator for narrative text rendering. Probes `g`, `h1`, and `h2` confirmed identical probabilities down to the fourth decimal place ($0.0000$).

### 3.5. How is the 100% confidence / "calibrated" label produced?
* **Evidence**: [src/models/transformer_classifier.py#L418-L434](file:///d:/Coding/Hate_Speech_NLP/src/models/transformer_classifier.py#L418-L434)
* **Findings**: Saturated probability. If a word matches `EXPLICIT_SLURS`, the logit is overridden with:
  `z1 = max(z1, z0 + 3.8)`
  Softmax over $[-11.7, +5.1]$ yields $1.0000000$. The "HIGH CERTAINTY (CALIBRATED)" label was simply a client-side formatting rule in the front-end triggering whenever `confidence >= 0.90`. No Platt scaling, isotonic regression, or temperature scaling was present.

### 3.6. Where do the numbers 8.4 ms, 18.8 ms, 130 ms, AOPC 0.308 vs 1.0 come from?
* **Evidence**:
  - `8.4 ms`: Hardcoded string in legacy `README.md` and documentation tables.
  - `18.8 ms`: Hardcoded in `presentation/generate_presentation.py`.
  - `130 ms`: Legacy UI static mockup text in HTML.
  - Actual measured CPU inference latency is $\sim 1.5\text{ ms}$ for model forward pass and $\sim 15\text{ ms}$ for complete leave-one-out attribution.
  - `AOPC = 1.0 vs 0.308`: In `src/explainability/text_attribution.py` line 92, when prob deltas saturated at zero, it artificially capped faithfulness at $1.0$. However, on non-saturated probes (Probe g), the formula computed $0.3076$. The UI ablation card hardcoded $1.0$.

---

## 4. Confirmation / Refutation of Known Symptoms

| Symptom | Status | Exact Root Cause & File Location |
|:---|:---:|:---|
| Confidence 100%, $P=1.0000$, "HIGH CERTAINTY (CALIBRATED)" | **Confirmed** | Softmax saturation via manual logit shift (`z1 = max(z1, z0 + 3.8)`) in [src/models/transformer_classifier.py#L419](file:///d:/Coding/Hate_Speech_NLP/src/models/transformer_classifier.py#L419). |
| Heatmap leaves "subhuman" unmarked, highlights "historical" | **Confirmed** | Leave-one-out on saturated $P=1.0000$ yields $\Delta P = 0$. Logit-fallback used relative shifts that normalized uninformative framing words. |
| AOPC shows 0.308 in studio, 1.0 in ablation card | **Confirmed** | Studio calculated live AOPC on probe g ($0.3076$), whereas markdown cards hardcoded `1.0`. |
| Explanation text garbled ("Classification: Classification:") | **Confirmed** | [src/explainability/synthesizer.py#L23](file:///d:/Coding/Hate_Speech_NLP/src/explainability/synthesizer.py#L23) outputs `"1. Classification: ..."`, and legacy UI JS prepended `"Classification: "` again. |
| Fabricated Dr. Verma quote in UI | **Confirmed** | Legacy `index.html` contained a hardcoded quote banner praising the system. |
| Raw LaTeX leaking in footer (`$y \in \{0,1\}$`) | **Confirmed** | Plain text string with unparsed math tokens in `index.html`. |
| Unauthenticated destructive endpoints (`/api/experiments/reset`) | **Confirmed** | [backend/api/experiments.py](file:///d:/Coding/Hate_Speech_NLP/backend/api/experiments.py) endpoints had no API key or admin token dependencies. |
| 100% Macro-F1 / 0.000 Equalized Odds Gap | **Confirmed** | Benchmarks evaluated synthetic and leaked training records without true held-out adversarial splits. |

---

## 5. Strategic Correction Plan for Phases 1–6

1. **Phase 1 (Harness & Fixtures)**: Build `tests/adversarial_heldout.jsonl` ($\ge 200$ samples) with quote-then-endorse, sarcasm, negation, and reclaimed slurs. Add 50-sentence language ID set and 10 meme fixtures.
2. **Phase 2 (Logic & Calibration)**: Implement post-hoc temperature scaling in `src/models/calibration.py` with ECE validation. Compute attribution on logits $z$, not saturated $p$. Feed context representation into inference with bounded effect ($\le \pm 1.0$ logits). Secure destructive endpoints with an admin token check.
3. **Phase 3 (Robust OCR)**: Replace catalog shortcuts in `src/multimodal/ocr.py` with multi-variant EasyOCR (CLAHE, thresholding, scale normalization, reading-order box sorting), returning line-level normalized coordinates. Expose `POST /api/detection/ocr` and support `ocr_lines_override`.
4. **Phase 4 (Three-Stream $x_i = \{T_i, V_i, C_i\}$ Shapley)**: Implement exact Shapley decomposition over $2^3 = 8$ subsets on the logit scale: $\phi_T + \phi_V + \phi_C = z(T,V,C) - z(\emptyset)$. Expose structured API v2 schema.
5. **Phase 5 (Front-End Studio Rebuild)**: Complete Cloudflare-styled interface with side-by-side stream cards, contribution waterfall, 5-step stepper, interactive OCR bounding boxes with click-to-edit, and DPO feedback form.
6. **Phase 6 (Academic Deliverables)**: Update `paper/main.tex`, `presentation/` slides, `README.md`, and `KNOWN_LIMITATIONS.md` with honest empirical metrics.

---
*Signed by Lead Auditor & ML Engineer*
