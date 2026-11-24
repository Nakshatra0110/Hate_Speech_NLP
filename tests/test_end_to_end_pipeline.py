import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app
from src.preprocessing.nlp_pipeline import NLPPipeline
from src.models.transformer_classifier import MultilingualTransformerEngine
from src.explainability.text_attribution import TextAttributionEngine


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def nlp():
    return NLPPipeline()


@pytest.fixture(scope="module")
def engine():
    return MultilingualTransformerEngine()


@pytest.fixture(scope="module")
def xai():
    return TextAttributionEngine()


# ==============================================================================
# 1. NLP Pipeline: Lemmatization, Tokenization & Stopword Tests
# ==============================================================================

def test_nlp_english_lemmatization(nlp):
    text = "These disgusting immigrants are infecting countries and running away."
    res = nlp.process_text(text)
    
    assert res["language"] == "en"
    assert len(res["tokens"]) > 0
    assert len(res["lemmas"]) == len(res["tokens"])
    
    # Check morphological lemmatization
    tok_to_lemma = dict(zip(res["tokens"], res["lemmas"]))
    assert tok_to_lemma.get("immigrants") == "immigrant"
    assert tok_to_lemma.get("infecting") == "infect"
    assert tok_to_lemma.get("countries") == "country"
    assert tok_to_lemma.get("running") == "run"
    
    # Stopwords should be removed from clean_tokens_no_stopwords
    clean = res["clean_tokens_no_stopwords"]
    assert "are" not in clean
    assert "and" not in clean
    assert "immigrant" in clean
    assert "infect" in clean


def test_nlp_hindi_morphological_lemmatization(nlp):
    text = "हमारे भाईचारे और शांति को नफरत फैलाने वाले खत्म नहीं कर सकते।"
    res = nlp.process_text(text)
    
    assert res["language"] == "hi"
    assert len(res["tokens"]) > 0
    assert len(res["lemmas"]) == len(res["tokens"])
    
    # Suffix stripping on inflected Hindi words
    tok_to_lemma = dict(zip(res["tokens"], res["lemmas"]))
    assert tok_to_lemma.get("भाईचारे") == "भाईचारा"
    assert "नहीं" not in res["clean_tokens_no_stopwords"] or "शांति" in res["clean_tokens_no_stopwords"]


def test_nlp_hinglish_lemmatization(nlp):
    text = "In chutiyon ko desh se bahar phenko aur sab gaddaron ko roko."
    res = nlp.process_text(text)
    
    assert res["language"] in ("hi-en", "en")
    tok_to_lemma = dict(zip(res["tokens"], res["lemmas"]))
    assert tok_to_lemma.get("chutiyon") == "chutiya"
    assert tok_to_lemma.get("gaddaron") == "gaddar"


# ==============================================================================
# 2. Dataset Folder & Splits Integrity
# ==============================================================================

