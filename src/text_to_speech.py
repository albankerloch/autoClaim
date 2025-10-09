import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from elevenlabs.client import ElevenLabs


load_dotenv()
EVENTLABS_API_KEY = os.environ.get("EVENTLABS_API_KEY")
if not EVENTLABS_API_KEY:
    raise ValueError("Missing EVENTLABS_API_KEY")


client = ElevenLabs(
    api_key=EVENTLABS_API_KEY,
    # éventuellement base_url si besoin selon region
)

st.title("🎙️ Text-to-Speech avec Evenlabs")

text = st.text_area("Entre ton texte :", "Bonjour, je suis une voix générée par Evenlabs !")

if st.button("🎧 Générer l’audio"):
    if text.strip():
        audio = client.text_to_speech.convert(
                text=text,
                model_id="eleven_multilingual_v2",
                voice_id="pmISDijbLDrzVXC8fEO0"  # Remplacez par une voix existante
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            for chunk in audio:
                f.write(chunk)
            audio_path = f.name
        st.audio(audio_path, format="audio/mp3")
        st.success("✅ Audio généré avec succès !")
    else:
        st.warning("❗ Entrez un texte avant de générer l’audio.")