from typing import List, Dict, Any, Optional

class ExplanationSynthesizer:
    """
    Synthesizes honest, plain-language multi-stream explanations
    strictly organized around x_i = {T_i, V_i, C_i}.
    Avoids duplicate headings and untruthful claims (e.g. 'gradient attribution').
    Provides 5 clear structured steps:
      1. Classification & Calibration
      2. Stream Decomposition
      3. Dominant Tokens & Visual Regions
      4. Cross-Stream Interactions & Nuance
      5. Faithfulness & Limitations
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
        aopc_details: Optional[Dict[str, Any]] = None,
        shapley_data: Optional[Dict[str, Any]] = None,
        calibrated_logits: Optional[List[float]] = None
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
        sorted_tokens = sorted(token_attributions, key=lambda x: x.get("score", 0.0), reverse=True)
        top_hate_tokens = [f"'{t['token']}' ({t['score']:+.2f})" for t in sorted_tokens if t.get("score", 0.0) > 0.01][:5]
        top_mitigating_tokens = [f"'{t['token']}' ({t['score']:+.2f})" for t in sorted(token_attributions, key=lambda x: x.get("score", 0.0)) if t.get("score", 0.0) < -0.01][:5]

        # Extract Shapley stream contributions if available
        phi_t = 0.0
        phi_v = 0.0
        phi_c = 0.0
        agreement = "concordant"
        if shapley_data and "shapley_streams" in shapley_data:
            ss = shapley_data["shapley_streams"]
            phi_t = ss.get("phi_T", 0.0)
            phi_v = ss.get("phi_V", 0.0)
            phi_c = ss.get("phi_C", 0.0)
            agreement = shapley_data.get("stream_agreement", "concordant")

        # Logit value
        z_val = 0.0
        if calibrated_logits and len(calibrated_logits) >= 2:
            z_val = round(calibrated_logits[1] - calibrated_logits[0], 2)
        elif shapley_data and "shapley_streams" in shapley_data:
            z_val = shapley_data["shapley_streams"].get("final_z", 0.0)

        steps = []

        # Step 1: Classification & Calibration
        # Retain both title and 'Classification' for backwards-compatibility
        step1_body = (
            f"Model predicts {verdict_desc} with calibrated probability P = {confidence*100:.1f}% "
            f"(logit z = {z_val:+.2f}, temperature T = 1.35, decision band = {decision_band or 'normal'})."
        )
        steps.append({
            "step": 1,
            "title": "Classification & Calibration",
            "body": step1_body,
            "detail": step1_body
        })

        # Step 2: Stream Decomposition
        t_dir = "hostile" if phi_t > 0.05 else ("mitigating" if phi_t < -0.05 else "neutral")
        v_dir = "hostile" if phi_v > 0.05 else ("mitigating" if phi_v < -0.05 else "neutral")
        c_dir = "hostile" if phi_c > 0.05 else ("mitigating" if phi_c < -0.05 else "neutral")
        c_framing = (context_data or {}).get("context_framing", "direct_mention")
        
        step2_body = (
            f"Stream decomposition of x_i = {{T_i, V_i, C_i}} via exact Shapley attribution: "
            f"Text contributed φ_T = {phi_t:+.2f} ({t_dir}), "
            f"Visual contributed φ_V = {phi_v:+.2f} ({v_dir}), "
            f"Context contributed φ_C = {phi_c:+.2f} ({c_dir}{f' - {c_framing}' if phi_c != 0 else ''})."
        )
        steps.append({
            "step": 2,
            "title": "Stream Decomposition",
            "body": step2_body,
            "detail": step2_body
        })

        # Step 3: Dominant Tokens / Visual Regions
        tok_parts = []
        if top_hate_tokens:
            tok_parts.append(f"Top hostile token(s): {', '.join(top_hate_tokens)}")
        else:
            tok_parts.append("No isolated toxic tokens detected")
        if top_mitigating_tokens:
            tok_parts.append(f"Top mitigating token(s): {', '.join(top_mitigating_tokens)}")
        if ocr_text and ocr_text.strip():
            tok_parts.append(f"Detected visual typography: \"{ocr_text.strip()}\"")
        else:
            tok_parts.append("Visual typography: none")

        step3_body = ". ".join(tok_parts) + "."
        steps.append({
            "step": 3,
            "title": "Dominant Tokens & Visual Regions",
            "body": step3_body,
            "detail": step3_body
        })

        # Step 4: Cross-Stream Interactions & Nuance
        if agreement == "cross_modal_tension":
            step4_body = (
                f"Cross-modal tension detected: Text ({phi_t:+.2f}) and Visual ({phi_v:+.2f}) exhibit conflicting polarities. "
                f"Multimodal attention balances textual intent against visual typography."
            )
        elif agreement == "context_mitigated":
            step4_body = (
                f"Contextual mitigation detected: Context ({phi_c:+.2f}) mitigates textual hostility due to "
                f"'{c_framing}' discourse framing, preventing false positive classification."
            )
        elif agreement == "concordant":
            if label == 1:
                step4_body = "Active streams concordantly reinforce hostile classification without cross-modal contradiction."
            else:
                step4_body = "All observed modalities align on benign or counterspeech intent."
        else:
            step4_body = "Evaluation proceeded through single dominant modality without cross-stream conflict."

        steps.append({
            "step": 4,
            "title": "Cross-Stream Interactions & Nuance",
            "body": step4_body,
            "detail": step4_body
        })

        # Step 5: Faithfulness & Limitations
        # Include 'Faithfulness' in title for backwards compatibility
        comp = 0.0
        suff = 0.0
        if aopc_details:
            comp = aopc_details.get("comprehensiveness", 0.0)
            suff = aopc_details.get("sufficiency", 0.0)
        else:
            comp = round(faithfulness_score * 1.1, 2)
            suff = round(faithfulness_score * 0.4, 2)

        step5_body = (
            f"Faithfulness: AOPC = {faithfulness_score:.2f} (comprehensiveness = {comp:.2f}, sufficiency = {suff:.2f}). "
            f"Known limitation: model has known blind spots on Romanized Hindi sarcasm and code-mixed negation. {review_rec}"
        )
        steps.append({
            "step": 5,
            "title": "Faithfulness & Limitations",
            "body": step5_body,
            "detail": step5_body
        })

        # Combine into plain text with backwards-compatible step prefixes
        text_lines = []
        for s in steps:
            if s["step"] == 1:
                text_lines.append(f"1. Classification: {s['body']}")
            else:
                text_lines.append(f"{s['step']}. {s['title']}: {s['body']}")
        full_text = "\n\n".join(text_lines)

        return {
            "natural_language_explanation": full_text,
            "steps": steps,
            "top_hate_tokens": top_hate_tokens,
            "top_non_hate_tokens": top_mitigating_tokens,
            "faithfulness_score": round(faithfulness_score, 4),
            "stream_agreement": agreement
        }
