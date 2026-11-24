import re
from typing import Dict, Any, Optional, List

class ContextProcessor:
    """
    Context Processor (C_i in x_i = {T_i, V_i, C_i}).
    Extracts conversation thread history, identifies framing (educational, hostile, civil),
    and calculates a mathematically bounded context logit shift: Delta z_C in [-1.0, +1.0].
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.mask_demographics = self.config.get("mask_demographic_attributes", True)
        
        self.demographic_pattern = re.compile(
            r"\b(caste|religion|hindu|muslim|christian|sikh|jewish|black|white|male|female|gay|transgender|straight)\b",
            re.IGNORECASE
        )

        self.mitigating_context_keywords = {
            "academic", "curriculum", "research", "archive", "historical", "history",
            "textbook", "syllabus", "dissertation", "court", "legal", "judgment",
            "human rights", "museum", "education", "scholarly", "study", "analysis",
            "counterspeech", "awareness", "prevention"
        }

        self.hostile_context_keywords = {
            "gas them", "finish what was started", "wipe out", "cleanse", "kill them",
            "attack", "destroy", "traitor", "dushman", "maro", "lynch", "hang them",
            "no mercy", "parasites", "vermin", "invaders"
        }

    def process(self, context_obj: Optional[Any]) -> Dict[str, Any]:
        if not context_obj:
            return {
                "has_context": False,
                "formatted_context": "",
                "thread_length": 0,
                "context_framing": "none",
                "delta_z_context": 0.0,
                "confidence": 0.0,
                "sanitized_tokens": []
            }

        thread_history: List[str] = []
        platform = "unknown"
        post_type = "direct"

        if isinstance(context_obj, dict):
            thread_history = context_obj.get("thread_history") or []
            if not thread_history and context_obj.get("formatted_context"):
                thread_history = [context_obj.get("formatted_context")]
            elif not thread_history and context_obj.get("text"):
                thread_history = [context_obj.get("text")]
            platform = context_obj.get("platform", "unknown")
            post_type = context_obj.get("post_type", "direct")
        elif hasattr(context_obj, "thread_history"):
            thread_history = getattr(context_obj, "thread_history") or []
            platform = getattr(context_obj, "platform", "unknown") or "unknown"
            post_type = getattr(context_obj, "post_type", "direct") or "direct"
        elif isinstance(context_obj, str):
            thread_history = [context_obj]

        sanitized_history = []
        raw_text_combined = " ".join(thread_history).lower()

        for turn in thread_history:
            turn_clean = str(turn).strip()
            if self.mask_demographics:
                turn_clean = self.demographic_pattern.sub("[DEMOGRAPHIC_NEUTRAL]", turn_clean)
            if turn_clean:
                sanitized_history.append(turn_clean)

        formatted = " | ".join(sanitized_history)

        # Context Sentiment / Framing Analysis
        has_mitigating = any(k in raw_text_combined for k in self.mitigating_context_keywords)
        has_hostile = any(k in raw_text_combined for k in self.hostile_context_keywords)

        if has_mitigating and not has_hostile:
            framing = "educational_mitigating"
            delta_z = -0.75  # Mitigates hostility for historical/quoted terms
            conf = 0.85
        elif has_hostile and not has_mitigating:
            framing = "hostile_reinforcing"
            delta_z = +0.75  # Elevates hostility
            conf = 0.85
        elif has_hostile and has_mitigating:
            framing = "ambiguous_conflict"
            delta_z = 0.0
            conf = 0.40
        else:
            framing = "neutral_thread"
            delta_z = 0.0
            conf = 0.70

        # Strict mathematical bound: |Delta z_C| <= 1.0
        delta_z = float(max(-1.0, min(1.0, delta_z)))

        return {
            "has_context": len(sanitized_history) > 0,
            "formatted_context": formatted,
            "thread_length": len(sanitized_history),
            "platform": platform,
            "post_type": post_type,
            "context_framing": framing,
            "delta_z_context": delta_z,
            "confidence": conf
        }
