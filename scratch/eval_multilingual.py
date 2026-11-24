import sys
sys.path.insert(0, ".")
from backend.api.detection import detect_content
from backend.schemas.detection import DetectionRequest

sentences = [
    # English Civil
    ("en", "Good morning! Wishing everyone a peaceful and productive day.", 0),
    ("en", "I really love learning about different cultures and cuisines around the world.", 0),
    ("en", "The conference highlighted the contributions of immigrant scientists to modern medicine.", 0),
    ("en", "We must protect human rights and support vulnerable communities across the nation.", 0),
    
    # English Hateful
    ("en", "These disgusting immigrants are vermin infecting our country and must be eradicated.", 1),
    ("en", "All of these subhuman creatures should be kicked out of our land permanently.", 1),
    ("en", "They are parasites living off our taxes, eliminate them now.", 1),
    
    # English Counterspeech / Negation / Quoted
    ("en", "Someone wrote 'immigrants are vermin' which is completely unacceptable racist hate speech.", 0),
    ("en", "We strongly condemn anyone who uses slurs like that to attack minority groups.", 0),
    ("en", "It is illegal and vile to call people subhuman parasites.", 0),
    
    # Hinglish Civil
    ("en/hi-en", "Bhai aaj ka cricket match kitna shandar tha, maza aa gaya!", 0),
    ("en/hi-en", "Hum sabko milkar apne desh ko aage le jana chahiye, sabhi dharmo ka aadar karo.", 0),
    ("en/hi-en", "Aapka bahut bahut dhanyawad itni achhi madad karne ke liye dost.", 0),
    ("en/hi-en", "Mujhe naye logo se milna aur unki baatein samajhna bahut pasand hai.", 0),
    ("en/hi-en", "Main ek proud Muslim hoon aur mujhe apne watan se beinteha mohabbat hai.", 0),
    ("en/hi-en", "Garv se kaho hum sab ek hain, unity in diversity hamari pehchan hai.", 0),
    
    # Hinglish Hateful
    ("hi-en", "ye log desh ke gaddar hai, inko maro aur yahan se bhagao", 1),
    ("hi-en", "In katwo aur mullon ko sabak sikhana padega, desh chhoro", 1),
    ("hi-en", "In bhangiyon aur chamaro ki koi aukaat nahi hai, inko bahar phenko", 1),
    ("hi-en", "Ye suar hamare desh ko kharab kar rahe hain, inko khatam karo", 1),
    ("hi-en", "In chutiyon ko yahan se nikal bahar karo, gaddaro ko sabak sikhao", 1),

    # Hinglish Counterspeech / Reporting
    ("hi-en", "Kisi ne likha 'ye log desh ke gaddar hai', aisi nafrat bhari baatein band honi chahiye.", 0),
    ("hi-en", "Aise slurs use karna bilkul galat aur sharmnak hai, nafrat mat failao.", 0),
    ("hi-en", "Unhone kaha ki inko maro, jo ki gair-kanuni aur ashobhniya hai.", 0),

    # Hindi (Devanagari) Civil
    ("hi", "नमस्ते दोस्तों, आशा है कि आपका दिन बहुत शुभ और मंगलमय हो।", 0),
    ("hi", "हमारे देश की असली ताकत इसकी विविधता और भाईचारे में निहित है।", 0),
    ("hi", "शिक्षा और स्वास्थ्य हर नागरिक का मौलिक अधिकार होना चाहिए।", 0),
    ("hi", "मैं एक गर्वित भारतीय नागरिक हूँ और समाज की सेवा करना चाहता हूँ।", 0),

    # Hindi (Devanagari) Hateful
    ("hi", "ये लोग देश के गद्दार हैं, इनको देश से निकालो और खत्म करो।", 1),
    ("hi", "इन सुअरों और जिहादियों को सबक सिखाने का समय आ गया है।", 1),
    ("hi", "नीच जाति के लोगों को अपनी औकात में रहना चाहिए, बाहर फेंको इनको।", 1),
    ("hi", "इन परजीवियों को हमारे समाज से मिटा देना चाहिए, कोई दया नहीं।", 1),

    # Hindi (Devanagari) Counterspeech / Condemnation
    ("hi", "सोशल मीडिया पर 'ये लोग देश के गद्दार हैं' लिखना अत्यंत निंदनीय और अस्वीकार्य है।", 0),
    ("hi", "हम किसी भी समुदाय के खिलाफ नफरत फैलाने वाले भाषण की कड़ी निंदा करते हैं।", 0),
    ("hi", "दूसरों को गाली देना और नीचा दिखाना हमारी संस्कृति नहीं है, शांति बनाए रखें।", 0)
]

correct = 0
failed = []

for expected_lang, text, expected_label in sentences:
    req = DetectionRequest(text=text, explain=True)
    res = detect_content(req)
    is_correct = (res.predicted_label == expected_label)
    if is_correct:
        correct += 1
    else:
        failed.append((text, expected_label, res.predicted_label, res.confidence, res.language_detected))
    mark = "OK" if is_correct else "FAIL"
    print(f"[{mark}] [{res.language_detected}] Exp={expected_label} Got={res.predicted_label} ({res.confidence:.2f}) | {text[:50]}")

print(f"\nSummary: {correct}/{len(sentences)} correct ({correct/len(sentences)*100:.1f}%)")
if failed:
    print("\nFailures:")
    for text, exp, got, conf, lang in failed:
        print(f"  Exp {exp} got {got} (conf={conf:.2f}, lang={lang}): {text}")
