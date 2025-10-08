import streamlit as st
from agent import launch_agent
import tempfile
from faster_whisper import WhisperModel
import os

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour, je suis votre assistant pour déclarer un sinistre. Décrivez l'accident avec un fichier audio."}
    ]

if "file_key" not in st.session_state:
    st.session_state["file_key"] = 0

if "claim_data" not in st.session_state:
    st.session_state["claim_data"] = {
        "input": "",
        "date_accident": "",
        "ville_accident": "",
        "degats_vehicule": "",
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

# Saisie par fichier vocal
uploaded_file = st.file_uploader("Ou envoyez un fichier audio", type=["mp3", "wav", "m4a"], key=st.session_state["file_key"])
# Saisie vocale directe 
# uploaded_file = st.audio_input("Record your answer", key=st.session_state["file_key"])
if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")
    if st.button("Transcrire et envoyer", key="voice_send"):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file.flush()
            model = WhisperModel("small", device="cpu", compute_type="int8")
            segments, info = model.transcribe(tmp_file.name)
            prompt = " ".join([segment.text for segment in segments])
            os.unlink(tmp_file.name)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state["claim_data"]["input"] = prompt
        st.session_state["claim_data"]["answer"] = ""
        response = launch_agent(st.session_state["claim_data"])
        st.session_state["claim_data"] = response
        st.session_state.messages.append({"role": "assistant", "content": response.get('answer')})
        st.session_state["file_key"] += 1
        st.rerun()