import numpy as np
from typing import List, Dict, Any, Callable, Tuple

class FaithfulnessEvaluator:
    """
    Empirical XAI Faithfulness Evaluation suite:
    1. AOPC (Area Over the Perturbation Curve / Average Order of Probability Change)
    2. Comprehensiveness (Does removing the rationale degrade prediction confidence?)
    3. Sufficiency (Is the rationale alone sufficient to sustain prediction confidence?)
    Evaluated on logit scale to avoid softmax saturation artifacts.
    """
    @staticmethod
    def evaluate_aopc(
        text: str,
        token_attributions: List[Dict[str, Any]],
        predict_fn: Callable[[str], Dict[str, Any]],
        k_steps: List[int] = [1, 2, 3, 5]
    ) -> Dict[str, Any]:
        words = text.split()
        if not words or not token_attributions:
            return {"aopc_score": 0.0, "step_drops": {}}

        base_res = predict_fn(text)
        base_logits = base_res.get("logits", [0.0, 0.0])
        pred_label = base_res.get("label", 1 if base_logits[1] > base_logits[0] else 0)
        base_logit = base_logits[pred_label]

        # Rank tokens by attribution magnitude supporting the predicted class
        if pred_label == 1:
            ranked_indices = [
                i for i in np.argsort([a["score"] for a in token_attributions])[::-1]
                if token_attributions[i]["score"] > 0
            ]
        else:
            ranked_indices = [
                i for i in np.argsort([a["score"] for a in token_attributions])
                if token_attributions[i]["score"] < 0
            ]

        if not ranked_indices:
            # Fall back to magnitude
            ranked_indices = list(np.argsort([abs(a["score"]) for a in token_attributions])[::-1])

        step_drops = {}
        valid_drops = []
        n_words = len(words)

        for k in k_steps:
            if k > n_words:
                continue
            remove_idx = set(ranked_indices[:k])
            ablated_tokens = [words[i] for i in range(n_words) if i not in remove_idx]
            ablated_text = " ".join(ablated_tokens) if ablated_tokens else "[EMPTY]"
            
            abl_res = predict_fn(ablated_text)
            abl_logits = abl_res.get("logits", [0.0, 0.0])
            abl_logit = abl_logits[pred_label]

            # Delta on target logit
            drop = base_logit - abl_logit
            step_drops[f"k_{k}"] = round(float(drop), 4)
            valid_drops.append(drop)

        # Average logit drop normalized by base margin
        mean_drop = float(np.mean(valid_drops)) if valid_drops else 0.0
        # Normalize into [0, 1] range: 0 means no drop (unfaithful), >0.5 means strong drop (faithful)
        norm_factor = max(1.0, abs(base_logit))
        normalized_aopc = round(float(np.clip(mean_drop / norm_factor, 0.0, 1.0)), 4)

        return {
            "aopc_score": normalized_aopc,
            "raw_mean_drop": round(mean_drop, 4),
            "step_drops": step_drops
        }

    @staticmethod
    def evaluate_comprehensiveness_and_sufficiency(
        text: str,
        token_attributions: List[Dict[str, Any]],
        predict_fn: Callable[[str], Dict[str, Any]],
        top_ratio: float = 0.20
    ) -> Dict[str, float]:
        """
        Comprehensiveness: base_prob - prob(text without top rationale tokens)
        Sufficiency: base_prob - prob(only top rationale tokens)
        """
        words = text.split()
        if not words or not token_attributions:
            return {"comprehensiveness": 0.0, "sufficiency": 0.0}

        base_res = predict_fn(text)
        base_logits = base_res.get("logits", [0.0, 0.0])
        pred_label = base_res.get("label", 1 if base_logits[1] > base_logits[0] else 0)
        base_logit = base_logits[pred_label]

        k = max(1, int(len(words) * top_ratio))
        # Top rationale indices
        if pred_label == 1:
            ranked = np.argsort([a["score"] for a in token_attributions])[::-1]
        else:
            ranked = np.argsort([a["score"] for a in token_attributions])

        top_k_indices = set(ranked[:k])

        # Comprehensiveness: evaluate text WITHOUT top rationale
        comp_tokens = [words[i] for i in range(len(words)) if i not in top_k_indices]
        comp_text = " ".join(comp_tokens) if comp_tokens else "[EMPTY]"
        comp_res = predict_fn(comp_text)
        comp_logit = comp_res.get("logits", [0.0, 0.0])[pred_label]
        comprehensiveness = round(float(base_logit - comp_logit), 4)

        # Sufficiency: evaluate ONLY top rationale
        suff_tokens = [words[i] for i in range(len(words)) if i in top_k_indices]
        suff_text = " ".join(suff_tokens) if suff_tokens else "[EMPTY]"
        suff_res = predict_fn(suff_text)
        suff_logit = suff_res.get("logits", [0.0, 0.0])[pred_label]
        sufficiency = round(float(base_logit - suff_logit), 4)

        return {
            "comprehensiveness": comprehensiveness,
            "sufficiency": sufficiency
        }
