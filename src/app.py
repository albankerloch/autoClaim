import streamlit as st
from agent import launch_agent
import tempfile
from llm_transcribe import call_transcribe_llm
import os
from gtts import gTTS
import io


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour, je suis votre assistant pour déclarer un sinistre. Décrivez moi votre besoin à l'oral."}
    ]

if "file_key" not in st.session_state:
    st.session_state["file_key"] = 0

if "claim_data" not in st.session_state:
    st.session_state["claim_data"] = {
        "input": "",
        "date_accident": "",
        "ville_accident": "",
        "degats_voiture": "",
        "constat_realise": "",
        "complete": False,
        "answer": ""
    }

st.set_page_config(page_title="Assurance Chat", page_icon="💬")
st.title("Déclaration de Sinistre Automobile")

# Affichage du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["content"].strip():
            tts = gTTS(msg["content"], lang="fr")
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.audio(audio_fp, format="audio/mpeg")

uploaded_file = st.audio_input("Décrivez votre problème (demande d'information ou déclaration de sinistre)", key=st.session_state["file_key"])
if uploaded_file is not None:
    if st.button("Transcrire et envoyer", key="voice_send"):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file.flush()
            prompt = call_transcribe_llm(tmp_file.name)
            os.unlink(tmp_file.name)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state["claim_data"]["input"] = prompt
        st.session_state["claim_data"]["answer"] = ""
        response = launch_agent(st.session_state["claim_data"])
        st.session_state["claim_data"] = response
        st.session_state.messages.append({"role": "assistant", "content": response.get('answer')})
        st.session_state["file_key"] += 1
        st.rerun()