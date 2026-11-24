import os
import json
import shutil
import csv
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter

from src.preprocessing.nlp_pipeline import NLPPipeline


def build_unified_nlp_dataset():
    """
    Builds the complete `dataset/` directory structure, applies full NLP transformations
    (tokenization, lemmatization, stopword removal, POS tagging) across all corpora,
    and produces stratified train, val, and test splits with summary metadata.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    dataset_dir = root_dir / "dataset"
    raw_out = dataset_dir / "raw"
    images_out = raw_out / "images"
    proc_out = dataset_dir / "processed"

    # Create directories
    raw_out.mkdir(parents=True, exist_ok=True)
    images_out.mkdir(parents=True, exist_ok=True)
    proc_out.mkdir(parents=True, exist_ok=True)

    data_raw_dir = root_dir / "data" / "raw"
    data_images_dir = data_raw_dir / "images"

    # 1. Copy raw datasets & images to dataset/raw/
    if data_images_dir.exists():
        for img in data_images_dir.glob("*.png"):
            shutil.copy2(img, images_out / img.name)

    for jsonl_file in data_raw_dir.glob("*.jsonl"):
        shutil.copy2(jsonl_file, raw_out / jsonl_file.name)

    print(f"Copied raw corpora and images to {raw_out}")

    # 2. Ingest and NLP-enrich every sample
    nlp = NLPPipeline()
    all_processed_records: List[Dict[str, Any]] = []

    # File 1: HASOC Hindi / English
    hasoc_path = raw_out / "hasoc_hi_en.jsonl"
    if hasoc_path.exists():
        with open(hasoc_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                text = d.get("text", "")
                lang_hint = d.get("language")
                nlp_res = nlp.process_text(text, script_hint=lang_hint)
                record = {
                    "id": d.get("id"),
                    "source_corpus": "HASOC-2021",
                    "raw_text": text,
                    "normalized_text": nlp_res["normalized_text"],
                    "language": nlp_res["language"],
                    "tokens": nlp_res["tokens"],
                    "lemmas": nlp_res["lemmas"],
                    "pos_tags": nlp_res["pos_tags"],
                    "clean_tokens_no_stopwords": nlp_res["clean_tokens_no_stopwords"],
                    "token_count": nlp_res["token_count"],
                    "lexical_richness": nlp_res["lexical_richness"],
                    "label": int(d.get("label", 0)),
                    "label_name": "HATEFUL" if int(d.get("label", 0)) == 1 else "NON-HATEFUL",
                    "category": d.get("category", "code_mixed"),
                    "modality": "text",
                    "context": None,
                    "image_path": None,
                    "ocr_text": None
                }
                all_processed_records.append(record)

    # File 2: HateXplain Benchmark
    hatexplain_path = raw_out / "hatexplain_benchmark.jsonl"
    if hatexplain_path.exists():
        with open(hatexplain_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                post_tokens = d.get("post_tokens")
                if isinstance(post_tokens, list):
                    text = " ".join(post_tokens)
                elif isinstance(post_tokens, str):
                    text = post_tokens
                else:
                    text = str(d.get("text", ""))
                nlp_res = nlp.process_text(text, script_hint="en")
                record = {
                    "id": d.get("id"),
                    "source_corpus": "HateXplain",
                    "raw_text": text,
                    "normalized_text": nlp_res["normalized_text"],
                    "language": "en",
                    "tokens": nlp_res["tokens"],
                    "lemmas": nlp_res["lemmas"],
                    "pos_tags": nlp_res["pos_tags"],
                    "clean_tokens_no_stopwords": nlp_res["clean_tokens_no_stopwords"],
                    "token_count": nlp_res["token_count"],
                    "lexical_richness": nlp_res["lexical_richness"],
                    "label": int(d.get("label", 0)),
                    "label_name": "HATEFUL" if int(d.get("label", 0)) == 1 else "NON-HATEFUL",
                    "category": "direct_hate" if int(d.get("label", 0)) == 1 else "civil",
                    "target": d.get("target"),
                    "modality": "text",
                    "context": None,
                    "image_path": None,
                    "ocr_text": None
                }
                all_processed_records.append(record)

    # File 3: Subtle Structural Benchmark (counterspeech, negation, quotes)
    subtle_path = raw_out / "subtle_structural_benchmark.jsonl"
    if subtle_path.exists():
        with open(subtle_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                text = d.get("text", "")
                lang_hint = d.get("language")
                nlp_res = nlp.process_text(text, script_hint=lang_hint)
                record = {
                    "id": d.get("id"),
                    "source_corpus": "Subtle-Structural-Benchmark",
                    "raw_text": text,
                    "normalized_text": nlp_res["normalized_text"],
                    "language": nlp_res["language"],
                    "tokens": nlp_res["tokens"],
                    "lemmas": nlp_res["lemmas"],
                    "pos_tags": nlp_res["pos_tags"],
                    "clean_tokens_no_stopwords": nlp_res["clean_tokens_no_stopwords"],
                    "token_count": nlp_res["token_count"],
                    "lexical_richness": nlp_res["lexical_richness"],
                    "label": int(d.get("label", 0)),
                    "label_name": "HATEFUL" if int(d.get("label", 0)) == 1 else "NON-HATEFUL",
                    "category": d.get("category", "subtle_context"),
                    "modality": "text",
                    "context": d.get("context"),
                    "image_path": None,
                    "ocr_text": None
                }
                all_processed_records.append(record)

    # File 4: Multimodal Memes
    memes_path = raw_out / "multimodal_memes.jsonl"
    if memes_path.exists():
        with open(memes_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                caption = d.get("caption", "")
                ocr_text = d.get("ocr_text", "")
                combined_text = f"{caption} [OCR: {ocr_text}]" if ocr_text else caption
                nlp_res = nlp.process_text(combined_text)
                record = {
                    "id": d.get("id"),
                    "source_corpus": "Multimodal-Memes",
                    "raw_text": combined_text,
                    "normalized_text": nlp_res["normalized_text"],
                    "language": d.get("language", nlp_res["language"]),
                    "tokens": nlp_res["tokens"],
                    "lemmas": nlp_res["lemmas"],
                    "pos_tags": nlp_res["pos_tags"],
                    "clean_tokens_no_stopwords": nlp_res["clean_tokens_no_stopwords"],
                    "token_count": nlp_res["token_count"],
                    "lexical_richness": nlp_res["lexical_richness"],
                    "label": int(d.get("label", 0)),
                    "label_name": "HATEFUL" if int(d.get("label", 0)) == 1 else "NON-HATEFUL",
                    "category": "multimodal_hate" if int(d.get("label", 0)) == 1 else "prosocial_meme",
                    "modality": "meme",
                    "context": d.get("context"),
                    "image_path": d.get("image_path"),
                    "ocr_text": ocr_text
                }
                all_processed_records.append(record)

    print(f"Processed and enriched {len(all_processed_records)} samples with full NLP techniques.")

    # 3. Save all_nlp_processed.jsonl and CSV
    all_jsonl_path = proc_out / "all_nlp_processed.jsonl"
    with open(all_jsonl_path, "w", encoding="utf-8") as f:
        for r in all_processed_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # CSV Export
    all_csv_path = proc_out / "all_nlp_processed.csv"
    with open(all_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "source_corpus", "raw_text", "normalized_text", "language",
            "lemmas", "clean_tokens_no_stopwords", "token_count", "label", "label_name", "category", "modality"
        ])
        for r in all_processed_records:
            writer.writerow([
                r["id"],
                r["source_corpus"],
                r["raw_text"],
                r["normalized_text"],
                r["language"],
                " ".join(r["lemmas"]),
                " ".join(r["clean_tokens_no_stopwords"]),
                r["token_count"],
                r["label"],
                r["label_name"],
                r["category"],
                r["modality"]
            ])

    # 4. Stratified Train (70%), Validation (15%), Test (15%) splits
    import random
    random.seed(42)

    by_class: Dict[int, List[Dict[str, Any]]] = {0: [], 1: []}
    for r in all_processed_records:
        by_class[r["label"]].append(r)

    train_records = []
    val_records = []
    test_records = []

    for lbl, group in by_class.items():
        random.shuffle(group)
        n = len(group)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        
        train_records.extend(group[:n_train])
        val_records.extend(group[n_train:n_train + n_val])
        test_records.extend(group[n_train + n_val:])

    # Shuffle final splits
    random.shuffle(train_records)
    random.shuffle(val_records)
    random.shuffle(test_records)

    with open(proc_out / "train.jsonl", "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(proc_out / "val.jsonl", "w", encoding="utf-8") as f:
        for r in val_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(proc_out / "test.jsonl", "w", encoding="utf-8") as f:
        for r in test_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. Metadata Summary
    lang_counts = dict(Counter(r["language"] for r in all_processed_records))
    class_counts = dict(Counter(r["label_name"] for r in all_processed_records))
    modality_counts = dict(Counter(r["modality"] for r in all_processed_records))
    source_counts = dict(Counter(r["source_corpus"] for r in all_processed_records))

    summary = {
        "dataset_name": "HateLess Unified Multilingual Hate Speech Dataset",
        "total_samples": len(all_processed_records),
        "split_counts": {
            "train": len(train_records),
            "val": len(val_records),
            "test": len(test_records)
        },
        "class_distribution": class_counts,
        "language_distribution": lang_counts,
        "modality_distribution": modality_counts,
        "corpora_distribution": source_counts,
        "nlp_techniques_applied": [
            "Unicode NFKC Normalization",
            "Zero-width character stripping",
            "Homoglyph and leetspeak translation",
            "Phonetic repeated character elongation collapse",
            "CamelCase hashtag segmentation",
            "URL and social mention tokenization",
            "Multilingual word and sentence tokenization",
            "English NLTK WordNet Lemmatization with POS code mapping",
            "Devanagari Hindi morphological affix-based lemmatization",
            "Romanized Hinglish plural and verbal inflection lemmatization",
            "Stopword filtering across English, Hindi, and Hinglish",
            "Part-of-Speech (POS) categorization"
        ]
    }

    with open(dataset_dir / "dataset_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # 6. Dataset README
    readme_content = f"""# HateLess Unified Multilingual Hate Speech Dataset

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
│   ├── train.jsonl                       # Stratified training split (70%: {len(train_records)} samples)
│   ├── val.jsonl                         # Stratified validation split (15%: {len(val_records)} samples)
│   ├── test.jsonl                        # Stratified holdout test split (15%: {len(test_records)} samples)
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
   - Script-aware tokenization preserving Devanagari combining marks (`\u0900-\u097F`) and English contractions.

