import re
from typing import Dict, Any

class MultilingualLanguageDetector:
    # Distinct Romanized Hindi (Hinglish) lexicon (excluding common English stop words)
    HINGLISH_LEXICON = {
        # Pronouns & determiners
        "main", "hum", "tum", "aap", "mera", "meri", "mere", "tera", "teri", "tere",
        "iska", "uski", "unka", "inhe", "unhe", "ye", "yeh", "wo", "woh", "kisi", "sab", "sabko",
        # Common particles & conjunctions
        "hai", "hain", "ho", "tha", "the", "thi", "nahi", "nahin", "na", "mat",
        "aur", "ya", "lekin", "par", "kyunki", "isliye", "bhi", "toh",
        "ka", "ki", "ke", "ko", "se", "mein", "pe", "tak",
        # Question words
        "kya", "kyu", "kyun", "kaise", "kaha", "kahan", "kab", "kaun", "kitna", "kitne",
        # Common verbs & auxiliary verbs
        "karo", "karna", "karte", "karti", "kiya", "raha", "rahe", "rahi", "hoga", "honge", "hogi",
        "dekh", "dekho", "bol", "bolo", "bolte", "likha", "likho", "padho", "jao", "aao",
        "khatam", "maro", "marna", "nikalo", "bhejo", "chhoro", "rok", "roko", "phenko", "sabak", "sikhao",
        "hona", "honi", "chahiye", "suno", "bataye", "batao", "samajhna", "pasand",
        # Conversational & affective nouns / adverbs
        "bhai", "yaar", "dost", "desh", "deshvasi", "deshdrohi", "gaddar", "gaddaro", "gaddaron",
        "aukaat", "aukat", "sharam", "sharmnak", "sach", "sacchai", "galat", "sahi", "watan", "mohabbat",
        "bazaar", "ghar", "shahar", "gao", "gaon", "samaj", "samudaay", "bheed", "swasthya",
        "khana", "paani", "pyaar", "nafrat", "khel", "match", "shandar", "mast", "achha", "accha", "badhiya",
        # Slurs and abuse tokens in Hinglish
        "chamar", "chamaro", "chamaron", "bhangi", "bhangiyo", "bhangiyon",
        "mulla", "mulle", "mullo", "mullon", "katwe", "katwa", "katwo", "katwon",
        "jihadi", "jihadis", "jihadiyo", "jihadiyon", "suar", "suaro", "suaron", "kutto", "kutte", "kutton",
        "saala", "saale", "kamine", "kaminon", "haramkhor", "harami", "madarchod", "behenchod", "chutiya", "chutiyon"
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "language": "unknown",
                "script": "Unknown",
                "confidence": 0.0,
                "is_code_mixed": False,
                "is_unsupported": False,
                "unsupported_warning": None,
                "script_breakdown": {"devanagari": 0.0, "latin": 0.0, "arabic": 0.0, "other": 0.0}
            }

        # Analyze scripts by unicode ranges
        devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
        latin_chars = len(re.findall(r"[a-zA-Z]", text))
        arabic_chars = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]", text))
        total_script_chars = devanagari_chars + latin_chars + arabic_chars

        if total_script_chars == 0:
            return {
                "language": "en",
                "script": "Latin",
                "confidence": 0.50,
                "is_code_mixed": False,
                "is_unsupported": False,
                "unsupported_warning": None,
                "script_breakdown": {"devanagari": 0.0, "latin": 0.0, "arabic": 0.0, "other": 1.0}
            }

        dev_ratio = devanagari_chars / total_script_chars
        latin_ratio = latin_chars / total_script_chars
        arabic_ratio = arabic_chars / total_script_chars

        # Check for Unsupported Script: Perso-Arabic (Urdu / Arabic / Sindhi)
        if arabic_ratio > 0.40:
            return {
                "language": "ur",
                "script": "Arabic/Perso-Arabic",
                "confidence": round(arabic_ratio, 3),
                "is_code_mixed": False,
                "is_unsupported": True,
                "unsupported_warning": "Perso-Arabic Urdu text detected. Active model vocabulary does not support Nastaliq/Arabic characters; predictions have high epistemic uncertainty.",
                "script_breakdown": {
                    "devanagari": round(dev_ratio, 3),
                    "latin": round(latin_ratio, 3),
                    "arabic": round(arabic_ratio, 3)
                }
            }

        # Token analysis for Romanized Hindi (Hinglish)
        tokens = [t.lower() for t in re.findall(r"[a-zA-Z]+", text)]
        hinglish_hits = sum(1 for t in tokens if t in cls.HINGLISH_LEXICON)
        hinglish_ratio = (hinglish_hits / len(tokens)) if tokens else 0.0

        # Classification
        if dev_ratio > 0.70:
            lang = "hi"
            script = "Devanagari"
            is_cm = False
            conf = min(0.99, round(0.85 + dev_ratio * 0.14, 3))
        elif dev_ratio > 0.15 and latin_ratio > 0.15:
            lang = "hi-en"
            script = "Mixed (Devanagari + Latin)"
            is_cm = True
            conf = round(0.80 + (dev_ratio * latin_ratio), 3)
        elif latin_ratio > 0.60:
            if hinglish_ratio >= 0.12 or (hinglish_hits >= 2) or (hinglish_hits >= 1 and len(tokens) <= 6):
                lang = "hi-en"
                script = "Latin (Romanized Hindi / Hinglish)"
                is_cm = True
                conf = min(0.95, round(0.65 + hinglish_ratio * 0.35, 3))
            else:
                lang = "en"
                script = "Latin"
                is_cm = False
                conf = round(0.90, 3)
        else:
            lang = "hi-en"
            script = "Mixed"
            is_cm = True
            conf = 0.75

        return {
            "language": lang,
            "script": script,
            "confidence": conf,
            "is_code_mixed": is_cm,
            "is_unsupported": False,
            "unsupported_warning": None,
            "script_breakdown": {
                "devanagari": round(dev_ratio, 3),
                "latin": round(latin_ratio, 3),
                "arabic": round(arabic_ratio, 3),
                "hinglish_lexicon_ratio": round(hinglish_ratio, 3)
            }
        }
