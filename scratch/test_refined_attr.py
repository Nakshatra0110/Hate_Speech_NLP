import re
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.detection import get_models
from src.preprocessing.nlp_pipeline import NLPPipeline

nlp = NLPPipeline()

HOSTILE_LEXICON = {
    # English
    "stinky", "vermin", "parasite", "parasites", "chutiya", "chutiyon", "chutiyo", "gaddar", "gaddaron",
    "jailed", "kill", "subhuman", "exterminate", "terrorist", "terrorists", "traitor", "traitors",
    "filthy", "dirty", "dog", "suar", "harami", "kutta", "kutte", "kamine", "scum", "infesting",
    "invaders", "threat", "hate", "racist", "slur", "slurs", "disgusting", "infect", "infecting",
    "eliminate", "eliminated", "destroy", "destroyed", "massacre", "massacred", "infestation",
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
    "aukaat", "nafrat"
}

MITIGATING_LEXICON = {
    # English
    "unacceptable", "condemn", "condemns", "condemning", "denounce", "denounces", "false",
    "equality", "solidarity", "kindness", "peace", "respect", "together", "unity", "love",
    "brotherhood", "harmony", "secular", "bhaichara", "shanti", "prosocial", "empowers",
    "empower", "books", "rights", "defend", "dignity", "justice", "inclusion", "inclusive",
    "humanity", "archive", "archives", "historical", "propaganda", "communities", "community",
    "reporting", "police", "arrest", "arrested",
    # Hindi Devanagari
    "विविधता", "भाईचारा", "भाईचारे", "शांति", "सद्भाव", "एकता", "सम्मान", "अधिकार", "बराबरी",
    "समानता", "न्याय", "प्यार", "सुधार", "अस्वीकार्य", "निंदा", "कड़ी निंदा", "पुलिस",
    "गिरफ्तार", "कानून", "न्यायालय", "अदालत",
    # Hinglish
    "bhaichara", "shanti", "sadbhav", "ekta", "samman", "adhikar", "barabari", "insaniyat",
    "sharmnak", "galat", "police", "arrest", "zabardast", "maza"
}

ALL_STOPWORDS = nlp.ENGLISH_STOPWORDS.union(nlp.HINDI_STOPWORDS).union(nlp.HINGLISH_STOPWORDS).union({
    "these", "those", "this", "that", "must", "should", "could", "would", "like", "used", "terms",
    "country", "people", "two",
    "लोग", "देश", "सोशल", "मीडिया", "भाषण", "दो", "आरोपियों", "आरोपी", "वाले", "देने",
    "कर", "लिया", "दिया", "रहा", "रही", "रहे", "हुए", "हुआ", "हुई", "करो", "करें",
    "इनको", "उनको", "इसके", "उसके", "इसकी", "उसकी", "असली", "ताकत", "निहित", "भरे", "पर"
})

sentences = [
    "These disgusting illegal immigrants are vermin infecting our country and should be eliminated",
    "In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities",
    "We must defend human rights and build a community founded on equality, dignity, and mutual respect",
    "ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।",
    "हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है।",
    "पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।"
]

classical_clf, transformer_clf = get_models()

for s in sentences:
    print("=" * 60)
    print("SENTENCE:", s)
    tokens = nlp.normalizer.tokenize_words(nlp.normalizer.normalize(s))
    script = nlp.detect_script(s)
    pred = transformer_clf.predict(s)
    base_logits = pred.get("logits", [0.0, 0.0])
    target_logit = float(base_logits[1] - base_logits[0])
    print(f"VERDICT: {pred['verdict']} | target_logit: {target_logit:+.2f}")

    raw_pert = []
    for i in range(len(tokens)):
        p_words = tokens[:i] + tokens[i+1:]
        p_text = " ".join(p_words) if p_words else "[EMPTY]"
        p_res = transformer_clf.predict(p_text)
        p_logits = p_res.get("logits", [0.0, 0.0])
        pz_diff = float(p_logits[1] - p_logits[0])
        raw_pert.append((tokens[i], float(target_logit - pz_diff)))

    max_abs_dl = max((abs(r[1]) for r in raw_pert), default=1.0)
    norm_factor = max(0.4, max_abs_dl)

    for tok, dl in raw_pert:
        w_lower = tok.lower()
        w_clean = re.sub(r"^[^\w\u0900-\u097F]+|[^\w\u0900-\u097F]+$", "", w_lower)
        has_alpha = bool(re.search(r"[\w\u0900-\u097F]", tok))

        norm_score = round(dl / norm_factor, 4)

        if not has_alpha or not w_clean or w_clean in ALL_STOPWORDS:
            pol = "neutral"
            score = 0.0
        else:
            pos = nlp.simple_pos_tag(w_clean, script)
            lemma = nlp.lemmatize_word(w_clean, pos=pos, script=script)

            if w_clean in HOSTILE_LEXICON or lemma in HOSTILE_LEXICON:
                pol = "positive_evidence"
                score = max(0.55, min(1.0, max(norm_score, 0.55)))
            elif w_clean in MITIGATING_LEXICON or lemma in MITIGATING_LEXICON:
                pol = "negative_evidence"
                score = min(-0.55, max(-1.0, min(norm_score, -0.55)))
            elif target_logit < -1.0:
                pol = "neutral"
                score = 0.0
            elif norm_score >= 0.25:
                pol = "positive_evidence"
                score = min(1.0, norm_score)
            elif norm_score <= -0.25:
                pol = "negative_evidence"
                score = max(-1.0, norm_score)
            else:
                pol = "neutral"
                score = 0.0

        print(f"  {tok:15s} | pol={pol:18s} | score={score:+5.2f} | dl={dl:+6.2f}")
