from typing import List, Dict, Any, Optional

class ExplanationSynthesizer:
    """
    Synthesizes honest, plain-language multi-stream explanations
    structured around x_i = {T_i, V_i, C_i}.
    Avoids duplicate headings and untruthful claims (e.g. 'gradient attribution').
    """
    @staticmethod
    def synthesize(
        label: int,
        confidence: float,
        language: str,
        token_attributions: List[Dict[str, Any]],
        faithfulness_score: float,
        ocr_text: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        decision_band: Optional[str] = None,
        aopc_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        label_str = "HATEFUL" if label == 1 else "NON-HATEFUL"
        if decision_band == "borderline_review" or (0.35 <= confidence <= 0.65):
            verdict_desc = f"{label_str} (Ambiguous / Borderline Decision)"
            review_rec = "Human review strongly recommended due to low decision margin."
        elif confidence >= 0.85:
            verdict_desc = f"{label_str} (High Certainty)"
            review_rec = "High statistical alignment; automated triage suitable."
        else:
            verdict_desc = f"{label_str} (Moderate Confidence)"
            review_rec = "Human review advised before taking punitive enforcement."

        # Extract top positive (hate-inducing) and negative (mitigating) tokens
        sorted_tokens = sorted(token_attributions, key=lambda x: x["score"], reverse=True)
        top_hate_tokens = [f"'{t['token']}' ({t['score']:+.2f})" for t in sorted_tokens if t["score"] > 0.01][:5]
        top_mitigating_tokens = [f"'{t['token']}' ({t['score']:+.2f})" for t in sorted(token_attributions, key=lambda x: x["score"]) if t["score"] < -0.01][:5]

        steps = []

        # Step 1: Classification
        steps.append({
            "step": 1,
            "title": "Classification",
            "body": f"The input is categorized as {verdict_desc} with {confidence*100:.1f}% temperature-calibrated confidence."
        })

        # Step 2: Textual Modality (T) Evidence
        if label == 1:
            if top_hate_tokens:
                t_body = f"Primary linguistic markers elevating hostility include: {', '.join(top_hate_tokens)}."
            else:
                t_body = "Hostility inferred from multi-word phrasing or code-mixed structural exclusion patterns."
        else:
            if top_mitigating_tokens:
                t_body = f"Civil, counter-speech, or mitigating markers lowering hostility include: {', '.join(top_mitigating_tokens)}."
            else:
                t_body = "Absence of dehumanizing slurs, hostile directives, or identity-targeted incitement."
        steps.append({
            "step": 2,
            "title": "Textual Evidence (T)",
            "body": t_body
        })

        # Step 3: Visual & Typography Modality (V)
        if ocr_text and ocr_text.strip():
            v_body = f"Embedded typography was extracted via multi-pass EasyOCR (\"{ocr_text.strip()}\") and evaluated alongside textual cues."
        else:
            v_body = "No visual typography detected; evaluation executed purely over the linguistic modality."
        steps.append({
            "step": 3,
            "title": "Visual Typography (V)",
            "body": v_body
        })

        # Step 4: Contextual History (C)
        if context_data and context_data.get("has_context"):
            framing = context_data.get("context_framing", "neutral_thread")
            delta_z = context_data.get("delta_z_context", 0.0)
            c_body = f"Conversation context evaluated ({context_data.get('thread_length', 1)} turns). Framing identified as '{framing}' (bounded logit shift Δz = {delta_z:+.2f})."
        else:
            c_body = "Standalone post evaluated without prior conversation thread history."
        steps.append({
            "step": 4,
            "title": "Contextual History (C)",
            "body": c_body
        })

        # Step 5: Faithfulness & Recommendation
        steps.append({
            "step": 5,
            "title": "Faithfulness",
            "body": f"Leave-one-out perturbation attribution verified with an AOPC faithfulness score of {faithfulness_score:.2f}. {review_rec}"
        })

        # Combine into plain text
        full_text = "\n\n".join([f"{s['step']}. {s['title']}: {s['body']}" for s in steps])

        return {
            "natural_language_explanation": full_text,
            "steps": steps,
            "top_hate_tokens": top_hate_tokens,
            "top_non_hate_tokens": top_mitigating_tokens,
            "faithfulness_score": round(faithfulness_score, 4)
        }
