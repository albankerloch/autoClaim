import streamlit as st
from elevenlabs import set_api_key, generate, save
import os
from dotenv import load_dotenv

load_dotenv()
EVENTLABS_API_KEY = os.environ.get("EVENTLABS_API_KEY")
if not EVENTLABS_API_KEY:
    raise ValueError("Missing EVENTLABS_API_KEY")

set_api_key(EVENTLABS_API_KEY)

st.title("🎙️ Text-to-Speech avec Evenlabs")

text = st.text_area("Entre ton texte :", "Bonjour, je suis une voix générée par Evenlabs !")

if st.button("🎧 Générer l’audio"):
    if text.strip():
        audio = generate(text, voice="fr-FR-Wavenet-D")
        st.audio(audio, format="audio/wav")
        st.success("✅ Audio généré avec succès !")
    else:
        st.warning("❗ Entrez un texte avant de générer l’audio.")