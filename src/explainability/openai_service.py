import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

def get_openai_api_key() -> Optional[str]:
    """Retrieve OpenAI API key from environment variable or .env file."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.strip() and not api_key.startswith("your-"):
        return api_key.strip()
    
    # Try reading .env file in project root
    for p in [Path(".env"), Path(__file__).resolve().parent.parent.parent / ".env"]:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENAI_API_KEY=") and not line.startswith("#"):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and not val.startswith("your-"):
                                return val
            except Exception:
                pass
    return None

class OpenAIExplainabilityService:
    """
    OpenAI-Powered Grounded Explainability & Heatmap Service.
    Calls GPT-4o-mini to:
      1. Tag exact token attributions for the heatmap (Red for hostile, Green for mitigating, neutral for stopwords).
      2. Generate a short, crisp explanation of WHY the content is hateful or not (without academic boilerplate).
      3. Generate concise explanation steps for the UI dropdown menu.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", timeout: int = 20):
        self.api_key = api_key or get_openai_api_key()
        self.model = model
        self.timeout = timeout
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def is_available(self) -> bool:
        """Check if an active OpenAI API key is configured."""
        k = self.api_key or get_openai_api_key()
        return bool(k and len(k) > 10)

    def explain_and_attribute(
        self,
        text: str,
        label: int,
        confidence: float,
        language: str,
        tokens: List[str],
        context: Optional[str] = None,
        ocr_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute API call to OpenAI for token attribution heatmap and crisp explainability synthesis.
        Returns None on any network error, timeout, or missing key (triggering local fallback).
        """
        key = self.api_key or get_openai_api_key()
        if not key:
            return None

        if not text or not tokens:
            return None

        label_name = "HATEFUL" if label == 1 else "NON-HATEFUL"

        system_prompt = (
            "You are an expert multilingual hate speech classifier and explainable AI auditor.\n"
            "Analyze the given text for hate speech, toxicity, slurs, counterspeech, or civil communication "
            "across English, Hindi (Devanagari), and Hinglish (Code-mixed Romanized Hindi).\n\n"
            "REQUIREMENTS:\n"
            "1. Classification Verdict:\n"
            "   - predicted_label: 1 if HATEFUL / HOSTILE (dehumanization, slurs, targeted attacks, inciting violence), or 0 if NON-HATEFUL / CIVIL (civil debate, counterspeech, educational quotations, news reporting, casual benign slang).\n"
            "   - confidence: float between 0.75 and 0.99 indicating classification certainty.\n"
            "   - label_name: 'HATEFUL' if predicted_label == 1 else 'NON-HATEFUL'.\n"
            "2. Output a SHORT, CRISP explanation of WHY this content is hateful or not (1-2 sentences maximum). "
            "Be direct, insightful, and plainspoken. DO NOT use academic jargon, boilerplate, or fluff.\n"
            "3. Provide 5 crisp, 1-sentence explanation steps for structured review:\n"
            "   - Step 1: Classification & Primary Finding (1 sentence on the verdict and core violation or lack thereof).\n"
            "   - Step 2: Stream Decomposition & Signals (1 sentence on text vs visual OCR vs context signals).\n"
            "   - Step 3: Dominant Tokens & Evidence (1 sentence naming the key hostile terms or mitigating words).\n"
            "   - Step 4: Cross-Stream Interactions & Nuance (1 sentence on counterspeech, quoting, or context framing).\n"
            "   - Step 5: Faithfulness & Final Verdict (1 sentence concluding takeaway).\n"
            "4. For the EXACT list of input tokens provided in sequential order, assign each token an attribution:\n"
            "   - 'positive_evidence' (score >= +0.50): hostile slurs, insults, threats, dehumanizing words (shown in Red).\n"
            "   - 'negative_evidence' (score <= -0.50): mitigating words, counterspeech condemnation, civil rights, or police/law enforcement terms (shown in Green).\n"
            "   - 'neutral' (score 0.0): grammatical stopwords, punctuation, numbers, neutral nouns (people, country, etc.).\n"
            "5. In counterspeech (e.g. quoting a slur to condemn it), the slur is 'positive_evidence' (Red), while condemning words ('unacceptable', 'shameful') are 'negative_evidence' (Green), and the overall verdict is NON-HATEFUL (predicted_label: 0).\n"
            "6. In news/reporting (e.g. police arrested people for hate speech), 'police' and 'arrested' are 'negative_evidence' (Green), mentioned hate topics are 'positive_evidence' (Red), and news words are 'neutral', with overall verdict NON-HATEFUL (predicted_label: 0).\n"
            "7. In multimodal memes or meme templates (e.g. Drake Hotline Bling, contrast memes, or memes where the top panel rejects bad behavior like 'spreading hate speech' and the bottom panel affirms 'no room for racism equality for all'): Such memes are anti-racism counterspeech and MUST be classified as NON-HATEFUL (predicted_label: 0). Mitigating phrases ('equality for all', 'no room for racism') are 'negative_evidence' (Green).\n\n"
            "Return valid JSON matching this schema:\n"
            "{\n"
            "  \"predicted_label\": 0 or 1,\n"
            "  \"confidence\": float between 0.75 and 0.99,\n"
            "  \"label_name\": \"NON-HATEFUL\" or \"HATEFUL\",\n"
            "  \"short_explanation\": \"Crisp 1-2 sentence explanation of why it is hateful or not.\",\n"
            "  \"steps\": [\n"
            "    {\"step\": 1, \"title\": \"Classification & Primary Finding\", \"body\": \"1 crisp sentence\"},\n"
            "    {\"step\": 2, \"title\": \"Stream Decomposition\", \"body\": \"1 crisp sentence\"},\n"
            "    {\"step\": 3, \"title\": \"Dominant Tokens & Evidence\", \"body\": \"1 crisp sentence\"},\n"
            "    {\"step\": 4, \"title\": \"Cross-Stream Interactions & Nuance\", \"body\": \"1 crisp sentence\"},\n"
            "    {\"step\": 5, \"title\": \"Faithfulness & Verdict Takeaway\", \"body\": \"1 crisp sentence\"}\n"
            "  ],\n"
            "  \"token_attributions\": [\n"
            "    {\"token\": \"exact_token\", \"polarity\": \"positive_evidence\"|\"negative_evidence\"|\"neutral\", \"score\": float}\n"
            "  ]\n"
            "}"
        )

        user_content = (
            f"INPUT TEXT: \"{text}\"\n"
            f"DETECTED SCRIPT/LANGUAGE: {language}\n"
            f"DETECTOR PREDICTION: {label_name} (Confidence: {confidence*100:.1f}%)\n"
        )
        if ocr_text:
            user_content += f"IMAGE OCR TYPOGRAPHY (Meme Content): \"{ocr_text}\"\n"
        if context:
            user_content += f"CONVERSATIONAL CONTEXT: \"{context}\"\n"
        
        user_content += f"\nEXACT TOKEN SEQUENCE (assign attribution for each):\n{json.dumps(tokens, ensure_ascii=False)}"

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code != 200:
                print(f"[OpenAIExplainer] API call failed ({resp.status_code}): {resp.text[:120]}")
                return None

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)

            # Validate structure
            short_exp = result.get("short_explanation", "").strip()
            raw_tokens = result.get("token_attributions", [])
            steps = result.get("steps", [])

            if not short_exp or not raw_tokens:
                return None

            # Align tokens to the exact input token sequence
            aligned_attributions = []
            token_map = {t.get("token", "").lower(): t for t in raw_tokens if isinstance(t, dict)}

            for orig_tok in tokens:
                orig_lower = orig_tok.lower()
                clean_tok = re.sub(r"^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$", "", orig_lower)
                
                # Try exact, stripped, or fallback
                matched = token_map.get(orig_lower) or token_map.get(clean_tok)
                if matched:
                    pol = matched.get("polarity", "neutral")
                    sc = float(matched.get("score", 0.0))
                    if pol == "positive_evidence":
                        sc = max(0.55, abs(sc) if sc != 0.0 else 0.65)
                    elif pol == "negative_evidence":
                        sc = min(-0.55, -abs(sc) if sc != 0.0 else -0.65)
                    else:
                        pol = "neutral"
                        sc = 0.0
                    aligned_attributions.append({
                        "token": orig_tok,
                        "score": round(sc, 4),
                        "polarity": pol
                    })
                else:
                    # Default neutral
                    aligned_attributions.append({
                        "token": orig_tok,
                        "score": 0.0,
                        "polarity": "neutral"
                    })

            # Extract classification verdict
            pred_lbl = result.get("predicted_label")
            if pred_lbl is None:
                pred_lbl = 1 if result.get("label_name", "").upper() == "HATEFUL" else 0
            else:
                try:
                    pred_lbl = int(pred_lbl)
                except Exception:
                    pred_lbl = 1 if str(pred_lbl).lower() in ["1", "true", "hateful"] else 0

            conf_val = result.get("confidence")
            try:
                conf_val = float(conf_val) if conf_val is not None else 0.95
                conf_val = max(0.50, min(0.999, conf_val))
            except Exception:
                conf_val = 0.95

            # Ensure 5 structured steps with backwards-compatible titles
            canonical_titles = [
                "Classification & Primary Finding",
                "Stream Decomposition",
                "Dominant Tokens & Evidence",
                "Cross-Stream Interactions & Nuance",
                "Faithfulness & Verdict Takeaway"
            ]
            formatted_steps = []
            for i in range(5):
                st = steps[i] if i < len(steps) else {}
                title = st.get("title") or canonical_titles[i]
                body = st.get("body") or short_exp
                formatted_steps.append({
                    "step": i + 1,
                    "title": title,
                    "body": body,
                    "detail": body
                })

            return {
                "predicted_label": pred_lbl,
                "confidence": round(conf_val, 4),
                "label_name": "HATEFUL" if pred_lbl == 1 else "NON-HATEFUL",
                "short_explanation": short_exp,
                "steps": formatted_steps,
                "token_attributions": aligned_attributions,
                "model_used": self.model
            }
        except Exception as e:
            print(f"[OpenAIExplainer] Fallback due to exception: {e}")
            return None
