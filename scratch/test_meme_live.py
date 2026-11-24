import requests
import json
from pathlib import Path

def test_meme_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Dedicated OCR endpoint
    print("Testing /api/detection/ocr with hostile meme...")
    ocr_payload = {"image_path": "data/raw/images/meme_vermin.png"}
    ocr_res = requests.post(f"{base_url}/api/detection/ocr", json=ocr_payload, timeout=60)
    assert ocr_res.status_code == 200, f"OCR endpoint failed: {ocr_res.text}"
    ocr_data = ocr_res.json()
    print("OCR Status:", ocr_data["status"])
    print("Extracted Text:", ocr_data["extracted_text"])
    print("Lines detected:", len(ocr_data["lines"]))
    for line in ocr_data["lines"]:
        print(f"  Line: '{line['text']}' (Conf: {line['confidence']}, Norm: {line.get('box_norm')})")

    # Test 2: Full Detection Pipeline with Meme (Hostile Meme)
    print("\n" + "="*60)
    print("Testing /api/detection/detect-v2 with Hostile Meme (meme_vermin.png)...")
    detect_payload = {
        "image_path": "data/raw/images/meme_vermin.png",
        "explain": True
    }
    det_res = requests.post(f"{base_url}/api/detection/detect-v2", json=detect_payload, timeout=60)
    assert det_res.status_code == 200, f"Detection failed: {det_res.text}"
    det_data = det_res.json()

    print(f"Verdict: {det_data['label_name']} ({det_data['confidence']*100:.1f}%)")
    expl = det_data.get("explanation", {})
    print(f"Verdict Rationale: {expl.get('natural_language_explanation')}")
    print(f"Visual Attributions Count: {len(expl.get('visual_attributions', []))}")
    for v in expl.get("visual_attributions", []):
        print(f"  Region '{v['region_label']}': score={v['attribution_score']}, norm={v.get('box_norm')}")

    shapley = expl.get("shapley_streams", {})
    print(f"Shapley Streams: φ_T={shapley.get('phi_T'):+.2f}, φ_V={shapley.get('phi_V'):+.2f}, φ_C={shapley.get('phi_C'):+.2f}")
    assert det_data["predicted_label"] == 1, "Hostile meme should be classified as HATEFUL"

    # Test 3: Full Detection Pipeline with Civil Meme (meme_counter.png)
    print("\n" + "="*60)
    print("Testing /api/detection/detect-v2 with Civil Meme (meme_counter.png)...")
    civil_payload = {
        "image_path": "data/raw/images/meme_counter.png",
        "explain": True
    }
    civ_res = requests.post(f"{base_url}/api/detection/detect-v2", json=civil_payload, timeout=60)
    assert civ_res.status_code == 200, f"Detection failed: {civ_res.text}"
    civ_data = civ_res.json()

    print(f"Verdict: {civ_data['label_name']} ({civ_data['confidence']*100:.1f}%)")
    civ_expl = civ_data.get("explanation", {})
    print(f"Verdict Rationale: {civ_expl.get('natural_language_explanation')}")
    print(f"Visual Attributions Count: {len(civ_expl.get('visual_attributions', []))}")
    for v in civ_expl.get("visual_attributions", []):
        print(f"  Region '{v['region_label']}': score={v['attribution_score']}, norm={v.get('box_norm')}")

    assert civ_data["predicted_label"] == 0, "Civil meme should be classified as NON-HATEFUL"
    print("\nALL MEME OCR AND API DETECTION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_meme_endpoints()
