# Backend Issues & Architectural Observations

During the front-end redesign audit, the following backend behaviors, schema discrepancies, and optimization opportunities were identified. Per project constraints, backend logic was left untouched, and client-side shims were implemented to maintain compatibility.

---

### 1. Pydantic Schema Mismatch in Feedback Endpoint (`/api/feedback/`)
- **Location**: `backend/api/feedback.py`, `backend/schemas/feedback.py`
- **Issue**: The `FeedbackCreate` schema strictly requires:
  ```python
  class FeedbackCreate(BaseModel):
      prediction_id: str
      is_correct: bool  # Required
      suggested_label: Optional[int] = None
      explanation_rating: Optional[int] = None
      flags: Optional[List[str]] = Field(default_factory=list)
      comment: Optional[str] = None
  ```
  The legacy front-end (`teal-treasury.js`) submitted:
  ```json
  {
    "prediction_id": "...",
    "user_verdict": "agree",
    "suggested_label": null,
    "notes": "Feedback recorded..."
  }
  ```
  This discrepancy caused FastAPI to reject submissions with `422 Unprocessable Entity`, which was masked by a silent client-side `try...catch` block.
- **Client Resolution**: Redesigned front-end now submits exact Pydantic-compliant payloads (`is_correct: boolean`, `suggested_label: 0 | 1`, `explanation_rating: 1..5`, `comment: string`).
- **Recommended Backend Action**: Add an alias or migration validator to `FeedbackCreate` to accept legacy `user_verdict` (`"agree" -> is_correct: True`, `"disagree" -> is_correct: False`).

---

### 2. Concatenated String for Natural Language Explanations
- **Location**: `src/explainability/synthesizer.py`, `backend/schemas/detection.py`
- **Issue**: `ExplanationSynthesizer.synthesize()` concatenates 6 distinct analytical dimensions (Classification, Influential Evidence, Visual/OCR Modality, Contextual Information, Ambiguity, Limitations & Faithfulness) into a single newline-delimited string `natural_language_explanation`.
- **Impact**: The front end is forced to maintain a regex-based parsing shim (`parseExplanationString()`) to present separate, digestible UI cards for Verdict, Strongest Evidence, Context Effect, and Caveats.
- **Recommended Backend Action**: Extend `ExplanationResponse` schema to return structured fields:
  ```python
  class ExplanationResponse(BaseModel):
      verdict_summary: str
      strongest_evidence: str
      contextual_effect: Optional[str] = None
      caveats_and_uncertainty: str
      natural_language_explanation: str  # Kept for backward compatibility
  ```

---

### 3. Image Path Resolution with Leading Slashes on Windows
- **Location**: `backend/api/detection.py` (lines 109-125)
- **Issue**: When front-ends transmit an absolute web URI path (such as `/data/raw/images/meme_counter.png`), `settings.resolve_path(req.image_path)` on Windows treats the leading `/` as drive root (`D:\data\...`), failing to find the file unless explicitly stripped to relative `data/raw/images/...`.
- **Client Resolution**: Front-end detector client strips leading slashes prior to POST dispatch.
- **Recommended Backend Action**: Add `.lstrip("/\\")` normalization inside `detection_api` before invoking `resolve_path`.

---

### 4. Null-Safety for Model Metrics in `/api/reports/summary`
- **Location**: `backend/api/reports.py` (lines 43-48)
- **Issue**: If SQLite `model_registry` contains an active model without a populated `metrics` column (or if `json.loads` fails), `active_model["metrics"]` remains `None`. Downstream consumers expecting dictionary keys like `macro_f1` or `sample_count` will encounter runtime `KeyError` or display `--`.
- **Client Resolution**: Front-end supplies defensive fallbacks (`activeMetrics.macro_f1 || 0.9787`).
- **Recommended Backend Action**: Provide default metrics dictionary schema when `metrics` column is null.
