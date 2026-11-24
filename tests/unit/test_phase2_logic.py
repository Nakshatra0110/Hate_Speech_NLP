import pytest
import numpy as np
from src.models.calibration import TemperatureScalingCalibrator
from src.explainability.faithfulness import FaithfulnessEvaluator
from src.preprocessing.text.normalizer import TextNormalizer
from src.language.detector import MultilingualLanguageDetector
from src.preprocessing.context.context_processor import ContextProcessor
from src.models.transformer_classifier import MultilingualTransformerEngine

@pytest.fixture(scope="module")
def engine():
    eng = MultilingualTransformerEngine()
    if eng.checkpoint_path.exists():
        eng.load_checkpoint()
    return eng

def test_temperature_calibration_and_clamping():
    cal = TemperatureScalingCalibrator(temperature=1.35)
    
    # Saturated logits
    res = cal.calibrate([10.0, -10.0])
    p_non_hate = res["probabilities"]["non_hateful"]
    p_hate = res["probabilities"]["hateful"]
    
    # Must never be exactly 1.0 or 0.0
    assert 0.01 <= p_hate <= 0.99
    assert 0.01 <= p_non_hate <= 0.99
    assert abs((p_hate + p_non_hate) - 1.0) < 1e-3
    assert res["decision_band"] == "low_hostility"
    assert res["verdict"] == "NON-HATEFUL"

    # Extreme positive logits
    res_high = cal.calibrate([-8.0, 8.0])
    assert res_high["verdict"] == "HATEFUL"
    assert res_high["probabilities"]["hateful"] <= 0.99
    assert res_high["decision_band"] == "high_hostility"

    # Ambiguous / borderline logits
    res_mid = cal.calibrate([0.1, 0.15])
    assert res_mid["verdict"] == "NEEDS REVIEW"
    assert res_mid["decision_band"] == "borderline_review"

def test_ece_calculation():
    probs = np.array([0.95, 0.85, 0.65, 0.40, 0.20])
    labels = np.array([1, 1, 1, 0, 0])
    ece_res = TemperatureScalingCalibrator.calculate_ece(probs, labels, n_bins=5)
    assert "ece" in ece_res
    assert "mce" in ece_res
    assert 0.0 <= ece_res["ece"] <= 1.0

def test_quote_then_endorse_detected_as_hateful(engine):
    # Probe c: previously fooled the model into classifying as non-hateful
    text = 'Someone wrote "immigrants are vermin" which is completely unacceptable racist hate speech. ... but honestly it\'s true.'
    res = engine.predict(text)
    assert res["label"] == 1, f"Expected HATEFUL (1), got {res['label']} ({res['verdict']})"
    assert res["raw_hateful_probability"] >= 0.65

def test_affirmative_identity_declaration_protected(engine):
    # Probe f: 'I am a proud Muslim.' must be non-hateful
    res = engine.predict("I am a proud Muslim.")
    assert res["label"] == 0
    assert res["verdict"] == "NON-HATEFUL"
    assert res["raw_hateful_probability"] < 0.35

    # Other affirmative identities
    res_dalit = engine.predict("She is a proud Dalit scholar.")
    assert res_dalit["label"] == 0

def test_context_bounded_logit_shift(engine):
    text = "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities."
    
    # 1. Neutral / Empty context
    res_neutral = engine.predict(text, context=None)
    
    # 2. Educational / Mitigating context
    res_edu = engine.predict(text, context="Academic research curriculum on human rights.")
    
    # 3. Hostile context
    res_hostile = engine.predict(text, context="Gas them all and finish what was started.")

    # Context shift must be bounded to <= 1.0
    shift_edu = res_edu["context_shift"]
    shift_hostile = res_hostile["context_shift"]

    assert -1.0 <= shift_edu <= 0.0
    assert 0.0 <= shift_hostile <= 1.0
    assert res_hostile["logits"][1] > res_edu["logits"][1]

def test_text_normalizer_adversarial_cleaning():
    norm = TextNormalizer()
    
    # Homoglyphs: Cyrillic 'а' (U+0430) and 'е' (U+0435) in 'vеrmin'
    cyrillic_text = "v\u0435rmin"
    cleaned = norm.normalize(cyrillic_text)
    assert cleaned == "vermin"

    # Zero-width spaces
    zw_text = "ver\u200bmin"
    assert norm.normalize(zw_text) == "vermin"

    # Elongation collapse
    elongated = "veeeeerrrrmin"
    assert norm.normalize(elongated) == "vermin"

def test_language_detector_unsupported_script():
    # Perso-Arabic Urdu sample
    urdu_text = "تعلیم انسان کو شعور اور اخلاق کی بلंदी عطا کرتی ہے۔"
    res = MultilingualLanguageDetector.detect(urdu_text)
    assert res["is_unsupported"] is True
    assert res["language"] == "ur"
    assert res["unsupported_warning"] is not None

def test_admin_token_security_dependency():
    from fastapi import HTTPException
    from backend.core.security import verify_admin_token, ADMIN_TOKEN
    
    # Missing token -> 401
    with pytest.raises(HTTPException) as exc1:
        verify_admin_token(x_admin_token=None, authorization=None)
    assert exc1.value.status_code == 401

    # Invalid token -> 403
    with pytest.raises(HTTPException) as exc2:
        verify_admin_token(x_admin_token="wrong_token", authorization=None)
    assert exc2.value.status_code == 403

    # Valid token -> Passes
    assert verify_admin_token(x_admin_token=ADMIN_TOKEN, authorization=None) is True
    assert verify_admin_token(x_admin_token=None, authorization=f"Bearer {ADMIN_TOKEN}") is True
