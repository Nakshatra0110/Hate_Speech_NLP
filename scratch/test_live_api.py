import urllib.request
import json

tests = [
    "These disgusting illegal immigrants are vermin infecting our country and should be eliminated",
    "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.",
    "पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।"
]

for text in tests:
    print("=" * 60)
    print("TEST:", text)
    payload = json.dumps({'text': text, 'explain': True}).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/detection/detect-v2',
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"VERDICT: {data['verdict']} ({data['confidence']*100:.1f}%)")
        expl = data.get('explanation', {})
        print("CRISP EXPLANATION:", expl.get('natural_language_explanation'))
        print("STEPS:")
        for s in expl.get('steps', []):
            print(f"  {s['step']}. {s['title']}: {s['body']}")
        print("TOKEN HEATMAP (Non-neutral):")
        for t in expl.get('token_attributions', []):
            if t['polarity'] != 'neutral':
                print(f"  {t['token']:15s} | {t['polarity']:18s} | {t['score']:+.2f}")
