import requests
import os
import json
from dotenv import load_dotenv

# load .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

print("Loaded API key:", "YES" if DEEPGRAM_API_KEY else "NO")

url = "https://api.deepgram.com/v1/listen"

headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "audio/wav"
}

with open("test.wav", "rb") as f:
    audio = f.read()

params = {
    "model": "nova-2"
}

response = requests.post(
    url,
    headers=headers,
    params=params,
    data=audio
)

data = response.json()

print("\n===== FULL DEEPGRAM RESPONSE =====")
print(json.dumps(data, indent=2))
print("==================================")