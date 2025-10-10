import json
import os
from typing import Dict, Tuple
import requests
from dotenv import load_dotenv
from datetime import datetime
import uuid
import sqlite3

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

# Initialiser la base de données SQLite pour le logging
def init_logging_db():
    conn = sqlite3.connect('llm_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_calls (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            app_id TEXT,
            model TEXT,
            system_prompt TEXT,
            user_message TEXT,
            response TEXT,
            usage TEXT,
            temperature REAL
        )
    ''')
    conn.commit()
    conn.close()

init_logging_db()

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

    # Logger dans notre propre base de données
    try:
        conn = sqlite3.connect('llm_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO llm_calls (id, timestamp, app_id, model, system_prompt, user_message, response, usage, temperature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            datetime.now().isoformat(),
            "llm_chat_app",
            model,
            system_prompt[:500],
            user_message[:500],
            json.dumps(json_response),
            json.dumps(usage),
            temperature
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erreur logging: {e}")

    return json_response, usage