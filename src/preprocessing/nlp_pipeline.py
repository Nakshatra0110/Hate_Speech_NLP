import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple

# Try loading NLTK WordNet Lemmatizer with fallback
try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    _nltk_lemmatizer = WordNetLemmatizer()
except Exception:
    _nltk_lemmatizer = None

from src.preprocessing.text.normalizer import TextNormalizer


class NLPPipeline:
    """
    Production-grade Multilingual NLP Pipeline for Hate Speech Analysis.
    Applies comprehensive NLP techniques:
      - Adversarial normalization & NFKC Unicode cleaning
      - Homoglyph & leetspeak resolution
      - Character elongation collapsing
      - Hashtag segmentation & URL/Mention sanitization
      - Multilingual tokenization (English, Devanagari Hindi, Romanized Hinglish)
      - Lemmatization (WordNet for English, rule-based morphological lemmatizer for Hindi and Hinglish)
      - POS tagging (Part-of-Speech categorization)
      - Stopword filtering and lexical hostility/mitigation tagging
    """

    ENGLISH_STOPWORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
        "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
        "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
        "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
        "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    }

    HINDI_STOPWORDS = {
        "का", "के", "की", "को", "में", "से", "पर", "ने", "और", "है", "हैं", "था", "थे", "थी",
        "यह", "वह", "ये", "वे", "इस", "उस", "इन", "उन", "होना", "होता", "होती", "होते", "किया",
        "गया", "गई", "गए", "भी", "तो", "ही", "तक", "या", "नहीं", "ना", "अपने", "अपनी", "अपना"
    }

    HINGLISH_STOPWORDS = {
        "ka", "ke", "ki", "ko", "se", "me", "mein", "par", "ne", "aur", "hai", "hain", "tha",
        "the", "thi", "yeh", "ye", "woh", "wo", "is", "us", "in", "un", "bhi", "to", "hi",
        "tak", "ya", "nahi", "nahin", "na", "apne", "apni", "apna", "kar", "karta", "karti",
        "karte", "karna", "hoga", "hogi", "honge", "kya", "kyun", "kaise", "kab", "kahan"
    }

    # Morphological suffixes for Hindi (Devanagari)
    HINDI_SUFFIXES = [
        ("ाइयों", "ाई"), ("ाइयाँ", "ाई"), ("ियों", "ी"), ("ियाँ", "ी"),
        ("ारे", "ारा"), ("ाएं", "ा"), ("ाओं", "ा"), ("यों", ""), ("याँ", ""),
        ("ेंगे", "ना"), ("ेगा", "ना"), ("एगी", "ना"),
        ("कर", ""), ("ना", ""), ("ता", ""), ("ती", ""), ("ते", ""),
        ("ा", ""), ("ी", ""), ("े", "ा"), ("ों", ""), ("ें", "")
    ]

    # Morphological suffixes for Hinglish (Romanized Hindi)
    HINGLISH_SUFFIXES = [
        ("tiyon", "tiya"), ("iyon", "iya"), ("iyan", "i"), ("iyen", "i"),
        ("aron", "ar"), ("on", ""),
        ("enge", "na"), ("ega", "na"), ("egi", "na"),
        ("kar", ""), ("ta", ""), ("ti", ""), ("te", ""), ("na", "")
    ]

    def __init__(self, normalizer: Optional[TextNormalizer] = None):
        self.normalizer = normalizer or TextNormalizer()
        self.nltk_lemmatizer = _nltk_lemmatizer

    def detect_script(self, text: str) -> str:
        """Detect dominant linguistic script of text."""
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
        has_latin = bool(re.search(r"[a-zA-Z]", text))
        if has_devanagari and has_latin:
            return "hi-en"
        elif has_devanagari:
            return "hi"
        elif has_latin:
            # Check for high density of Hinglish romanized tokens
            words = text.lower().split()
            hinglish_matches = sum(1 for w in words if w in self.HINGLISH_STOPWORDS)
            if len(words) > 0 and (hinglish_matches / len(words)) > 0.15:
                return "hi-en"
            return "en"
        return "other"

    def simple_pos_tag(self, word: str, script: str) -> str:
        """Infer basic part-of-speech tag using rule heuristics and morphological patterns."""
        w_lower = word.lower()
        if not re.search(r"[\w\u0900-\u097F]", word):
            return "PUNCT"

        if script == "hi":
            if w_lower in self.HINDI_STOPWORDS:
                return "STOP"
            if w_lower.endswith(("ना", "ता", "ती", "ते", "ेंगे", "ेगा", "एगी")):
                return "VERB"
            if w_lower.endswith(("दार", "वान", "शील", "हीन", "जनक")):
                return "ADJ"
            return "NOUN"

        elif script in ("en", "hi-en"):
            if w_lower in self.ENGLISH_STOPWORDS or w_lower in self.HINGLISH_STOPWORDS:
                return "STOP"
            if w_lower.endswith(("ing", "ed", "ize", "ise", "ate")):
                return "VERB"
            if w_lower.endswith(("able", "ible", "ous", "ful", "less", "ive", "al", "ic")):
                return "ADJ"
            if w_lower.endswith(("ly",)):
                return "ADV"
            if w_lower.endswith(("tion", "sion", "ment", "ness", "ity", "ship", "ism", "er", "or")):
                return "NOUN"
            return "NOUN"

        return "OTHER"

    def lemmatize_word(self, word: str, pos: str = "NOUN", script: str = "en") -> str:
        """
        Lemmatize an individual word based on script and POS tag:
          - English: NLTK WordNet Lemmatizer (with noun/verb/adj mapping)
          - Hindi: Rule-based morphological affix stripper
          - Hinglish: Romanized affix mapping + English fallback
        """
        w_lower = word.lower()
        if len(w_lower) <= 2:
            return w_lower

        if script == "hi":
            # Devanagari morphological lemmatization
            for suff, repl in self.HINDI_SUFFIXES:
                if w_lower.endswith(suff) and len(w_lower) > len(suff) + 1:
                    return w_lower[:-len(suff)] + repl
            return w_lower

        if script == "hi-en":
            # Hinglish morphological lemmatization
            for suff, repl in self.HINGLISH_SUFFIXES:
                if w_lower.endswith(suff) and len(w_lower) > len(suff) + 2:
                    return w_lower[:-len(suff)] + repl

        # English or Latin-based WordNet Lemmatization
        if self.nltk_lemmatizer:
            pos_code = 'n'
            if pos == "VERB":
                pos_code = 'v'
            elif pos == "ADJ":
                pos_code = 'a'
            elif pos == "ADV":
                pos_code = 'r'
            try:
                lemma = self.nltk_lemmatizer.lemmatize(w_lower, pos=pos_code)
                # If unchanged and might be plural noun, try noun fallback
                if lemma == w_lower and pos_code != 'n':
                    lemma = self.nltk_lemmatizer.lemmatize(w_lower, pos='n')
                return lemma
            except Exception:
                pass

        # Rule-based fallback for English suffixes
        if w_lower.endswith("ies") and len(w_lower) > 4:
            return w_lower[:-3] + "y"
        if w_lower.endswith("ing") and len(w_lower) > 5:
            return w_lower[:-3]
        if w_lower.endswith("es") and len(w_lower) > 4:
            return w_lower[:-2]
        if w_lower.endswith("s") and not w_lower.endswith("ss") and len(w_lower) > 3:
            return w_lower[:-1]

        return w_lower

    def process_text(self, text: str, script_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute full end-to-end NLP enrichment pipeline over raw text.
        Returns:
          - raw_text: original input
          - normalized_text: Unicode NFKC, de-noised, cleaned text
          - language: detected language / script
          - tokens: list of word tokens
          - lemmas: list of lemmatized base forms
          - pos_tags: inferred POS categories
          - clean_tokens_no_stopwords: content words without stopwords
          - token_count: integer word count
          - lexical_richness: unique lemmas / total tokens ratio
        """
        if not text:
            return {
                "raw_text": "",
                "normalized_text": "",
                "language": "en",
                "tokens": [],
                "lemmas": [],
                "pos_tags": [],
                "clean_tokens_no_stopwords": [],
                "token_count": 0,
                "lexical_richness": 0.0
            }

        norm_text = self.normalizer.normalize(text)
        script = script_hint or self.detect_script(norm_text)
        raw_tokens = self.normalizer.tokenize_words(norm_text)

        tokens = []
        lemmas = []
        pos_tags = []
        clean_content_tokens = []

        # Determine stopword set for filtering
        stopwords_set = self.ENGLISH_STOPWORDS
        if script == "hi":
            stopwords_set = self.HINDI_STOPWORDS
        elif script == "hi-en":
            stopwords_set = self.ENGLISH_STOPWORDS.union(self.HINGLISH_STOPWORDS)

        for tok in raw_tokens:
            tok_clean = tok.strip()
            if not tok_clean:
                continue
            tokens.append(tok_clean)

            # Assign POS Tag
            pos = self.simple_pos_tag(tok_clean, script)
            pos_tags.append(pos)

            # Lemmatize
            lemma = self.lemmatize_word(tok_clean, pos=pos, script=script)
            lemmas.append(lemma)

            # Filter non-alphanumeric punctuation and stopwords
            is_word = bool(re.search(r"[\w\u0900-\u097F]", tok_clean))
            if is_word and tok_clean.lower() not in stopwords_set:
                clean_content_tokens.append(lemma)

        token_count = len(tokens)
        unique_lemmas = len(set(lemmas))
        lexical_richness = round(unique_lemmas / max(1, token_count), 4)

        return {
            "raw_text": text,
            "normalized_text": norm_text,
            "language": script,
            "tokens": tokens,
            "lemmas": lemmas,
            "pos_tags": pos_tags,
            "clean_tokens_no_stopwords": clean_content_tokens,
            "token_count": token_count,
            "lexical_richness": lexical_richness
        }
