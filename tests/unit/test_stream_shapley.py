import pytest
import math
from src.explainability.stream_shapley import StreamShapleyExplainer
from backend.schemas.detection import DetectionRequest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_stream_shapley_efficiency_synthetic():
    """
    Test exact Shapley efficiency:
    phi_T + phi_V + phi_C = z(1,1,1) - z(0,0,0)
    holds with tolerance < 1e-6.
    """
    # Define a non-linear arbitrary mock function with complex cross-stream interactions
    def mock_eval_fn(t: str, v: str, c: dict) -> float:
        z = -0.5
        if t:
            z += 2.0
        if v:
            z += 1.5
        if c:
            z -= 0.8
        # Non-linear interaction between T and V
        if t and v:
            z += 0.4
        # Non-linear interaction between T and C
        if t and c:
            z -= 0.6
        return float(z)

    text = "Hostile slur text"
    ocr_text = "Hate meme banner"
    context = {"has_context": True, "context_framing": "counterspeech_quote"}

    res = StreamShapleyExplainer.compute_shapley_streams(
        text=text,
        eval_fn=mock_eval_fn,
        ocr_text=ocr_text,
        context_data=context
    )

    streams = res["shapley_streams"]
    phi_t = streams["phi_T"]
    phi_v = streams["phi_V"]
    phi_c = streams["phi_C"]
    z_base = streams["baseline_z"]
    z_final = streams["final_z"]
    sum_phi = streams["sum_check"]
    gap = streams["efficiency_gap"]

    assert gap < 1e-6, f"Efficiency gap {gap} exceeds 1e-6"
    assert math.isclose(phi_t + phi_v + phi_c, z_final - z_base, abs_tol=1e-6)

    # Check waterfall
    waterfall = res["waterfall"]
    assert len(waterfall) == 4
    assert waterfall[0]["name"] == "Prior Baseline z(∅)"
    assert waterfall[3]["cumulative_z"] == round(z_final, 4)
    for step in waterfall:
        assert 0.0 <= step["probability"] <= 1.0

def test_stream_agreement_cross_modal_tension():
    def tension_eval_fn(t: str, v: str, c: dict) -> float:
        z = 0.0
        if t:
            z -= 1.8 # Mitigating text
        if v:
            z += 2.2 # Hostile visual
        return z

    res = StreamShapleyExplainer.compute_shapley_streams(
        text="Peaceful unity slogan",
        eval_fn=tension_eval_fn,
        ocr_text="Nazi symbol and hate slur"
    )

    assert res["stream_agreement"] == "cross_modal_tension"
    assert res["shapley_streams"]["phi_T"] < 0
    assert res["shapley_streams"]["phi_V"] > 0

def test_stream_agreement_context_mitigated():
    def context_mitigated_eval_fn(t: str, v: str, c: dict) -> float:
        z = 0.0
        if t:
            z += 2.0
        if c:
            z -= 1.2
        return z

    res = StreamShapleyExplainer.compute_shapley_streams(
        text="Historical quote mentioning slur",
        eval_fn=context_mitigated_eval_fn,
        context_data={"has_context": True, "context_framing": "academic_research"}
    )

    assert res["stream_agreement"] == "context_mitigated"
    assert res["shapley_streams"]["phi_T"] > 0
    assert res["shapley_streams"]["phi_C"] < 0

def test_api_detection_v2_response_structure():
    """Verify that POST /api/detection/detect and detect-v2 return the complete v2 schema."""
    payload = {
        "text": "Someone wrote 'immigrants are vermin' which is unacceptable racist hate speech.",
        "context": {
            "thread_history": ["Discussion on civil rights and hate speech laws"],
            "platform": "twitter",
            "post_type": "quote"
        },
        "explain": True
    }

    resp = client.post("/api/detection/detect-v2", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "prediction_id" in data
    assert "verdict" in data
    assert "timing_ms" in data
    assert "total_ms" in data["timing_ms"]
    assert data["timing_ms"]["total_ms"] > 0

    expl = data["explanation"]
    assert expl is not None
    assert "formal_input" in expl
    assert expl["formal_input"]["T"] != ""
    assert "shapley_streams" in expl
    assert "phi_T" in expl["shapley_streams"]
    assert "phi_V" in expl["shapley_streams"]
    assert "phi_C" in expl["shapley_streams"]
    assert "waterfall" in expl
    assert len(expl["waterfall"]) == 4

    steps = expl["steps"]
    assert len(steps) == 5
    step_titles = [s["title"] for s in steps]
    assert any("Classification" in t for t in step_titles)
    assert any("Stream Decomposition" in t for t in step_titles)
    assert any("Dominant Tokens" in t for t in step_titles)
    assert any("Interactions" in t for t in step_titles)
    assert any("Faithfulness" in t for t in step_titles)
