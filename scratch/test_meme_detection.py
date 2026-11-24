import urllib.request, json

url = 'http://127.0.0.1:8000/api/detection/detect-v2'

for img_file in ['meme_counter.png', 'meme_vermin.png']:
    payload = {
        'image_path': f'data/raw/images/{img_file}',
        'explain': True
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
        print(f"[{img_file}] Result: {data['predicted_label']} ({data['label_name']}) | Conf: {data['confidence']:.4f} | Modalities: {data['modalities_used']}")
