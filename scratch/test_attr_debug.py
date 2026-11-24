import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.detection import _xai_engine, get_models

sentences = [
    "These disgusting illegal immigrants are vermin infecting our country and should be eliminated",
    "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities",
    "We must defend human rights and build a community founded on equality, dignity, and mutual respect",
    "ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।",
    "हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है।",
    "पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।"
]

classical_clf, transformer_clf = get_models()

for s in sentences:
    print("=" * 60)
    print("SENTENCE:", s)
    pred = transformer_clf.predict(s)
    print("PREDICT VERDICT:", pred['verdict'], "CONF:", pred['confidence'], "LOGITS:", pred['logits'])
    res = _xai_engine.compute_perturbation_attribution(s, lambda text: transformer_clf.predict(text))
    for a in res['token_attributions']:
        print(f"  {a['token']:15s} | score={a['score']:6.2f} | raw_dl={a['raw_delta_logit']:6.2f} | pol={a['polarity']}")
