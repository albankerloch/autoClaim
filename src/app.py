import streamlit as st 
import json
import os
from llm_chat import call_chat_llm

# title of the app
st.title("Déclaration de sinistre Automobile")

# description of the app
st.markdown("""
Cette application permet de déclarer un sinistre automobile en analysant divers facteurs et en fournissant des informations.
""")

# input fields for user to enter details about the claim
st.header("Informations sur le sinistre")
description = st.text_area("Description de l'accident")

# button to submit the claim
if st.button("Soumettre la déclaration"):
    st.success("Votre déclaration de sinistre a été soumise avec succès!")
    with open("src/types/one-claim.json", "r", encoding="utf-8") as f:
        json_schema = json.load(f)
    response, usage = call_chat_llm("You are a helpful assistant.", f"Here is the CV of a consultant. Extract the car claim insurance from the following input: {description}", json_schema, model="google/gemini-2.5-flash", temperature=0.0)
    st.write(json.dumps(response, indent=2, ensure_ascii=False))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "..", "data", "output", "claim_details.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)    
    with open(output_path, "w") as f:
        json.dump(response, f)
    st.info("Les détails de votre sinistre ont été enregistrés dans 'claim_details.json'.")
	
