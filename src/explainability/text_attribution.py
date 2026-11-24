from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from src.preprocessing.text.normalizer import TextNormalizer
from src.explainability.faithfulness import FaithfulnessEvaluator

class TextAttributionEngine:
    """
    Logit-Scale Leave-One-Out Perturbation Attribution Engine.
    Operates strictly on the unconstrained logit scale z to eliminate softmax saturation.
    Computes token-level and multi-word phrase-level delta logits:
        Delta z = z_1(text) - z_1(text \ {token})
    Delta > 0: token increases hateful score (positive evidence for hostility).
    Delta < 0: token decreases hateful score (mitigating evidence / counterspeech).
    """
    def __init__(self, normalizer: Optional[TextNormalizer] = None):
        self.normalizer = normalizer or TextNormalizer()

    def compute_perturbation_attribution(self, text: str, predict_fn) -> Dict[str, Any]:
        words = self.normalizer.tokenize_words(self.normalizer.normalize(text))
        if not words:
            return {
                "token_attributions": [],
                "faithfulness_score": 1.0,
                "aopc_details": {},
                "comprehensiveness": 0.0,
                "sufficiency": 0.0
            }

        base_res = predict_fn(text)
        base_logits = base_res.get("logits", [0.0, 0.0])
        z0, z1 = base_logits[0], base_logits[1]
        target_logit = z1  # Attribute with respect to hate logit z1

        raw_pert = []
        for i in range(len(words)):
            perturbed_words = words[:i] + words[i+1:]
            perturbed_text = " ".join(perturbed_words) if perturbed_words else "[EMPTY]"
            
            p_res = predict_fn(perturbed_text)
            p_logits = p_res.get("logits", [0.0, 0.0])
            pz1 = p_logits[1]

            # Change in hate logit when token i is removed
            dl = float(target_logit - pz1)
            raw_pert.append((words[i], dl))

        # Normalize logit sensitivity to [-1.0, +1.0] scale
        max_abs_dl = max((abs(r[1]) for r in raw_pert), default=1.0)
        norm_factor = max(0.5, max_abs_dl)

        attributions = []
        for w, dl in raw_pert:
            # Normalized attribution score
            norm_score = round(dl / norm_factor, 4)
            # Filter negligible scores
            if abs(norm_score) < 0.005:
                norm_score = 0.0
                pol = "neutral"
            elif norm_score > 0.0:
                pol = "positive_evidence"
            else:
                pol = "negative_evidence"

            attributions.append({
                "token": w,
                "score": norm_score,
                "raw_delta_logit": round(dl, 4),
                "abs_score": abs(norm_score),
                "polarity": pol
            })

        # Multi-word phrase check (for quoted phrases or multi-word slurs)
        if len(words) >= 4:
            for window in [2, 3]:
                for start_idx in range(len(words) - window + 1):
                    phrase_tokens = words[start_idx:start_idx+window]
                    remaining = words[:start_idx] + words[start_idx+window:]
                    rem_text = " ".join(remaining) if remaining else "[EMPTY]"
                    p_res = predict_fn(rem_text)
                    p_logits = p_res.get("logits", [0.0, 0.0])
                    phrase_dl = float(target_logit - p_logits[1])
                    if abs(phrase_dl) > 1.2 * sum(abs(a["raw_delta_logit"]) for a in attributions[start_idx:start_idx+window]):
                        # Interaction effect detected across phrase
                        for k in range(start_idx, start_idx+window):
                            boosted = round(phrase_dl / (window * norm_factor), 4)
                            attributions[k]["score"] = boosted
                            attributions[k]["polarity"] = "positive_evidence" if boosted > 0 else "negative_evidence"

        # Rigorous Faithfulness Evaluation via AOPC
        aopc_eval = FaithfulnessEvaluator.evaluate_aopc(text, attributions, predict_fn)
        comp_suff = FaithfulnessEvaluator.evaluate_comprehensiveness_and_sufficiency(text, attributions, predict_fn)

        return {
            "token_attributions": attributions,
            "faithfulness_score": aopc_eval["aopc_score"],
            "aopc_details": aopc_eval,
            "comprehensiveness": comp_suff["comprehensiveness"],
            "sufficiency": comp_suff["sufficiency"],
            "base_logits": [round(z0, 4), round(z1, 4)]
        }
