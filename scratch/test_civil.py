import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from src.models.transformer_classifier import MultilingualTransformerEngine
from src.explainability.text_attribution import TextAttributionEngine

engine = MultilingualTransformerEngine()
xai = TextAttributionEngine()
res = xai.compute_perturbation_attribution("We believe in peace and equality for all people", engine.predict)
print("Base logits:", res.get("base_logits"))
for t in res["token_attributions"]:
    print(f"{t['token']}: score={t['score']} pol={t['polarity']}")
