import json
import os
import pytest
from pathlib import Path
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix

from backend.core.config import settings
from src.models.transformer_classifier import MultilingualTransformerEngine

@pytest.fixture(scope="module")
def adversarial_data():
    base_dir = Path(__file__).resolve().parent.parent
    adv_file = base_dir / "tests" / "adversarial_heldout.jsonl"
    assert adv_file.exists(), f"Missing {adv_file}"
    records = []
    with open(adv_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

@pytest.fixture(scope="module")
def language_id_data():
    base_dir = Path(__file__).resolve().parent.parent
    lang_file = base_dir / "tests" / "fixtures" / "language_id_samples.json"
    assert lang_file.exists(), f"Missing {lang_file}"
    return json.loads(lang_file.read_text(encoding="utf-8"))

def test_adversarial_heldout_dataset_integrity(adversarial_data):
    assert len(adversarial_data) >= 200, f"Expected >= 200 samples, got {len(adversarial_data)}"
    subcats = set(r["subcategory"] for r in adversarial_data)
    expected_subcats = {
        "direct_hate", "counterspeech", "quote_then_endorse",
        "embedded_negation", "sarcastic_counterspeech",
        "identity_declaration", "reclaimed_terms",
        "historical_mention", "subtle_structural_hate",
        "civil_discourse"
    }
    assert expected_subcats.issubset(subcats), f"Missing subcategories: {expected_subcats - subcats}"
    
    # Class balance check
    labels = [r["label"] for r in adversarial_data]
    hateful_count = labels.count(1)
    non_hateful_count = labels.count(0)
    assert hateful_count >= 80, f"Too few hateful samples: {hateful_count}"
    assert non_hateful_count >= 80, f"Too few non-hateful samples: {non_hateful_count}"

def test_language_id_fixtures_integrity(language_id_data):
    assert len(language_id_data) >= 50, f"Expected >= 50 samples, got {len(language_id_data)}"
    langs = set(r["expected_language"] for r in language_id_data)
    assert {"en", "hi", "Hinglish"}.issubset(langs)
