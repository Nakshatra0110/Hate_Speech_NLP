import sys
sys.path.insert(0, ".")
from src.multimodal.ocr import OCRService

for m in ['meme_counter.png', 'meme_vermin.png', 'meme_kindness.png', 'meme_education.png', 'meme_change_my_mind.png']:
    res = OCRService.extract_text(f'data/raw/images/{m}')
    print(f"[{m}] Text: {res.get('extracted_text')} | Lines: {len(res.get('lines', []))} | Conf: {res.get('confidence')}")
