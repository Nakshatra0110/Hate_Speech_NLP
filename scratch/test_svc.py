import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.explainability.openai_service import OpenAIExplainabilityService
from src.preprocessing.text.normalizer import TextNormalizer

svc = OpenAIExplainabilityService()
norm = TextNormalizer()
t = "These disgusting illegal immigrants are vermin infecting our country and should be eliminated"
toks = norm.tokenize_words(norm.normalize(t))
res = svc.explain_and_attribute(t, label=1, confidence=0.99, language="en", tokens=toks)

print("SUCCESS:", res is not None)
if res:
    print("SHORT EXP:", res["short_explanation"])
    print("STEPS:")
    for s in res["steps"]:
        print(f"  Step {s['step']}: {s['title']} -> {s['body']}")
    print("NON-NEUTRAL TOKENS:")
    for tok in res["token_attributions"]:
        if tok["polarity"] != "neutral":
            print(f"  {tok['token']:15s} | {tok['polarity']:18s} | {tok['score']:+.2f}")
