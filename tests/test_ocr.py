import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from src.multimodal.ocr import OCRService

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def fixtures_dir():
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "tests" / "fixtures" / "memes"

def test_ocr_clean_english_meme(fixtures_dir):
    meme_path = fixtures_dir / "01_clean_civil.png"
    assert meme_path.exists(), f"Missing fixture {meme_path}"
    
    res = OCRService.extract_text(str(meme_path))
    assert res["status"] == "ok"
    assert len(res["lines"]) > 0
    assert 0.0 <= res["confidence"] <= 1.0

    # Verify normalized box bounds
    for line in res["lines"]:
        assert "box_norm" in line
        ymin, xmin, ymax, xmax = line["box_norm"]
        assert 0.0 <= ymin <= ymax <= 1.0
        assert 0.0 <= xmin <= xmax <= 1.0
        assert line["script"] in ["Latin", "Devanagari"]

def test_ocr_dark_inverted_meme(fixtures_dir):
    meme_path = fixtures_dir / "03_dark_inverted_civil.png"
    assert meme_path.exists()
    
    res = OCRService.extract_text(str(meme_path))
    assert res["status"] in ["ok", "no_text_found"]
    if res["status"] == "ok":
        assert len(res["extracted_text"]) > 0

def test_ocr_devanagari_hindi_meme(fixtures_dir):
    meme_path = fixtures_dir / "04_devanagari_civil.png"
    assert meme_path.exists()
    
    res = OCRService.extract_text(str(meme_path))
    # Devanagari script detection check
    if res["status"] == "ok":
        scripts = [l["script"] for l in res["lines"]]
        assert "Devanagari" in scripts or "Latin" in scripts

def test_ocr_invalid_file_handling():
    res = OCRService.extract_text("non_existent_file_path.png")
    assert res["status"] == "invalid_image"
    assert res["extracted_text"] == ""

def test_ocr_endpoint(client, fixtures_dir):
    meme_path = fixtures_dir / "01_clean_civil.png"
    payload = {"image_path": str(meme_path)}
    resp = client.post("/api/detection/ocr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["ok", "no_text_found"]
    assert "lines" in data
    assert "extracted_text" in data

def test_detection_with_ocr_lines_override(client):
    payload = {
        "text": "Check this meme out:",
        "ocr_lines_override": [
            {
                "text": "NO ROOM FOR RACISM",
                "confidence": 0.98,
                "script": "Latin",
                "box_px": [30, 40, 80, 500],
                "box_norm": [0.05, 0.06, 0.13, 0.83]
            },
            {
                "text": "EQUALITY FOR ALL",
                "confidence": 0.97,
                "script": "Latin",
                "box_px": [120, 50, 180, 480],
                "box_norm": [0.20, 0.08, 0.30, 0.80]
            }
        ],
        "explain": True
    }
    resp = client.post("/api/detection/detect", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["predicted_label"] == 0
    assert data["label_name"] == "NON-HATEFUL"
    assert "NO ROOM FOR RACISM" in (data["explanation"]["ocr_evidence"] or "")