def test_dataset_directory_structure():
    root = Path(__file__).resolve().parent.parent
    dataset_dir = root / "dataset"
    proc_dir = dataset_dir / "processed"
    raw_dir = dataset_dir / "raw"
    
    assert dataset_dir.exists(), "dataset/ folder must exist"
    assert proc_dir.exists(), "dataset/processed/ must exist"
    assert raw_dir.exists(), "dataset/raw/ must exist"
    
    # Check splits exist
    train_file = proc_dir / "train.jsonl"
    val_file = proc_dir / "val.jsonl"
    test_file = proc_dir / "test.jsonl"
    all_file = proc_dir / "all_nlp_processed.jsonl"
    
    assert train_file.exists() and train_file.stat().st_size > 0
    assert val_file.exists() and val_file.stat().st_size > 0
    assert test_file.exists() and test_file.stat().st_size > 0
    assert all_file.exists() and all_file.stat().st_size > 0
    
    # Check summary metadata
    summary_file = dataset_dir / "dataset_summary.json"
    assert summary_file.exists()
    with open(summary_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["total_samples"] >= 1000
    assert "split_counts" in meta
    assert "class_distribution" in meta
    assert len(meta["nlp_techniques_applied"]) >= 8


def test_dataset_splits_no_data_leakage():
    root = Path(__file__).resolve().parent.parent
    proc_dir = root / "dataset" / "processed"
    
    def get_ids(path):
        ids = set()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    ids.add(json.loads(line)["id"])
        return ids

    train_ids = get_ids(proc_dir / "train.jsonl")
    val_ids = get_ids(proc_dir / "val.jsonl")
    test_ids = get_ids(proc_dir / "test.jsonl")
    
    # Mathematical proof of zero split leakage
    assert len(train_ids.intersection(val_ids)) == 0, "Train and Val must be disjoint"
    assert len(train_ids.intersection(test_ids)) == 0, "Train and Test must be disjoint"
    assert len(val_ids.intersection(test_ids)) == 0, "Val and Test must be disjoint"


# ==============================================================================
# 3. Dynamic End-to-End Classification Across Categories
# ==============================================================================

@pytest.mark.parametrize("text,expected_label", [
    # English direct hate vs civil
    ("These disgusting illegal immigrants are vermin infecting our country and should be eliminated.", 1),
    ("We must defend human rights, equality, dignity, and mutual respect for all people.", 0),
    ("In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.", 0),
    # Hindi direct hate vs civil
    ("ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।", 1),
    ("हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है।", 0),
    # Hinglish direct hate vs counterspeech
    ("In chutiyon ko desh se bahar phenko, inka koi haq nahi yahan rehne ka.", 1),
    ("Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.", 0),
    ("Bhai aaj match me kya zabardast batting ki Virat ne, maza aa gaya sach me!", 0),
])
def test_end_to_end_multilingual_classification(engine, text, expected_label):
    pred = engine.predict(text)
    assert pred["label"] == expected_label, (
        f"Failed for input '{text}': got label {pred['label']}, expected {expected_label}"
    )
    assert 0.0 <= pred["confidence"] <= 1.0


# ==============================================================================
# 4. Token Attribution: Hateful (Red) vs Non-Hateful (Green) Validation
# ==============================================================================

def test_token_attribution_hostile_words_marked_positive(engine, xai):
    text = "These disgusting immigrants are vermin and parasites."
    res = xai.compute_perturbation_attribution(text, engine.predict)
    tokens = {t["token"].lower(): t for t in res["token_attributions"]}
    
    # Hostile words must be flagged with positive attribution (Hateful / Red)
    assert "vermin" in tokens
    assert tokens["vermin"]["polarity"] == "positive_evidence"
    assert tokens["vermin"]["score"] > 0.0
    
    if "parasites" in tokens:
        assert tokens["parasites"]["polarity"] == "positive_evidence"
        assert tokens["parasites"]["score"] > 0.0


def test_token_attribution_counterspeech_marked_negative(engine, xai):
    text = "Quoting slurs is completely unacceptable and false."
    res = xai.compute_perturbation_attribution(text, engine.predict)
    tokens = {t["token"].lower(): t for t in res["token_attributions"]}
    
    # Mitigating words must be flagged with negative attribution (Non-hateful / Green)
    assert "unacceptable" in tokens
    assert tokens["unacceptable"]["polarity"] == "negative_evidence"
    assert tokens["unacceptable"]["score"] < 0.0


def test_token_attribution_stopwords_marked_neutral(engine, xai):
    text = "samanyu is stinky indian and he should be jailed"
    res = xai.compute_perturbation_attribution(text, engine.predict)
    tokens = {t["token"].lower(): t for t in res["token_attributions"]}
    
    # Functional conjunctions and pronouns should be neutral
    for stop in ["is", "and", "he", "be"]:
        if stop in tokens:
            assert tokens[stop]["polarity"] == "neutral"


# ==============================================================================
# 5. Live REST API Endpoints Verification
# ==============================================================================

def test_api_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "device" in data
    assert "app" in data


def test_api_detect_v2_with_explainability(client):
    payload = {
        "text": "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.",
        "explain": True
    }
    res = client.post("/api/detection/detect-v2", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert data["predicted_label"] == 0
    assert data["label_name"] == "NON-HATEFUL"
    assert "explanation" in data
    
    exp = data["explanation"]
    assert "token_attributions" in exp
    assert len(exp["token_attributions"]) > 0
    assert "shapley_streams" in exp
    assert "steps" in exp
    assert len(exp["steps"]) >= 4


def test_api_reports_summary_endpoint(client):
    res = client.get("/api/reports/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_samples"] >= 1000
    assert "active_model" in data
    assert "datasets" in data
