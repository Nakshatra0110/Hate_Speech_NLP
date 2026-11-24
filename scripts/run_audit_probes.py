import os
import sys
import json
import time
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

import sqlite3
import torch
from backend.core.config import settings
from src.models.transformer_classifier import MultilingualAttentionClassifier, MultilingualTransformerEngine
from src.multimodal.ocr import OCRService, BENCHMARK_MEME_CATALOG
from src.preprocessing.text.normalizer import TextNormalizer
from src.explainability.text_attribution import TextAttributionEngine
from src.language.detector import MultilingualLanguageDetector
from src.preprocessing.context.context_processor import ContextProcessor
from src.preprocessing.image.image_preprocessor import ImagePreprocessor
from src.multimodal.fusion import MultimodalDetector

# 1. Database & Dataset Analysis
conn = sqlite3.connect(str(settings.database_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 1. DATASETS & SPLITS AUDIT ===")
datasets = cursor.execute("SELECT * FROM datasets").fetchall()
for d in datasets:
    d_dict = dict(d)
    print(f"Dataset {d_dict['id']}: name={d_dict['name']}, count={d_dict['sample_count']}, path={d_dict['file_path']}")
    p = Path(d_dict['file_path']) if d_dict['file_path'] else None
    if p and not p.is_absolute():
        p = base_dir / p
    if p and p.exists():
        if p.suffix == ".jsonl":
            records = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            records = json.loads(p.read_text(encoding="utf-8"))
        print(f"  File exists, records={len(records)}")
        texts = [r['text'] for r in records if 'text' in r]
        print(f"  Unique texts: {len(set(texts))}/{len(texts)}")

# 2. Model Architecture & Checkpoint Audit
print("\n=== 2. MODEL ARCHITECTURE & REGISTRY AUDIT ===")
models = cursor.execute("SELECT * FROM model_registry").fetchall()
for m in models:
    print(dict(m))

ckpt_path = base_dir / "models/checkpoints/multilingual_transformer.pt"
if ckpt_path.exists():
    state = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
    print(f"multilingual_transformer.pt keys: {list(state.keys()) if isinstance(state, dict) else type(state)}")
    if isinstance(state, dict) and "model_state_dict" in state:
        sd = state["model_state_dict"]
        print(f"  Layer names in checkpoint: {list(sd.keys())}")
        print(f"  lstm weight_ih_l0 shape: {sd.get('lstm.weight_ih_l0', 'None').shape if 'lstm.weight_ih_l0' in sd else 'N/A'}")
        print(f"  attention in_proj_weight shape: {sd.get('attention.in_proj_weight', 'None').shape if 'attention.in_proj_weight' in sd else 'N/A'}")

# 3. Running Pre-Flight Probes a-i
print("\n=== 3. PROBES a-i (TEXT, COUNTERSPEECH, CODE-MIXED, CONTEXT) ===")
engine = MultilingualTransformerEngine(checkpoint_path=str(ckpt_path))
engine.load_checkpoint()

normalizer = TextNormalizer()
xai = TextAttributionEngine(normalizer)

probes = [
    ("a", "immigrants are vermin", None),
    ("b", 'Someone wrote "immigrants are vermin" which is completely unacceptable racist hate speech.', None),
    ("c", 'Someone wrote "immigrants are vermin" which is completely unacceptable racist hate speech. ... but honestly it\'s true.', None),
    ("d", "ye log desh ke gaddar hai", None),
    ("e", "ये लोग देश के गद्दार हैं", None),
    ("f", "I am a proud Muslim.", None),
    ("g", "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.", "Academic research curriculum on human rights."),
    ("h_empty", "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.", None),
    ("h_hostile", "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.", "Gas them all and finish what was started."),
    ("i_framing_removed", "propaganda used terms like 'subhuman' to systematically dehumanize communities.", None),
    ("i_bare_slurs", "subhuman dehumanize communities", None)
]

probe_results = {}
for pid, text, ctx in probes:
    t0 = time.perf_counter()
    pred = engine.predict(text)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    
    # XAI
    attr_res = xai.compute_perturbation_attribution(text, engine.predict)
    tokens_top = [f"{a['token']}({a['score']:+.3f})" for a in attr_res['token_attributions'][:5]]
    
    probe_results[pid] = {
        "text": text,
        "context": ctx,
        "label": pred["label"],
        "label_name": pred["label_name"],
        "confidence": pred["confidence"],
        "raw_hateful_p": pred["raw_hateful_probability"],
        "logits": pred["logits"],
        "elapsed_ms": round(elapsed_ms, 2),
        "faithfulness": attr_res["faithfulness_score"],
        "top_tokens": tokens_top
    }
    print(f"Probe {pid:18s} | {pred['label_name']:12s} | p_hate={pred['raw_hateful_probability']:.4f} | conf={pred['confidence']:.4f} | logits={pred['logits']} | lat={elapsed_ms:.2f}ms")
    print(f"   Tokens: {', '.join(tokens_top)}")
    print(f"   Faithfulness: {attr_res['faithfulness_score']}")

# 4. Context Impact Verification
print("\n=== 4. CONTEXT IMPACT TEST ON DETECTION API ===")
# Does context change probability in the current backend?
# Let's check backend/api/detection.py logic:
ctx_proc = ContextProcessor()
for ctx_text in ["", "Academic research curriculum on human rights.", "Gas them all and finish what was started."]:
    ctx_info = ctx_proc.process(ctx_text)
    # in backend/api/detection.py, transformer_clf.predict(full_text) is called without ctx!
    print(f"Context: '{ctx_text[:30]}...' -> has_context={ctx_info['has_context']}, passed to model=NO (0.0 logit impact)")

# 5. Visual Impact Verification (V)
print("\n=== 5. VISUAL FUSION IMPACT TEST ===")
# MultimodalDetector in backend/api/detection.py
mm_detector = MultimodalDetector(dim=128, text_in_dim=256)
img_proc = ImagePreprocessor()
test_images = [
    "data/raw/images/meme_counter.png",
    "data/raw/images/meme_vermin.png",
    "data/raw/images/meme_kindness.png"
]
text_for_v = "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities."
text_feat = engine.encode_text(text_for_v)
print(f"Text: '{text_for_v[:50]}...'")
for img_path in test_images:
    p = base_dir / img_path
    if p.exists():
        img_props = img_proc.inspect_and_preprocess(p)
        arr = img_props["processed_array"]
        img_tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).float()
        with torch.no_grad():
            mm_logits = mm_detector(text_feat, img_tensor)
            mm_probs = torch.softmax(mm_logits, dim=-1).numpy()[0]
        p_mm_hate = float(mm_probs[1])
        base_pred = engine.predict(text_for_v)
        fused = round(0.70 * base_pred["raw_hateful_probability"] + 0.30 * p_mm_hate, 4)
        print(f"Image: {p.name:20s} | mm_logits={mm_logits.numpy()[0]} | p_mm_hate={p_mm_hate:.4f} | fused_p={fused:.4f}")

# 6. OCR Probe j on 10 Memes
print("\n=== 6. OCR PROBE j ON 10 REAL MEMES ===")
# Test both: (A) with filename in catalog vs (B) raw image without filename to see actual OCR
images_dir = base_dir / "data/raw/images"
meme_files = sorted(images_dir.glob("*.png"))
from PIL import Image

for mf in meme_files:
    # A: Filename passed (catalog hit)
    res_catalog = OCRService.extract_text(str(mf))
    # B: PIL Image passed (bypasses filename match if Path check fails, or check reader)
    pil_img = Image.open(str(mf))
    # Test OCR reader directly
    reader = OCRService.get_reader()
    if reader is not None:
        try:
            enhanced = OCRService.preprocess_for_ocr(pil_img)
            import numpy as np
            raw_ocr = reader.readtext(np.array(enhanced))
            ocr_text = " ".join([t[1] for t in raw_ocr])
        except Exception as e:
            ocr_text = f"ERROR: {e}"
    else:
        ocr_text = "READER_NONE"

    print(f"Meme: {mf.name:18s} | Catalog: '{res_catalog['extracted_text']}' ({res_catalog['engine']}) | Real EasyOCR: '{ocr_text}'")

# Save results for AUDIT.md
out_file = base_dir / "scratch" / "probe_results.json"
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(json.dumps(probe_results, indent=2), encoding="utf-8")
print(f"\nProbe results saved to {out_file}")
