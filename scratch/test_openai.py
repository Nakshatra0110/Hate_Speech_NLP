import os
import requests

api_key = None
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("OPENAI_API_KEY="):
            api_key = line.strip().split("=", 1)[1].strip()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "Respond with 'API_KEY_VALID'"}
    ],
    "max_tokens": 10
}

resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
print("STATUS:", resp.status_code)
if resp.status_code == 200:
    print("REPLY:", resp.json()["choices"][0]["message"]["content"])
else:
    print("ERROR:", resp.text)
