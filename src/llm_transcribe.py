import os
from typing import Dict, Tuple
import requests
from dotenv import load_dotenv
import base64

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

def encode_audio_to_base64(audio_path):
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')
    
def call_transcribe_llm(
    audio_path: str,
    model: str = "google/gemini-2.5-flash",
) -> Tuple[Dict, Dict]:
    """Send a transcription request to the LLM."""

    base64_audio = encode_audio_to_base64(audio_path)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": "Transcrire cet audio."
                },
                {
                "type": "input_audio",
                "input_audio": {
                    "data": base64_audio,
                    "format": "wav"
                }
            }
            ],
        },
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    try:
        resp = response.json()
    except Exception as e:
        print("Error decoding JSON response:", e)
        print("Raw response text:\n", response.text)
        raise RuntimeError(f"LLM request failed: Could not decode JSON. Raw response: {response.text}")
    
    if response.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp}")
    
    content = resp["choices"][0]["message"]["content"]

    return content


if __name__ == "__main__":
    audio_path = "/root/autoClaim/data/input/comment_faire.mp3"
    audio_path = "/tmp/tmpbvueaml9.wav"
    resp = call_transcribe_llm(audio_path)
    content = resp["choices"][0]["message"]["content"]
    print("Transcription Response:", content)
