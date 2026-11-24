import re
import requests
import json
from pathlib import Path

def run_benchmark():
    api_url = "http://127.0.0.1:8000/api/detection/detect-v2"
    
    # Representative benchmark subset from tests.md covering key categories
    benchmark_cases = [
        # Cat 1: Direct Hate (English) -> 1
        ("These disgusting illegal immigrants are vermin infecting our country and should be eliminated.", 1, "Direct Hate / Dehumanization"),
        ("All Muslims are violent terrorists who belong in cages, kick them out now.", 1, "Direct Religious Hate"),
        # Cat 2: Direct Hate (Hindi Devanagari) -> 1
        ("ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।", 1, "Devanagari Incitement"),
        ("इन कीड़े-मकौड़ों को हमारे मोहल्ले से भगाओ, ये हमारी संस्कृति को गंदा कर रहे हैं।", 1, "Devanagari Insect Metaphor"),
        # Cat 3: Code-mixed Hate (Hinglish) -> 1
        ("In chutiyon ko desh se bahar phenko, inka koi haq nahi yahan rehne ka.", 1, "Hinglish Vulgar Expulsion"),
        ("Yeh log katue aur suar hain, inko peeto aur bhagao yahan se.", 1, "Hinglish Communal Slurs"),
        # Cat 4: Counterspeech (Quoting slurs to condemn them) -> 0
        ("Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.", 0, "Counterspeech Condemning Slur"),
        ("Calling refugees 'parasites' is a vile and dangerous dehumanization tactic that must stop.", 0, "Counterspeech Refuting Metaphor"),
        ("किसी समुदाय को 'कीड़े-मकौड़े' कहना अत्यंत शर्मनाक और गैरकानूनी है, हम इसकी निंदा करते हैं।", 0, "Hindi Counterspeech"),
        # Cat 5: Academic / Historical -> 0
        ("In historical archives, propaganda used terms like 'subhuman' to systematically dehumanize communities.", 0, "Historical Propaganda Analysis"),
        # Cat 6: News / Law Enforcement -> 0
        ("पुलिस ने सोशल मीडिया पर भड़काऊ और नफरत भरे भाषण देने वाले दो आरोपियों को गिरफ्तार कर लिया है।", 0, "Police Arrest Report Hindi"),
        ("Police arrested two suspects after they shouted 'shoot all immigrants' outside the municipal council.", 0, "Police Arrest Report English"),
        # Cat 8: Casual Swearing (Non-Hateful) -> 0
        ("What the fuck was that glitch, my character fell through the entire game map!", 0, "Gaming Frustration / Benign Swear"),
        # Cat 9: Political Debate -> 0
        ("I strongly oppose the government's new border taxation policy; it hurts small business.", 0, "Civil Policy Debate"),
        # Cat 10: Solidarity -> 0
        ("We must defend human rights, equality, dignity, and mutual respect for all people.", 0, "Universal Human Rights"),
        ("हमारे देश की असली ताकत इसकी विविधता, भाईचारे और शांति में निहित है।", 0, "National Diversity Harmony")
    ]

    print("================================================================================")
    print("RUNNING BENCHMARK EVALUATION ACROSS MULTILINGUAL CATEGORIES")
    print("================================================================================")

    passed = 0
    failed = 0

    for idx, (text, exp_label, category) in enumerate(benchmark_cases, 1):
        payload = {"text": text, "explain": True}
        try:
            resp = requests.post(api_url, json=payload, timeout=25)
            if resp.status_code != 200:
                print(f"[{idx}] FAILED (HTTP {resp.status_code}): {text[:50]}")
                failed += 1
                continue

            data = resp.json()
            pred_lbl = data["predicted_label"]
            conf = data["confidence"]
            expl = data.get("explanation", {})
            nat_exp = expl.get("natural_language_explanation", "")
            shapley = expl.get("shapley_streams", {})
            tokens = expl.get("token_attributions", [])

            is_match = (pred_lbl == exp_label)
            if is_match:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            print(f"[{idx}] {status} | Expected: {exp_label} | Pred: {pred_lbl} ({conf*100:.1f}%) | {category}")
            print(f"     Sentence: \"{text[:65]}...\"" if len(text) > 65 else f"     Sentence: \"{text}\"")
            print(f"     ML Formulation: φ_T={shapley.get('phi_T', 0):+.2f}, φ_V={shapley.get('phi_V', 0):+.2f}, φ_C={shapley.get('phi_C', 0):+.2f} | Agreement: {expl.get('stream_agreement')}")
            print(f"     Verdict Rationale: {nat_exp[:100]}...")
            
            # Print non-neutral tokens
            salient = [f"{t['token']}({t['polarity'][:3]}:{t['score']:+.2f})" for t in tokens if t['polarity'] != 'neutral']
            if salient:
                print(f"     Salient Tokens: {', '.join(salient[:6])}")
            print("-" * 80)

        except Exception as e:
            print(f"[{idx}] EXCEPTION: {e}")
            failed += 1

    print(f"\nFINAL BENCHMARK SCORE: {passed}/{len(benchmark_cases)} PASSED ({(passed/len(benchmark_cases))*100:.1f}%)")

if __name__ == "__main__":
    run_benchmark()
