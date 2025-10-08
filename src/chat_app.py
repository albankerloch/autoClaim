import streamlit as st
from agent import launch_agent
from dataclasses import dataclass

@dataclass
class State:
    input: str
    date_accident: str
    ville_accident: str
    degats_vehicule: str
    constat_realise: str
    complete: str
    answer: str

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

# --- Configuration ---
st.set_page_config(page_title="Assurance Chat", page_icon="💬")
st.title("Déclaration de Sinistre")


# --- Historique de conversation ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour, je suis votre assistant pour déclarer un sinistre. Pouvez-vous m’en dire plus ?"}
    ]

# --- Affichage des messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Entrée utilisateur ---
if prompt := st.chat_input("Votre message..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Appel de l'agent et affichage de la réponse
    with st.chat_message("assistant"):
        with st.spinner("Rédaction de la réponse..."):
            print("Prompt utilisateur :", prompt)
            claim = st.session_state.get("claim_data", {})
            print("Données du sinistre avant l'agent :", claim)
            print(type(claim))
            claim["input"] = prompt
            claim["answer"] = ""
            print("Données du sinistre juste avant l'agent :", claim)
            response = launch_agent(claim)
            st.session_state["claim_data"] = response
            st.markdown(response['answer'])
            print("Réponse de l'agent :", st.session_state.get("claim_data", {}))

    # Ajouter la réponse dans l’historique
    st.session_state.messages.append({"role": "assistant", "content": response.get('answer')})
