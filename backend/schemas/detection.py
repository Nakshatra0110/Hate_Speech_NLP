from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class ContextInput(BaseModel):
    thread_history: Optional[List[str]] = Field(default=None, description="Previous messages in thread")
    platform: Optional[str] = Field(default=None, description="Origin platform e.g. twitter, reddit")
    post_type: Optional[str] = Field(default=None, description="Direct post, reply, or quote")

class OCRLine(BaseModel):
    text: str
    confidence: float
    script: str = "Latin"
    box_px: Optional[List[Union[int, float]]] = None # [ymin, xmin, ymax, xmax]
    box_norm: Optional[List[float]] = None # [ymin/H, xmin/W, ymax/H, xmax/W] in [0, 1]
    low_confidence: bool = False

class OCRRequest(BaseModel):
    image_path: Optional[str] = Field(default=None, description="Server image path")
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded image string")

class OCRResponse(BaseModel):
    status: str = Field(..., description="'ok', 'no_text_found', 'ocr_unavailable', 'ocr_timeout', 'invalid_image'")
    extracted_text: str
    confidence: float
    lines: List[OCRLine] = []
    image_dimensions: Optional[Dict[str, int]] = None
    engine: str

class DetectionRequest(BaseModel):
    text: Optional[str] = Field(default="", max_length=1000, description="Post text (max 1000 characters)")
    image_path: Optional[str] = Field(default=None, description="Optional path or filename of uploaded meme/image")
    image_base64: Optional[str] = Field(default=None, description="Optional base64 image data")
    ocr_text: Optional[str] = Field(default=None, description="Optional manual or overridden OCR typography text")
    ocr_lines_override: Optional[List[OCRLine]] = Field(default=None, description="User-curated or overridden OCR line objects")
    context: Optional[Union[ContextInput, str, Dict[str, Any]]] = Field(default=None, description="Optional conversation context")
    model_id: Optional[str] = Field(default=None, description="Model to use (defaults to active model)")
    explain: bool = Field(default=True, description="Whether to compute explainability attribution")

class TokenAttribution(BaseModel):
    token: str
    score: float
    polarity: str # "positive_evidence" (pushes toward hate) or "negative_evidence" (pushes toward non-hate)

class VisualAttribution(BaseModel):
    box: Optional[List[int]] = None # [ymin, xmin, ymax, xmax]
    box_norm: Optional[List[float]] = None
    region_label: Optional[str] = None
    attribution_score: float = 0.0

class FormalInput(BaseModel):
    T: str = Field(..., description="Linguistic text content")
    V: Dict[str, Any] = Field(default_factory=dict, description="Visual typography & features")
    C: Dict[str, Any] = Field(default_factory=dict, description="Contextual conversation & framing")

class ShapleyStreams(BaseModel):
    phi_T: float = Field(..., description="Shapley attribution of text stream")
    phi_V: float = Field(..., description="Shapley attribution of visual stream")
    phi_C: float = Field(..., description="Shapley attribution of context stream")
    baseline_z: float = Field(..., description="Neutral baseline logit z(∅)")
    final_z: float = Field(..., description="Final output logit z(T, V, C)")
    sum_check: float = Field(..., description="Sum of phi_i values")
    efficiency_gap: float = Field(default=0.0, description="Absolute difference |sum(phi) - delta_z| (< 1e-6)")

class WaterfallStep(BaseModel):
    step_index: int
    name: str
    stream: str # "baseline", "text", "visual", "context"
    delta_z: float
    cumulative_z: float
    probability: float

class ExplanationStep(BaseModel):
    step: int
    title: str
    body: str
    detail: Optional[str] = None

class ExplanationResponse(BaseModel):
    token_attributions: List[TokenAttribution] = []
    visual_attributions: List[VisualAttribution] = []
    ocr_evidence: Optional[str] = None
    contextual_evidence: Optional[Dict[str, Any]] = None
    natural_language_explanation: str
    faithfulness_score: float # AOPC faithfulness metric
    uncertainty_notes: Optional[str] = None
    formal_input: Optional[FormalInput] = None
    shapley_streams: Optional[ShapleyStreams] = None
    stream_agreement: Optional[str] = "concordant"
    steps: Optional[List[ExplanationStep]] = []
    waterfall: Optional[List[WaterfallStep]] = []

class DetectionResponse(BaseModel):
    prediction_id: str
    predicted_label: int = Field(..., description="0 for Non-Hateful, 1 for Hateful")
    label_name: str = Field(..., description="'NON-HATEFUL', 'HATEFUL', or 'NEEDS REVIEW'")
    confidence: float
    verdict: Optional[str] = None
    decision_band: Optional[str] = None
    probabilities: Optional[Dict[str, float]] = None
    logits: Optional[List[float]] = None
    model_id: str
    model_version: str
    language_detected: str
    modalities_used: List[str]
    explanation: Optional[ExplanationResponse] = None
    timing_ms: Optional[Dict[str, float]] = None
    created_at: str
