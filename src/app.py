import streamlit as st 
import json
import os
from llm_chat import call_chat_llm
from faster_whisper import WhisperModel
import tempfile
import tempfile

# title of the app
st.title("Déclaration de sinistre Automobile")

# description of the app
st.markdown("""
Cette application permet de déclarer un sinistre automobile en analysant divers facteurs et en fournissant des informations.
""")

# input text area for user to enter details about the claim
st.header("Informations sur le sinistre")
#description = st.text_area("Description de l'accident")
# input audio for user to tell about details about the claim
# audio_data = st.audio_input("Description de l'accident")

uploaded_file = st.file_uploader("Choisissez un fichier audio", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    audio_data = st.audio(uploaded_file, format="audio/mp3")

    if st.button("Soumettre la déclaration"):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file.flush()        
            model = WhisperModel("small", device="cpu", compute_type="int8")
            segments, info = model.transcribe(tmp_file.name)
            text = " ".join([segment.text for segment in segments])        
            os.unlink(tmp_file.name)
        st.write(text)
        st.success("Votre déclaration de sinistre a été soumise avec succès!")
        with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
            json_schema = json.load(f)
        response, usage = call_chat_llm("You are a helpful assistant.", f"Here is an audio transcription. Extract the car claim insurance from the following input: {text}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
        st.write(json.dumps(response, indent=2, ensure_ascii=False))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "..", "data", "output", "claim_details.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)    
        with open(output_path, "w") as f:
            json.dump(response, f)
        st.info("Les détails de votre sinistre ont été enregistrés dans 'claim_details.json'.")

