from backend.api.detection import detect_content
from backend.schemas.detection import DetectionRequest
import traceback

test_texts = [
    # English non-hateful
    "Hello everyone, hope you are having a wonderful day!",
    # English hateful
    "These immigrants are vermin infecting our country and should be eliminated.",
    # Hinglish counterspeech (the one in user's screenshot)
    "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.",
    # Hinglish hateful
    "ye log desh ke gaddar hai, inko maro",
    # Hindi Devanagari non-hateful
    "नमस्ते दोस्तों, आज का दिन बहुत सुंदर है और हम सब मिलकर काम करेंगे।",
    # Hindi Devanagari hateful
    "ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।"
]

for t in test_texts:
    try:
        req = DetectionRequest(text=t, explain=True)
        res = detect_content(req)
        print(f"[{res.language_detected}] {res.predicted_label} ({res.verdict}) conf={res.confidence:.4f} | Text: {t[:40]}...")
    except Exception as e:
        print(f"FAILED on '{t[:30]}': {e}")
        traceback.print_exc()
