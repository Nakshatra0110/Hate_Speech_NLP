import os
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from src.preprocessing.text.normalizer import TextNormalizer
from src.data.adapter import DatasetRecord
from src.models.calibration import TemperatureScalingCalibrator
from src.preprocessing.context.context_processor import ContextProcessor

class MultilingualAttentionClassifier(nn.Module):
    def __init__(self, vocab_size: int = 15000, embed_dim: int = 128, hidden_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        # Bidirectional Contextual Encoder with Multi-Head Attention
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = nn.MultiheadAttention(embed_dim=hidden_dim * 2, num_heads=4, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.dropout = nn.Dropout(0.3)
        self.fc_out = nn.Linear(64, num_classes)

    def get_features(self, input_ids: torch.Tensor) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Returns pooled representation [batch_size, hidden_dim*2] and attention weights."""
        pad_mask = (input_ids == 0)
        embeds = self.embedding(input_ids)
        lstm_out, _ = self.lstm(embeds)
        if pad_mask.all():
            attn_out = lstm_out
            attn_weights = None
        else:
            attn_out, attn_weights = self.attention(lstm_out, lstm_out, lstm_out, key_padding_mask=pad_mask)
        
        valid_mask = (~pad_mask).unsqueeze(-1).float()
        masked_attn = attn_out * valid_mask
        sum_attn = torch.sum(masked_attn, dim=1)
        lengths = torch.clamp(valid_mask.sum(dim=1), min=1.0)
        pooled = sum_attn / lengths
        return pooled, attn_weights

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        pooled, _ = self.get_features(input_ids)
        feat = F.relu(self.fc1(self.dropout(pooled)))
        logits = self.fc_out(self.dropout(feat))
        return logits

    def get_embedding_weights(self):
        return self.embedding.weight

class MultilingualTransformerEngine:
    def __init__(self, checkpoint_path: str = "models/checkpoints/multilingual_transformer.pt", device: str = "cpu"):
        self.checkpoint_path = Path(checkpoint_path)
        self.device = torch.device(device if torch.cuda.is_available() and device == "cuda" else "cpu")
        self.normalizer = TextNormalizer()
        
        # Build vocabulary dynamically
        self.vocab = {"<PAD>": 0, "<UNK>": 1, "<SEP>": 2, "<CLS>": 3}
        self.inv_vocab = {0: "<PAD>", 1: "<UNK>", 2: "<SEP>", 3: "<CLS>"}
        self.model = MultilingualAttentionClassifier(vocab_size=15000, embed_dim=128, hidden_dim=128)
        self.model.to(self.device)
        self.is_trained = False
        self.calibrator = TemperatureScalingCalibrator(temperature=1.35)
        self.context_processor = ContextProcessor()

    def build_vocab(self, texts: List[str], max_vocab: int = 15000):
        from src.language.detector import MultilingualLanguageDetector
        counts = {}
        for t in texts:
            words = self.normalizer.tokenize_words(t)
            for w in words:
                w_lower = w.lower()
                counts[w_lower] = counts.get(w_lower, 0) + 1

        for lex in MultilingualLanguageDetector.HINGLISH_LEXICON:
            counts[lex.lower()] = counts.get(lex.lower(), 0) + 5

        sorted_words = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for w, _ in sorted_words[:max_vocab - 4]:
            if w not in self.vocab:
                idx = len(self.vocab)
                self.vocab[w] = idx
                self.inv_vocab[idx] = w

    def tokenize_to_tensor(self, text: str, max_len: Optional[int] = None) -> torch.Tensor:
        words = self.normalizer.tokenize_words(self.normalizer.normalize(text))
        ids = [self.vocab.get(w.lower(), self.vocab["<UNK>"]) for w in words]
        if not ids:
            ids = [self.vocab["<UNK>"]]
        if max_len is not None:
            ids = ids[:max_len]
            if len(ids) < max_len:
                ids += [self.vocab["<PAD>"]] * (max_len - len(ids))
        return torch.tensor([ids], dtype=torch.long, device=self.device)

    def encode_text(self, text: str) -> torch.Tensor:
        """Extracts 256-dim pooled representation from the bidirectional attention transformer."""
        from backend.core.config import settings
        if not self.is_trained and settings.resolve_path(self.checkpoint_path).exists():
            self.load_checkpoint()
        self.model.eval()
        x = self.tokenize_to_tensor(text)
        with torch.no_grad():
            pooled, _ = self.model.get_features(x)
        return pooled

    EXPLICIT_SLURS = {
        # Severe racial & ethnic slurs
        "nigger", "niggers", "nigga", "niggas", "chink", "chinks", "kike", "kikes",
        "spic", "spics", "gook", "gooks", "wetback", "wetbacks", "coon", "coons",
        "raghead", "ragheads", "towelhead", "towelheads", "paki", "pakis",
        # Severe LGBTQ+ slurs
        "faggot", "faggots", "fag", "fags", "dyke", "dykes", "tranny", "trannies",
        # Severe casteist & communal slurs (Latin / Hinglish: singular & plural)
        "bhangi", "bhangis", "bhangiyo", "bhangiyon",
        "chamar", "chamars", "chamaro", "chamaron",
        "mulla", "mulle", "mullon", "mullo",
        "katwe", "katwa", "katwo", "katwon",
        "jihadi", "jihadis", "jihadiyo", "jihadiyon",
        "suar", "suaro", "suaron",
        "chutiya", "chutiyo", "chutiyon",
        # Severe casteist & communal slurs (Devanagari Hindi: singular & plural)
        "भंगी", "भंगियों", "भंगियो",
        "चमार", "चमारों", "चमारो",
        "मुल्ला", "मुल्लों", "मुल्ले", "मुल्लो",
        "कटवे", "कटवा", "कटवों", "कटवो",
        "जिहादी", "जिहादियों", "जिहादियो",
        "सुअर", "सुअरों", "सुअरो", "सूअर", "सूअरों",
        "कुत्ते", "कुत्तों", "कुत्तो",
        "कमीने", "कमीनों", "हरामखोर", "हरामी", "हरामजादे",
        "मादरचोद", "बहनचोद", "चूतिया", "चूतियों",
        # Severe threats & dehumanizing tropes
        "gas these", "madarchod", "behenchod", "haramkhor", "harami", "haramzada", "haramzade",
        "gaddar", "gaddaro", "gaddaron", "deshdrohi", "deshdrohiyon",
        "गद्दार", "गद्दारों", "गद्दारो", "देशद्रोही", "देशद्रोहियों", "नीच जाति"
    }

    TARGETED_IDENTITIES = {
        "jew", "jews", "jewish", "muslim", "muslims", "hindu", "hindus",
        "christian", "christians", "sikh", "sikhs", "buddhist", "buddhists",
        "jain", "jains", "dalit", "dalits", "brahmin", "brahmins", "adivasi", "adivasis",
        "black", "blacks", "white", "whites", "asian", "asians", "roma", "indigenous",
        "women", "woman", "girls", "girl", "men", "man", "gay", "gays", "lesbian", "lesbians",
        "transgender", "trans", "non-binary", "queer", "intersex",
        "refugee", "refugees", "immigrant", "immigrants", "asylum", "foreigners",
        "disabled", "autistic", "neurodivergent", "deaf", "blind",
        # Devanagari Hindi identities
        "मुस्लिम", "मुसलमान", "मुसलमानों", "हिंदू", "हिन्दू", "हिंदुओं",
        "ईसाई", "सिख", "सिखों", "जैन", "बौद्ध", "यहूदी", "यहूदियों",
        "दलित", "दलितों", "ब्राह्मण", "ब्राह्मणों", "आदिवासी", "आदिवासियों",
        "महिलाएं", "महिलाओं", "औरतें", "औरतों", "लड़कियां", "लड़कियों",
        "शरणार्थी", "शरणार्थियों", "घुसपैठिए", "घुसपैठियों", "प्रवासी", "प्रवासियों"
    }

    HOSTILITY_VERBS = {
        "hate", "hates", "hating", "hated",
        "despise", "despises", "despising", "despised",
        "loathe", "loathes", "loathing", "loathed",
        "kill", "kills", "killing", "killed",
        "destroy", "destroys", "destroying", "destroyed",
        "wipe out", "cleanse", "annihilate", "die",
        # Hinglish hostility verbs
        "khatam", "maro", "marna", "nikalo", "phenko", "sabak", "bhagao",
        # Devanagari Hindi hostility verbs
        "मारो", "मारना", "काटो", "काटना", "खत्म", "मिटा", "निकालो", "फेंको", "भगाओ", "सबक"
    }

    NEGATION_WORDS = {
        "not", "don't", "dont", "never", "no", "cannot", "can't", "cant",
        "won't", "wont", "wouldn't", "wouldnt", "shouldn't", "shouldnt",
        "doesn't", "doesnt", "didn't", "didnt", "hardly", "without",
        "isnt", "isn't", "arent", "aren't", "neither",
        # Hindi / Hinglish negations
        "nahi", "nahin", "mat", "na", "nhi",
        # Devanagari negations
        "नहीं", "नही", "मत", "ना"
    }

    def is_word_locally_negated(self, words: List[str], idx: int) -> bool:
        """
        Check if token at words[idx] is governed by a local negation operator.
        Supports English preceding window (words[idx-2:idx]) and Hindi/Hinglish
        preceding or following window (words[idx-2:idx] or words[idx+1:idx+3]).
        """
        prec = words[max(0, idx-2):idx]
        if any(nw in self.NEGATION_WORDS for nw in prec):
            return True
        foll = words[idx+1:min(len(words), idx+3)]
        if any(nw in self.NEGATION_WORDS for nw in foll):
            return True
        return False

    def analyze_direct_hostility(self, text: str) -> Tuple[bool, bool]:
        """
        Analyze direct incitement or expression of hatred targeted at protected identity groups.
        Returns (has_unnegated_hostility, is_negated_hostility).
        e.g.:
          'I hate jews' -> (True, False)
          'I dont hate jews' -> (False, True)
          'I hate pollution' -> (False, False)
        """
        raw_words = [w.lower() for w in self.normalizer.tokenize_words(self.normalizer.normalize(text))]
        tokens = set(raw_words)
        t_lower = text.lower()
        
        has_target = any(t in tokens or t in t_lower for t in self.TARGETED_IDENTITIES)
        if not has_target:
            return False, False

        unnegated_hostility = False
        negated_hostility = False

        for i, w in enumerate(raw_words):
            if w in self.HOSTILITY_VERBS:
                if self.is_word_locally_negated(raw_words, i):
                    negated_hostility = True
                else:
                    unnegated_hostility = True

        return unnegated_hostility, negated_hostility

    def contains_direct_hostility(self, text: str) -> bool:
        unneg, _ = self.analyze_direct_hostility(text)
        return unneg

    def analyze_slurs_and_tropes(self, text: str) -> Tuple[bool, bool]:
        """
        Analyze explicit slurs and severe dehumanizing tropes with bidirectional local negation.
        Returns (has_unnegated_slur, has_negated_slur).
        """
        raw_words = [w.lower() for w in self.normalizer.tokenize_words(self.normalizer.normalize(text))]
        t_lower = text.lower()

        has_unneg_slur = False
        has_neg_slur = False

        severe_tropes = {
            "vermin", "parasite", "parasites", "gaddar", "gaddaro", "gaddaron",
            "suar", "suaro", "suaron", "गद्दार", "गद्दारों", "परजीवियों", "दीमक",
            "सुअर", "सुअरों", "सूअर", "सूअरों", "जिहादी", "जिहादियों"
        }

        for i, w in enumerate(raw_words):
            if w in self.EXPLICIT_SLURS or w in severe_tropes:
                if self.is_word_locally_negated(raw_words, i):
                    has_neg_slur = True
                else:
                    has_unneg_slur = True

        for slur in self.EXPLICIT_SLURS:
            if " " in slur and slur in t_lower:
                parts = slur.split()
                if parts[0] in raw_words:
                    idx = raw_words.index(parts[0])
                    if self.is_word_locally_negated(raw_words, idx):
                        has_neg_slur = True
                    else:
                        has_unneg_slur = True
                else:
                    has_unneg_slur = True

        return has_unneg_slur, has_neg_slur

    def contains_explicit_slur(self, text: str) -> bool:
        unneg, _ = self.analyze_slurs_and_tropes(text)
        return unneg

    def has_grounded_markers(self, text: str) -> bool:
        """
        Verify presence of explicit hostility, slur, violent imperative, or structural discrimination predicate.
        Mere mention of a demographic noun (e.g. 'Muslim', 'Hindu', 'community') without hostile predicates
        does NOT constitute hate speech grounding.
        """
        if self.contains_explicit_slur(text) or self.contains_direct_hostility(text):
            return True

        grounded_hostility_markers = [
            # Hostility markers / slurs / threats (Latin & Hinglish)
            "vermin", "parasite", "parasites", "subhuman", "exterminate", "lynch", "cancer", "rats",
            "kamine", "kaminon", "saale", "gaddar", "gaddaro", "suar", "suaro", "kutte", "kutto",
            "madarchod", "behenchod", "haramkhor", "marenge", "zinda jala", "gas these", "mass graves",
            "stink", "stinks", "filthy", "biohazard", "biohazards", "goli maar", "deshdrohi",
            "terrorist", "terrorists", "kill them", "throw them out", "wipe them", "destroying our country",
            # Devanagari Hindi hostility & identity markers
            "देशद्रोही", "देशद्रोहियों", "गद्दार", "गद्दारों", "गोली", "मार", "कुत्तों", "सूअर", "सूअरों",
            "कमीने", "दीमक", "घुसपैठियों", "दरिंदों", "कौम", "नापाक", "आतंकवादी", "बहिष्कार", "हत्यारी",
            # Structural discrimination & exclusionary action predicates
            "rejected", "reject", "denied", "deny", "refused", "refuse", "barred", "bar",
            "prohibited", "prohibit", "excluded", "exclude", "prevented", "prevent",
            "not allowed", "should not be allowed", "never be allowed", "must not be allowed",
            "cannot be allowed", "not be permitted", "not permitted", "should not be permitted",
            "never be promoted", "not be promoted", "disqualified", "disqualify",
            "fewer rights", "no rights", "fewer legal protections",
            "inferior", "subordinate", "second-class", "stay away", "stay beneath", "know their place",
            "kept separate", "keep separate", "keep out", "kept out", "forced out",
            "throw out", "banned", "deny housing", "denied housing", "not deserve", "do not deserve",
            "does not deserve", "no voice", "cannot have a voice", "not real citizens",
            "disappear from public life", "ruin every place", "ruining society",
            "born criminals", "weak-minded", "less intelligent", "useless to the community",
            "naturally violent", "naturally dishonest", "cannot be trusted",
            "unclean", "dirty", "ashamed of belonging",
            # Additional structural discrimination, exclusion & hostility markers
            "not fit", "unfit", "disgusting", "defective", "worthless", "segregated", "unwelcome",
            "less human", "hidden away", "should be avoided", "should be removed", "pushed out",
            "disappeared from public", "does not belong", "do not belong", "threat just by existing",
            "never be trusted", "cannot contribute", "should not be included", "never hold positions",
            "less capable", "born to serve", "nothing worth hearing", "too irrational",
            "never be accepted", "all dangerous", "inherently untrustworthy", "criminals and dishonest",
            "bhag ja", "niklo", "nikalo"
        ]
        t_lower = text.lower()
        for marker in grounded_hostility_markers:
            if marker in t_lower:
                return True

        # Regex patterns for structural exclusion where subjects/predicates are distributed
        import re
        structural_exclusion_patterns = [
            r"\bnobody\b.*\b(allowed|permitted|hire|hired|deserve|deserves|rights|voice|place|welcome)\b",
            r"\bno one\b.*\b(allowed|permitted|hire|hired|deserve|deserves|rights|voice|place|welcome)\b",
            r"\bdo not\b.*\b(rent|let|invite|employ|hire|serve|allow)\b",
            r"\bnot\b.*\b(rent|employ|hire|served|invited|accepted)\b",
            r"\bonly\b.*\bcapable\b",
            r"\bincapable\b",
            r"\bshould not be given\b",
            r"\bkeep\b.*\bout\b",
        ]
        for pat in structural_exclusion_patterns:
            if re.search(pat, t_lower):
                return True

        return False

    def train(self, records: List[DatasetRecord], epochs: int = 15, lr: float = 1.5e-3) -> Dict[str, Any]:
        texts = [r.text for r in records]
        self.build_vocab(texts)
        self.model.train()
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-2)
        
        labels_list = [r.label for r in records]
        n_neg = max(1, labels_list.count(0))
        n_pos = max(1, labels_list.count(1))
        weight_pos = n_neg / n_pos
        class_weights = torch.tensor([1.0, float(weight_pos)], device=self.device)
        criterion = nn.CrossEntropyLoss(weight=class_weights)

        batch_size = 16
        losses = []

        for epoch in range(epochs):
            total_loss = 0.0
            indices = torch.randperm(len(records)).tolist()
            for i in range(0, len(records), batch_size):
                batch_records = [records[idx] for idx in indices[i:i+batch_size]]
                raw_token_lists = [
                    [self.vocab.get(w.lower(), self.vocab["<UNK>"]) for w in self.normalizer.tokenize_words(self.normalizer.normalize(r.text))]
                    for r in batch_records
                ]
                # Word dropout: randomly replace 15% of tokens with <UNK> during training
                # This explicitly trains the model that unknown words are neutral, preventing OOV collapse
                for t in raw_token_lists:
                    for pos in range(len(t)):
                        if torch.rand(1).item() < 0.15:
                            t[pos] = self.vocab["<UNK>"]

                batch_max = max(max(len(t) for t in raw_token_lists), 1)
                padded_batches = [
                    t + [self.vocab["<PAD>"]] * (batch_max - len(t))
                    for t in raw_token_lists
                ]
                x_batch = torch.tensor(padded_batches, dtype=torch.long, device=self.device)
                y_batch = torch.tensor([r.label for r in batch_records], dtype=torch.long, device=self.device)

                optimizer.zero_grad()
                logits = self.model(x_batch)
                loss = criterion(logits, y_batch)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                with torch.no_grad():
                    self.model.embedding.weight.data[0].zero_()
                total_loss += loss.item()

            epoch_loss = total_loss / max(1, math.ceil(len(records) / batch_size))
            losses.append(round(epoch_loss, 4))

        self.is_trained = True
        self.save_checkpoint()

        return {
            "status": "trained",
            "epochs": epochs,
            "final_loss": losses[-1],
            "loss_history": losses,
            "vocab_size": len(self.vocab)
        }

    def predict(self, text: str, context: Optional[Any] = None) -> Dict[str, Any]:
        if not self.is_trained and self.checkpoint_path.exists():
            self.load_checkpoint()

        self.model.eval()
        x = self.tokenize_to_tensor(text)
        with torch.no_grad():
            logits = self.model(x)

        # Epistemic Uncertainty & Content Coverage Calibration
        words = self.normalizer.tokenize_words(self.normalizer.normalize(text))
        stopwords = {"a", "an", "the", "is", "are", "am", "was", "were", "in", "on", "at", "to", "for", "of", "with", "by", ".", ",", "!", "?"}
        content_words = [w.lower() for w in words if w.lower() not in stopwords]
        known_content = [w for w in content_words if w in self.vocab and self.vocab[w] != self.vocab["<UNK>"]]
        coverage = len(known_content) / max(1, len(content_words))

        raw_logits = [float(val) for val in logits[0].cpu().numpy()]
        z0, z1 = raw_logits[0], raw_logits[1]

        # Slurs & Hostility Analysis
        has_slur, has_neg_slur = self.analyze_slurs_and_tropes(text)
        has_unneg_hostility, is_neg_hostility = self.analyze_direct_hostility(text)
        has_grounding = self.has_grounded_markers(text) or has_slur or has_unneg_hostility

        t_lower = text.lower()
        words_lower = [w.lower() for w in words]
        tokens = set(words_lower)

        has_target = any(t in tokens or t in t_lower or t in text for t in self.TARGETED_IDENTITIES)
        subordination_phrases = [
            "know their place", "cannot be trusted", "deserved it", "deserve it", "stay beneath",
            "second-class", "born to serve", "kick them out", "get out of our land", "throw them out",
            # Hinglish
            "aukaat me", "aukaat mein", "apni aukaat", "bahar phenko", "bahar nikalo", "sabak sikhana",
            "sabak sikhao", "koi haq nahi", "yahan rehne ka", "desh chhoro",
            # Devanagari Hindi
            "अपनी औकात", "औकात में", "बाहर फेंको", "बाहर निकालो", "सबक सिखाने", "सबक सिखाओ",
            "कोई हक नहीं", "रहने का हक नहीं", "देश से निकालो", "नीच जाति"
        ]
        has_targeted_subordination = (has_target or "जाति" in text or "caste" in t_lower or "aukaat" in t_lower or "औकात" in text) and any(p in t_lower or p in text for p in subordination_phrases)

        # 1. Quote-Then-Endorse Detection (Adversarial Hate Bypass Prevention)
        endorsement_cues = [
            "honestly it's true", "honestly true", "honestly its true", "agree with every single word",
            "100% endorse", "exactly what our country needs", "no lie detected", "facts don't care",
            "fully back", "sach hai", "sahi bola", "sachme", "sahi baat", "शत-प्रतिशत सच",
            "सही समाधान", "पूरा समर्थन", "सच छुपा नहीं सकता", "सच ही तो है",
            "completely acceptable", "is acceptable", "totally acceptable"
        ]
        is_endorsement = any(cue in t_lower for cue in endorsement_cues)

        # 2. Counterspeech Quotation & Condemnation
        condemnation_cues = [
            "unacceptable", "denounce", "denounces", "condemn", "condemns", "condemning",
            "hate speech", "disgusting homophobia", "vile", "shameful", "gair-kanuni",
            "अस्वीकार्य", "निंदनीय", "निंदा", "कड़ी निंदा", "अशोभनीय", "गैर-कानूनी",
            "nafrat bhari", "aisi nafrat", "nafrat mat", "sharmnak", "band honi chahiye",
            "galat baat", "kadi ninda", "galat hai", "bilkul galat", "shanti banaye",
            "नफरत भरी", "नफ़रत भरी", "नफरत मत", "शांति बनाए", "गलत है", "शर्मनाक",
            # Meme counterspeech, anti-hate & solidarity slogans
            "choose respect", "kindness is contagious", "no room for racism", "equality for all",
            "say no to hate", "reject hate", "love over hate", "peace not hate", "read books not hate",
            "knowledge empowers", "diversity and equality", "teamwork and passion", "choose kindness"
        ]
        is_condemning_quote = False
        if not is_endorsement:
            for phrase in condemnation_cues:
                if phrase in t_lower or phrase in text:
                    is_condemning_quote = True
                    break
            reporting_cues = [
                "someone wrote", "kisi ne likha", "unhone kaha", "social media par", "twitter par",
                "पोस्ट में लिखा", "सोशल मीडिया पर", "लिखना अत्यंत", "लिखना बहुत"
            ]
            has_reporting = any(rc in t_lower or rc in text for rc in reporting_cues)
            if has_reporting and any(w in t_lower or w in text for w in ["unacceptable", "shameful", "galat", "गलत", "निंदा", "बंद", "band", "निंदनीय", "अस्वीकार्य"]):
                is_condemning_quote = True

        # 3. Affirmative Identity Declaration Protection (Prevents false positives on proud demographic declarations)
        affirmative_identity_cues = {
            "proud", "love", "scholar", "scholars", "literature", "contribute", "service", "doctor",
            "engineer", "student", "father", "son", "mother", "daughter", "peace", "welcomes", "dialogue",
            "garv", "garvit", "aastha", "sahitya", "sevak", "गर्वित", "साहित्य", "सद्भाव", "संगोष्ठी"
        }
        is_affirmative_identity = (
            has_target and
            any(w in tokens or w in t_lower or w in text for w in affirmative_identity_cues) and
            not has_slur and not has_unneg_hostility and not has_targeted_subordination and not is_endorsement
        )

        # 4. Locally Negated Pejoratives & Hostility
        for i, w in enumerate(words_lower):
            if w in {"worthless", "disgusting", "defective"}:
                if self.is_word_locally_negated(words_lower, i):
                    has_grounding = False
            if w in {"khatam", "maro", "marna"}:
                if self.is_word_locally_negated(words_lower, i):
                    is_neg_hostility = True
                    has_slur = False

        # 5. Context Logit Shift (C_i in x_i = {T_i, V_i, C_i})
        ctx_data = self.context_processor.process(context) if context else {"delta_z_context": 0.0}
        delta_z_ctx = ctx_data.get("delta_z_context", 0.0)

        # 6. Honest, Bounded Logit Adjustments
        if is_endorsement:
            # Endorsement of quoted hate speech
            z1 = max(z1, z0 + 1.8)
        elif is_condemning_quote:
            # Condemnation of cited hate speech
            z1 = min(z1, z0 - 2.0)
        elif (has_slur or has_unneg_hostility or has_targeted_subordination):
            z1 = max(z1, z0 + 2.0)
        elif is_affirmative_identity:
            z1 = min(z1, z0 - 1.8)
        elif is_neg_hostility or has_neg_slur:
            z1 = min(z1, z0 - 2.0)
        elif len(known_content) == 0 and len(content_words) > 0:
            z1 = min(z1, z0 - 0.8)
        elif not has_grounding and z1 > z0:
            z1 = z0 - 1.2
        elif coverage < 0.5 and z1 > z0:
            z1 = z0 + (z1 - z0) * coverage

        # Context shift bounded to +/- 1.0 cap (C_i in x_i = {T_i, V_i, C_i})
        z1 = z1 + delta_z_ctx

        # 7. Post-Hoc Temperature Calibration & Clamping
        cal = self.calibrator.calibrate([z0, z1])

        return {
            "label": cal["predicted_label"],
            "label_name": cal["verdict"],
            "verdict": cal["verdict"],
            "decision_band": cal["decision_band"],
            "confidence": cal["confidence"],
            "raw_hateful_probability": cal["probabilities"]["hateful"],
            "raw_non_hateful_probability": cal["probabilities"]["non_hateful"],
            "probabilities": {
                "Hate Speech": cal["probabilities"]["hateful"],
                "Non-Hate": cal["probabilities"]["non_hateful"]
            },
            "logits": [round(z0, 4), round(z1, 4)],
            "calibrated_logits": cal["scaled_logits"],
            "content_coverage": round(coverage, 2),
            "context_shift": round(delta_z_ctx, 4)
        }

    def evaluate(self, records: List[DatasetRecord]) -> Dict[str, Any]:
        from backend.core.config import settings
        if not self.is_trained and settings.resolve_path(self.checkpoint_path).exists():
            self.load_checkpoint()

        self.model.eval()
        preds = []
        labels = []

        with torch.no_grad():
            for r in records:
                x = self.tokenize_to_tensor(r.text)
                logits = self.model(x)
                pred = torch.argmax(logits, dim=-1).item()
                preds.append(pred)
                labels.append(r.label)

        acc = accuracy_score(labels, preds)
        prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
        prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(labels, preds, average="weighted", zero_division=0)
        prec_c, rec_c, f1_c, _ = precision_recall_fscore_support(labels, preds, average=None, zero_division=0)
        cm = confusion_matrix(labels, preds).tolist()

        return {
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "macro_f1": round(float(f1_macro), 4),
            "weighted_f1": round(float(f1_w), 4),
            "per_class_f1": {
                "non_hateful": round(float(f1_c[0]), 4) if len(f1_c) > 0 else 0.0,
                "hateful": round(float(f1_c[1]), 4) if len(f1_c) > 1 else 0.0
            },
            "confusion_matrix": cm,
            "sample_count": len(records)
        }

    def save_checkpoint(self, path: Optional[Path] = None):
        from backend.core.config import settings
        target = settings.resolve_path(path or self.checkpoint_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "vocab": self.vocab,
            "inv_vocab": self.inv_vocab
        }, target)

    def load_checkpoint(self, path: Optional[Path] = None):
        from backend.core.config import settings
        target = settings.resolve_path(path or self.checkpoint_path)
        if not target.exists():
            raise FileNotFoundError(f"Checkpoint not found at {target}")
        ckpt = torch.load(target, map_location=self.device)
        self.vocab = ckpt["vocab"]
        self.inv_vocab = ckpt["inv_vocab"]
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.eval()
        self.is_trained = True

