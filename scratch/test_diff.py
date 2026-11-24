import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from src.models.transformer_classifier import MultilingualTransformerEngine

engine = MultilingualTransformerEngine()
text = "samanyu is stinky indian and he should be jailed"
words = text.split()
base = engine.predict(text)
bz0, bz1 = base["logits"][0], base["logits"][1]
base_diff = bz1 - bz0

print(f"Base: diff={base_diff:.4f} (z0={bz0:.3f}, z1={bz1:.3f})")
for i, w in enumerate(words):
    sub = " ".join(words[:i] + words[i+1:])
    p = engine.predict(sub)
    pz0, pz1 = p["logits"][0], p["logits"][1]
    p_diff = pz1 - pz0
    dl = base_diff - p_diff
    print(f"Token '{w}': delta_diff={dl:.4f} (sub_diff={p_diff:.4f})")
