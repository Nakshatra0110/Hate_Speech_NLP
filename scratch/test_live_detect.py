import requests
import json

url = "http://127.0.0.1:8000/api/detection/detect"

test_sentences = [
    "These disgusting illegal immigrants are vermin infecting our country and should be eliminated",
    "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities",
    "We must defend human rights and build a community founded on equality, dignity, and mutual respect",
    "ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।"
]

for s in test_sentences:
    print("=" * 70)
    print("INPUT:", s)
    res = requests.post(url, json={"text": s}).json()
    print("VERDICT:", res.get("label_name"), f"({res.get('confidence')*100:.1f}%)")
    expl = res.get("explanation") or {}
    print("EXPLANATION:", expl.get("natural_language_explanation"))
    tokens = expl.get("token_attributions", [])
    print("TOKENS (token | polarity | score):")
    for t in tokens:
        print(f"  {t['token']:<15} | {t['polarity']:<17} | {t['score']:+.3f}")
