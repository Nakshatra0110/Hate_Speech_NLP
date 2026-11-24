import os
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import requests
from src.preprocessing.text.normalizer import TextNormalizer

api_key = None
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("OPENAI_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip()

normalizer = TextNormalizer()
text = "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech."
tokens = normalizer.tokenize_words(normalizer.normalize(text))

system_prompt = """You are an expert multilingual hate speech explainability auditor.
Analyze the given text for hate speech, toxicity, slurs, counterspeech, or civil communication.

Provide a short, crisp explanation of WHY it is hateful or not (NO YAP, NO LARP, NO FLUFF).
Also, for the EXACT sequence of input tokens provided, assign each token an attribution:
- "positive_evidence" (score >= +0.50) if the token is a hostile slur, insult, threat, or hate marker (Red).
- "negative_evidence" (score <= -0.50) if the token is a mitigating, counterspeech, condemnation, prosocial, or law enforcement term (Green).
- "neutral" (score 0.0) if the token is a grammatical stopword, punctuation, or neutral word.

Return valid JSON with schema:
{
  "short_explanation": "Crisp 1-2 sentence explanation of why this content is hateful or non-hateful.",
  "steps": [
    {"step": 1, "title": "Core Finding", "body": "Crisp 1-sentence finding."},
    {"step": 2, "title": "Language & Nuance", "body": "Crisp 1-sentence breakdown of key tokens."},
    {"step": 3, "title": "Verdict Takeaway", "body": "Crisp conclusion."}
  ],
  "token_attributions": [
    {"token": "token_name", "polarity": "positive_evidence"|"negative_evidence"|"neutral", "score": float}
  ]
}
"""

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Full text:\n{text}\n\nExact token sequence:\n{json.dumps(tokens, ensure_ascii=False)}"}
    ],
    "response_format": {"type": "json_object"},
    "temperature": 0.0
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=25)
res = json.loads(resp.json()["choices"][0]["message"]["content"])
print("SHORT EXPLANATION:", res["short_explanation"])
print("STEPS:")
for s in res["steps"]:
    print(f"  {s['step']}. {s['title']}: {s['body']}")
print("TOKENS COUNT:", len(res["token_attributions"]), "EXPECTED:", len(tokens))
for t in res["token_attributions"]:
    print(f"  {t['token']:15s} | {t['polarity']:18s} | {t['score']:+.2f}")
