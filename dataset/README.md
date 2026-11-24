# HateLess Unified Multilingual Hate Speech Dataset

Comprehensive multilingual & multimodal dataset for explainable hate speech detection.
Includes English, Devanagari Hindi, and code-mixed Hinglish corpora, along with multimodal meme typography.

## Dataset Structure

```
dataset/
├── raw/                                  # Pristine raw benchmark corpora
│   ├── hasoc_hi_en.jsonl                 # HASOC Hindi-English social media corpus
│   ├── hatexplain_benchmark.jsonl        # HateXplain English benchmark
│   ├── subtle_structural_benchmark.jsonl # Subtle negation & counterspeech samples
│   ├── multimodal_memes.jsonl            # Multimodal meme OCR & image metadata
│   └── images/                           # Benchmark meme images
├── processed/                            # NLP-enriched datasets
│   ├── train.jsonl                       # Stratified training split (70%: 916 samples)
│   ├── val.jsonl                         # Stratified validation split (15%: 195 samples)
│   ├── test.jsonl                        # Stratified holdout test split (15%: 199 samples)
│   ├── all_nlp_processed.jsonl           # Complete dataset with token/lemma enrichments
│   └── all_nlp_processed.csv             # Tabular CSV export
└── dataset_summary.json                  # High-level dataset metadata & distributions
```

## NLP Techniques Applied

1. **Adversarial Cleaning & Normalization**:
   - Unicode NFKC form standardization
   - Zero-width character & invisible formatter stripping
   - Homoglyph translation (Cyrillic & Greek lookalike evasion characters mapped to Latin)
   - Elongation compression (collapses repeated characters e.g. `haaaate` -> `hate`, preserving legitimate double letters)
   - CamelCase hashtag segmentation (`#StopHate` -> `Stop Hate`)

2. **Multilingual Tokenization**:
   - Script-aware tokenization preserving Devanagari combining marks (`ऀ-ॿ`) and English contractions.

3. **Lemmatization**:
   - **English**: NLTK WordNet Lemmatizer with dynamic noun, verb, adjective, and adverb POS mapping (`immigrants` -> `immigrant`, `infecting` -> `infect`, `running` -> `run`).
   - **Hindi (Devanagari)**: Morphological affix-stripping lemmatizer handling inflected verbs (`-ता`, `-ती`, `-ते`, `-ना`, `-ेंगे`) and plural nouns (`-ों`, `-ियां`, `-ें`).
   - **Hinglish (Code-Mixed)**: Transliterated plural suffix mapping (`-on`, `-iyan` -> base) and verbal affix normalization.

4. **Stopword Filtering & Content Token Extraction**:
   - Multilingual stopword catalogs for English, Hindi, and Hinglish. Content lemmas extracted for keyword density analysis.

5. **POS Tagging**:
   - Categorization of tokens into NOUN, VERB, ADJ, ADV, STOP, PUNCT, OTHER.

## Dataset Statistics

- **Total Samples**: 1310
- **Classes**: 725 Non-Hateful / 585 Hateful
- **Languages**: {'en': 981, 'hi': 147, 'hi-en': 182}
- **Modalities**: {'text': 1260, 'meme': 50}