3. **Lemmatization**:
   - **English**: NLTK WordNet Lemmatizer with dynamic noun, verb, adjective, and adverb POS mapping (`immigrants` -> `immigrant`, `infecting` -> `infect`, `running` -> `run`).
   - **Hindi (Devanagari)**: Morphological affix-stripping lemmatizer handling inflected verbs (`-ता`, `-ती`, `-ते`, `-ना`, `-ेंगे`) and plural nouns (`-ों`, `-ियां`, `-ें`).
   - **Hinglish (Code-Mixed)**: Transliterated plural suffix mapping (`-on`, `-iyan` -> base) and verbal affix normalization.

4. **Stopword Filtering & Content Token Extraction**:
   - Multilingual stopword catalogs for English, Hindi, and Hinglish. Content lemmas extracted for keyword density analysis.

5. **POS Tagging**:
   - Categorization of tokens into NOUN, VERB, ADJ, ADV, STOP, PUNCT, OTHER.

## Dataset Statistics

- **Total Samples**: {len(all_processed_records)}
- **Classes**: {class_counts.get('NON-HATEFUL', 0)} Non-Hateful / {class_counts.get('HATEFUL', 0)} Hateful
- **Languages**: {lang_counts}
- **Modalities**: {modality_counts}
"""
    with open(dataset_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("Successfully built dataset/ folder and summary metadata.")
    return summary


if __name__ == "__main__":
    build_unified_nlp_dataset()
