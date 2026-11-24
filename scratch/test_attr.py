import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from src.models.transformer_classifier import MultilingualTransformerEngine
from src.explainability.text_attribution import TextAttributionEngine

engine = MultilingualTransformerEngine()
xai = TextAttributionEngine()
res = xai.compute_perturbation_attribution("samanyu is stinky indian and he should be jailed", engine.predict)
print("Base logits:", res.get("base_logits"))
for t in res["token_attributions"]:
    print(f"{t['token']}: score={t['score']} pol={t['polarity']} raw={t.get('raw_delta_logit')}")
