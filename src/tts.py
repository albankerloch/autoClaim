import streamlit as st
from elevenlabs import set_api_key, generate, save

set_api_key("sk_82fc19b9dd1c51bc01b5325a59c719cca11c694ae7e8b3b6") 

st.title("🎙️ Text-to-Speech avec Evenlabs")

text = st.text_area("Entre ton texte :", "Bonjour, je suis une voix générée par Evenlabs !")

if st.button("🎧 Générer l’audio"):
    if text.strip():
        audio = generate(text, voice="fr-FR-Wavenet-D")
        st.audio(audio, format="audio/wav")
        st.success("✅ Audio généré avec succès !")
    else:
        st.warning("❗ Entrez un texte avant de générer l’audio.")