import os
import json
import requests

api_key = None
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("OPENAI_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip()

test_sentences = [
    "These disgusting illegal immigrants are vermin infecting our country and should be eliminated",
    "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.",
    "पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।"
]

system_prompt = """You are an expert multilingual hate speech and explainable AI auditor.
Analyze the given text for hate speech, toxicity, slurs, counterspeech, or civil communication across English, Hindi (Devanagari), and Hinglish (Code-mixed).

You must output valid JSON with this exact schema:
{
  "verdict": "HATEFUL" or "NON-HATEFUL",
  "confidence": float between 0.50 and 0.99,
  "short_explanation": "Short, crisp 1-2 sentence explanation of WHY it is hateful or not (NO YAP, NO LARP, NO PSEUDO-ACADEMIC JARGON, purely direct and insightful).",
  "explanation_steps": [
    {
      "step": 1,
      "title": "Short Title",
      "body": "Crisp 1-sentence finding on why it is hateful or not."
    },
    {
      "step": 2,
      "title": "Language & Nuance",
      "body": "Crisp 1-sentence breakdown of key tokens, slurs, counterspeech, or reporting context."
    },
    {
      "step": 3,
      "title": "Verdict Justification",
      "body": "Crisp concluding takeaway."
    }
  ],
  "token_attributions": [
    {
      "token": "exact word token as it appears in the text",
      "polarity": "positive_evidence" (if hateful/hostile -> Red) OR "negative_evidence" (if mitigating/counterspeech/prosocial -> Green) OR "neutral" (if stopword/grammar/neutral),
      "score": float in range [-1.0, 1.0] (positive for hateful, negative for mitigating/prosocial, 0.0 for neutral)
    }
  ]
}

CRITICAL RULES FOR TOKEN HEATMAP:
1. Punctuation (commas, periods, quotes) and purely grammatical stopwords (is, are, to, the, and, ne, ko, se, aur, hai, etc.) MUST have polarity "neutral" and score 0.0.
2. Slurs, insults, threats, and dehumanizing terms MUST have polarity "positive_evidence" and score >= 0.50 (e.g. vermin, gaddar, chutiya, disgusting, infecting, eliminated).
3. Mitigating terms, condemnation of hate, civil rights terms, and law enforcement actions (unacceptable, equality, condemn, dignity, peace, police, arrested) MUST have polarity "negative_evidence" and score <= -0.50.
4. Maintain the exact tokens from the input text in sequential order.
5. In counterspeech (e.g., quoting a slur to condemn it), the quoted slur itself is positive_evidence (Red), while the condemning words ('unacceptable', 'denounce') are negative_evidence (Green), and the overall verdict is NON-HATEFUL.
"""

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

for s in test_sentences:
    print("=" * 60)
    print("TEST:", s)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this text:\n\n{s}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
    data = resp.json()
    res = json.loads(data["choices"][0]["message"]["content"])
    print("VERDICT:", res["verdict"], f"({res['confidence']*100:.1f}%)")
    print("SHORT EXPLANATION:", res["short_explanation"])
    print("STEPS:")
    for st in res["explanation_steps"]:
        print(f"  Step {st['step']}: {st['title']} -> {st['body']}")
    print("TOKEN HEATMAP:")
    for t in res["token_attributions"]:
        if t["polarity"] != "neutral":
            print(f"  {t['token']:15s} | {t['polarity']:18s} | {t['score']:+.2f}")
