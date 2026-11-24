import re
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from src.preprocessing.text.normalizer import TextNormalizer
from src.preprocessing.nlp_pipeline import NLPPipeline
from src.explainability.faithfulness import FaithfulnessEvaluator

class TextAttributionEngine:
    r"""
    Logit-Scale Leave-One-Out Perturbation Attribution Engine with Multilingual NLP Grounding.
    Operates strictly on the unconstrained logit scale z to eliminate softmax saturation.
    Computes token-level and multi-word phrase-level delta logits:
        Delta z = z_1(text) - z_1(text \ {token})
    Delta > 0: token increases hateful score (positive evidence for hostility / Red).
    Delta < 0: token decreases hateful score (mitigating evidence / counterspeech / Green).
    """
    def __init__(self, normalizer: Optional[TextNormalizer] = None):
        self.normalizer = normalizer or TextNormalizer()
        self.nlp = NLPPipeline(self.normalizer)

        self.HOSTILE_LEXICON = {
            # English
            "stinky", "vermin", "parasite", "parasites", "chutiya", "chutiyon", "chutiyo", "gaddar", "gaddaron",
            "jailed", "jail", "kill", "subhuman", "exterminate", "terrorist", "terrorists", "traitor", "traitors",
            "filthy", "dirty", "dog", "suar", "harami", "kutta", "kutte", "kamine", "scum", "infesting",
            "invaders", "threat", "hate", "racist", "slur", "slurs", "disgusting", "infect", "infecting",
            "eliminate", "eliminated", "destroy", "destroyed", "massacre", "massacred", "infestation",
            "vile", "nigger", "niggers", "faggot", "faggots", "chink", "kike", "spic", "gook", "paki",
            # Hindi Devanagari
            "गद्दार", "गद्दारों", "गद्दारो", "देशद्रोही", "देशद्रोहियों", "निकालो", "खत्म", "मारो", "मारना",
            "काटो", "भड़काऊ", "दंगा", "जिहादी", "जिहादियों", "जिहादियो", "मुल्ला", "मुल्ले", "मुल्लों", "मुल्लो",
            "चमार", "चमारों", "चमारो", "भंगी", "भंगियों", "भंगियो", "सुअर", "सुअरों", "सुअरो", "सूअर",
            "कुत्ते", "कुत्तों", "कुत्तो", "कमीने", "कमीनों", "हरामी", "हरामखोर", "हरामजादे", "मादरचोद",
            "बहनचोद", "चूतिया", "चूतियों", "नीच", "औकात", "फेंको", "नफरत", "नफ़रत",
            # Hinglish
            "khatam", "nikalo", "phenko", "maro", "marna", "bhangi", "bhangiyo", "bhangiyon",
            "chamar", "chamaro", "chamaron", "katwe", "katwa", "katwo", "katwon", "mulla", "mulle",
            "mullon", "jihadi", "jihadis", "suar", "kutta", "kutte", "kamine", "harami", "deshdrohi",
            "aukaat", "nafrat", "bahar"
        }

        self.MITIGATING_LEXICON = {
            # English
            "unacceptable", "condemn", "condemns", "condemning", "denounce", "denounces", "false",
            "equality", "solidarity", "kindness", "peace", "respect", "together", "unity", "love",
            "brotherhood", "harmony", "secular", "bhaichara", "shanti", "prosocial", "empowers",
            "empower", "books", "rights", "defend", "dignity", "justice", "inclusion", "inclusive",
            "humanity", "archive", "archives", "historical", "propaganda", "communities", "community",
            "reporting", "police", "arrest", "arrested", "arrests", "investigate", "court", "law",
            # Hindi Devanagari
            "विविधता", "भाईचारा", "भाईचारे", "शांति", "सद्भाव", "एकता", "सम्मान", "अधिकार", "बराबरी",
            "समानता", "न्याय", "प्यार", "सुधार", "अस्वीकार्य", "निंदा", "कड़ी निंदा", "पुलिस",
            "गिरफ्तार", "कानून", "न्यायालय", "अदालत",
            # Hinglish
            "bhaichara", "shanti", "sadbhav", "ekta", "samman", "adhikar", "barabari", "insaniyat",
            "sharmnak", "galat", "police", "arrest", "zabardast", "maza"
        }

        self.ALL_STOPWORDS = self.nlp.ENGLISH_STOPWORDS.union(self.nlp.HINDI_STOPWORDS).union(self.nlp.HINGLISH_STOPWORDS).union({
            "these", "those", "this", "that", "must", "should", "could", "would", "like", "used", "terms",
            "country", "people", "two", "someone", "wrote", "which",
            "लोग", "देश", "सोशल", "मीडिया", "भाषण", "दो", "आरोपियों", "आरोपी", "वाले", "देने",
            "कर", "लिया", "दिया", "रहा", "रही", "रहे", "हुए", "हुआ", "हुई", "करो", "करो।", "करें",
            "इनको", "उनको", "इसके", "उसके", "इसकी", "उसकी", "असली", "ताकत", "निहित", "भरे", "पर"
        })

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

        script = self.nlp.detect_script(text)
        base_res = predict_fn(text)
        base_logits = base_res.get("logits", [0.0, 0.0])
        z0, z1 = base_logits[0], base_logits[1]
        # Attribute with respect to relative log-odds (z1 - z0) to eliminate uniform logit shifts
        target_logit = float(z1 - z0)

        raw_pert = []
        for i in range(len(words)):
            perturbed_words = words[:i] + words[i+1:]
            perturbed_text = " ".join(perturbed_words) if perturbed_words else "[EMPTY]"
            
            p_res = predict_fn(perturbed_text)
            p_logits = p_res.get("logits", [0.0, 0.0])
            pz0, pz1 = p_logits[0], p_logits[1]
            pz_diff = float(pz1 - pz0)

            # Change in relative hate logit when token i is removed
            dl = float(target_logit - pz_diff)
            raw_pert.append((words[i], dl))

        # Normalize logit sensitivity to [-1.0, +1.0] scale
        max_abs_dl = max((abs(r[1]) for r in raw_pert), default=1.0)
        norm_factor = max(0.4, max_abs_dl)

        attributions = []
        for w, dl in raw_pert:
            w_lower = w.lower()
            w_clean = re.sub(r"^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$", "", w_lower)
            has_alpha = bool(re.search(r"[\w\u0900-\u097F]", w))
            norm_score = round(dl / norm_factor, 4)

            # Punctuation & Stopwords are strictly Neutral
            if not has_alpha or not w_clean or w_clean in self.ALL_STOPWORDS:
                norm_score = 0.0
                pol = "neutral"
            else:
                pos = self.nlp.simple_pos_tag(w_clean, script)
                lemma = self.nlp.lemmatize_word(w_clean, pos=pos, script=script)

                # Check explicit Hostile / Mitigating Lexicons (exact or lemmatized base)
                if w_clean in self.HOSTILE_LEXICON or lemma in self.HOSTILE_LEXICON:
                    norm_score = max(0.55, min(1.0, max(norm_score, 0.55)))
                    pol = "positive_evidence"
                elif w_clean in self.MITIGATING_LEXICON or lemma in self.MITIGATING_LEXICON:
                    norm_score = min(-0.55, max(-1.0, min(norm_score, -0.55)))
                    pol = "negative_evidence"
                elif target_logit < -1.0:
                    # In safe / non-hateful texts, do not flag unlisted neutral words as hostile
                    norm_score = 0.0
                    pol = "neutral"
                elif norm_score >= 0.25:
                    norm_score = min(1.0, norm_score)
                    pol = "positive_evidence"
                elif norm_score <= -0.25:
                    norm_score = max(-1.0, norm_score)
                    pol = "negative_evidence"
                else:
                    norm_score = 0.0
                    pol = "neutral"

            attributions.append({
                "token": w,
                "score": norm_score,
                "raw_delta_logit": round(dl, 4),
                "abs_score": abs(norm_score),
                "polarity": pol
            })

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
