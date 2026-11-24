import urllib.request, json

url = 'http://127.0.0.1:8000/api/detection/detect-v2'
payload = {
    'text': "Someone wrote 'ye log desh ke gaddar hai' which is completely unacceptable racist hate speech.",
    'explain': True
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as res:
    data = json.loads(res.read().decode('utf-8'))
    print('detect-v2 SUCCESS!')
    print('Label:', data.get('predicted_label'), data.get('label_name'))
    print('Confidence:', data.get('confidence'))
    print('Language:', data.get('language_detected'))
    print('Decision band:', data.get('decision_band'))
    print('Timing:', data.get('timing_ms'))
    print('Has explanation:', bool(data.get('explanation')))

# Also test meme OCR endpoint
url_ocr = 'http://127.0.0.1:8000/api/detection/ocr'
payload_ocr = {'image_path': 'data/raw/images/meme_counter.png'}
req_ocr = urllib.request.Request(url_ocr, data=json.dumps(payload_ocr).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req_ocr) as res:
    data_ocr = json.loads(res.read().decode('utf-8'))
    print('OCR SUCCESS!')
    print('Extracted:', data_ocr.get('extracted_text'))
    print('Lines count:', len(data_ocr.get('lines', [])))
