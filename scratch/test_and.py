import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from src.models.transformer_classifier import MultilingualTransformerEngine

engine = MultilingualTransformerEngine()
p1 = engine.predict("samanyu is stinky indian and he should be jailed")
p2 = engine.predict("samanyu is stinky indian he should be jailed")
print("With 'and':", p1["logits"], p1["calibrated_logits"], p1["label"])
print("Without 'and':", p2["logits"], p2["calibrated_logits"], p2["label"])
