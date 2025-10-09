import streamlit as st
from tts import gTTS
import io

st.title("🎙️ Text-to-Speech avec gTTS (gratuit)")

text = st.text_area("Entre ton texte :", "Bonjour, je suis une voix générée par gTTS !")

if st.button("🎧 Générer l’audio"):
    if text.strip():
        tts = gTTS(text, lang="fr")
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.audio(audio_fp, format="audio/mp3")
        st.success("✅ Audio généré avec succès !")
    else:
        st.warning("❗ Entrez un texte avant de générer l’audio.")