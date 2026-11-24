import re
import unicodedata
from typing import Dict, Any, List

class TextNormalizer:
    # Homoglyphs commonly used in adversarial evasion (Cyrillic & Greek lookalikes)
    HOMOGLYPH_MAP = {
        'а': 'a', 'с': 'c', 'е': 'e', 'о': 'o', 'р': 'p', 'х': 'x', 'у': 'y',
        'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'К': 'K', 'М': 'M',
        'О': 'O', 'Р': 'P', 'Т': 'T', 'Х': 'X', 'У': 'Y', 'і': 'i', 'І': 'I'
    }

    # Leetspeak translation table
    LEET_MAP = {
        '@': 'a', '4': 'a', '8': 'b', '3': 'e', '1': 'i', '!': 'i', '0': 'o',
        '$': 's', '5': 's', '7': 't', '+': 't', 'v': 'u'
    }

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.unicode_form = self.config.get("unicode_normalization", "NFKC")
        self.clean_urls = self.config.get("clean_urls", True)
        self.preserve_emojis = self.config.get("preserve_emojis", True)

        self.url_pattern = re.compile(r"https?://\S+|www\.\S+")
        self.mention_pattern = re.compile(r"@[\w_]+")
        self.hashtag_pattern = re.compile(r"#([\w_]+)")
        self.zero_width_pattern = re.compile(r"[\u200B-\u200D\uFEFF\u200E\u200F\u00AD]")
        self.multiple_spaces = re.compile(r"\s+")

    def normalize(self, text: str, apply_adversarial_cleaning: bool = True) -> str:
        if not text:
            return ""

        # 1. Unicode NFKC normalization
        text = unicodedata.normalize(self.unicode_form, text)

        # 2. Strip zero-width and invisible formatting characters
        text = self.zero_width_pattern.sub("", text)

        # 3. URL handling
        if self.clean_urls:
            text = self.url_pattern.sub(" [URL] ", text)

        # 4. Mention handling
        text = self.mention_pattern.sub(" [MENTION] ", text)

        # 5. Hashtag handling (split camelCase)
        def _split_hashtag(match):
            tag = match.group(1)
            spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", tag)
            return f" {spaced} "

        text = self.hashtag_pattern.sub(_split_hashtag, text)

        # 6. Adversarial homoglyph mapping
        if apply_adversarial_cleaning:
            # Map Cyrillic/Greek homoglyphs to Latin equivalents
            char_list = [self.HOMOGLYPH_MAP.get(c, c) for c in text]
            text = "".join(char_list)

            # Collapse 3 or more character elongations e.g. "veeeerrrmin" -> "vermin", "nafrrrrat" -> "nafrat"
            # Preserves legitimate doubles (e.g., "good", "book", "gaddar")
            text = re.sub(r"(.)\1{2,}", r"\1", text)

        # 7. Collapse excessive whitespace
        text = self.multiple_spaces.sub(" ", text).strip()

        return text

    def tokenize_words(self, text: str) -> List[str]:
        # Multilingual word tokenizer with Indic / Devanagari combining mark preservation
        return re.findall(r"[\w\u0900-\u097f']+|[^\s\w\u0900-\u097f]", text, re.UNICODE)
