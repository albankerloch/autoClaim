import json
import os
from typing import Dict, Tuple
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")


def call_chat_llm(
    system_prompt: str,
    user_message: str,
    json_schema: Dict,
    model: str = "google/gemini-2.5-pro",
    temperature: float = 0.0,
) -> Tuple[Dict, Dict]:
    """Send a chat request with an attached PDF and return the JSON response with usage."""

    messages = [
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": user_message
                },
            ],
        },
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        'provider': {
            'require_parameters': True
        },
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "key-data",
                "strict": True,
                "description": "Extracts key data.",
                "schema": json_schema,
            },
        },
        "temperature": temperature,
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
    json_response = json.loads(content)
    usage = resp.get("usage", {})

    return json_response, usage
