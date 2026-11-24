import math
from typing import Dict, Any, List, Optional, Callable

class StreamShapleyExplainer:
    """
    Computes exact Shapley attribution for the three-stream input formulation:
        x_i = { T_i, V_i, C_i }
    where:
        T_i: Linguistic / textual content
        V_i: Visual typography (OCR) and visual representations
        C_i: Conversational context, metadata, and framing

    Since |N| = 3, evaluating all 2^3 = 8 subsets S ⊆ {T, V, C} is exact,
    deterministic, and takes ~1-2 milliseconds.
    Efficiency property: phi_T + phi_V + phi_C = z(T, V, C) - z(∅)
    holds identically to floating-point precision (< 1e-6).
    """

    @staticmethod
    def sigmoid(z: float) -> float:
        """Numerically stable sigmoid function."""
        if z >= 0:
            ez = math.exp(-z)
            return 1.0 / (1.0 + ez)
        else:
            ez = math.exp(z)
            return ez / (1.0 + ez)

    @classmethod
    def compute_shapley_streams(
        cls,
        text: str,
        eval_fn: Callable[[str, Optional[str], Optional[Dict[str, Any]]], float],
        ocr_text: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        ocr_lines: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        eval_fn(t, v_ocr, c_dict) -> logit z for hateful class relative to non-hateful class.
        """
        has_t_input = bool(text and text.strip())
        has_v_input = bool(ocr_text and ocr_text.strip()) or bool(ocr_lines and len(ocr_lines) > 0)
        has_c_input = bool(context_data and context_data.get("has_context"))

        # Define 8 subsets: (T_active, V_active, C_active) -> logit z
        # If an input stream is completely absent in the request, its marginal contribution is 0.
        subsets = {}
        for b_t in (0, 1):
            for b_v in (0, 1):
                for b_c in (0, 1):
                    t_val = text if (b_t and has_t_input) else ""
                    v_val = ocr_text if (b_v and has_v_input) else ""
                    c_val = context_data if (b_c and has_c_input) else None
                    
                    z_val = eval_fn(t_val, v_val, c_val)
                    subsets[(b_t, b_v, b_c)] = float(z_val)

        z000 = subsets[(0, 0, 0)]
        z100 = subsets[(1, 0, 0)]
        z010 = subsets[(0, 1, 0)]
        z001 = subsets[(0, 0, 1)]
        z110 = subsets[(1, 1, 0)]
        z101 = subsets[(1, 0, 1)]
        z011 = subsets[(0, 1, 1)]
        z111 = subsets[(1, 1, 1)]

        # Shapley formula weights for |N|=3:
        # |S| = 0: 1/3
        # |S| = 1: 1/6
        # |S| = 2: 1/3
        w0 = 1.0 / 3.0
        w1 = 1.0 / 6.0
        w2 = 1.0 / 3.0

        phi_t = w0 * (z100 - z000) + w1 * (z110 - z010) + w1 * (z101 - z001) + w2 * (z111 - z011)
        phi_v = w0 * (z010 - z000) + w1 * (z110 - z100) + w1 * (z011 - z001) + w2 * (z111 - z101)
        phi_c = w0 * (z001 - z000) + w1 * (z101 - z100) + w1 * (z011 - z010) + w2 * (z111 - z110)

        # Efficiency verification:
        total_delta = z111 - z000
        sum_phi = phi_t + phi_v + phi_c
        efficiency_gap = abs(sum_phi - total_delta)

        # Stream agreement classification
        agreement = "concordant"
        t_active = abs(phi_t) > 0.15
        v_active = abs(phi_v) > 0.15
        c_active = abs(phi_c) > 0.15

        if t_active and v_active and ((phi_t > 0.2 and phi_v < -0.2) or (phi_t < -0.2 and phi_v > 0.2)):
            agreement = "cross_modal_tension"
        elif phi_t > 0.2 and phi_c < -0.2:
            agreement = "context_mitigated"
        elif not t_active and not v_active and not c_active:
            agreement = "neutral"

        # Sequential Waterfall Steps
        # Step 0: Baseline neutral logit
        # Step 1: + phi_T -> Text contribution
        # Step 2: + phi_V -> Visual contribution
        # Step 3: + phi_C -> Context contribution -> Final logit
        z_step0 = z000
        z_step1 = z_step0 + phi_t
        z_step2 = z_step1 + phi_v
        z_step3 = z_step2 + phi_c

        waterfall = [
            {
                "step_index": 0,
                "name": "Prior Baseline z(∅)",
                "stream": "baseline",
                "delta_z": round(z000, 4),
                "cumulative_z": round(z_step0, 4),
                "probability": round(cls.sigmoid(z_step0), 4)
            },
            {
                "step_index": 1,
                "name": "Linguistic Content T_i",
                "stream": "text",
                "delta_z": round(phi_t, 4),
                "cumulative_z": round(z_step1, 4),
                "probability": round(cls.sigmoid(z_step1), 4)
            },
            {
                "step_index": 2,
                "name": "Visual Typography V_i",
                "stream": "visual",
                "delta_z": round(phi_v, 4),
                "cumulative_z": round(z_step2, 4),
                "probability": round(cls.sigmoid(z_step2), 4)
            },
            {
                "step_index": 3,
                "name": "Conversational Context C_i",
                "stream": "context",
                "delta_z": round(phi_c, 4),
                "cumulative_z": round(z_step3, 4),
                "probability": round(cls.sigmoid(z_step3), 4)
            }
        ]

        return {
            "formal_input": {
                "T": text or "(empty)",
                "V": {
                    "has_visual": has_v_input,
                    "ocr_text": ocr_text or "",
                    "line_count": len(ocr_lines) if ocr_lines else 0
                },
                "C": {
                    "has_context": has_c_input,
                    "platform": (context_data or {}).get("platform", "none"),
                    "framing": (context_data or {}).get("context_framing", "none")
                }
            },
            "shapley_streams": {
                "phi_T": round(phi_t, 4),
                "phi_V": round(phi_v, 4),
                "phi_C": round(phi_c, 4),
                "baseline_z": round(z000, 4),
                "final_z": round(z111, 4),
                "sum_check": round(sum_phi, 4),
                "efficiency_gap": round(efficiency_gap, 8)
            },
            "stream_agreement": agreement,
            "subsets": {f"{k[0]}{k[1]}{k[2]}": round(v, 4) for k, v in subsets.items()},
            "waterfall": waterfall
        }
