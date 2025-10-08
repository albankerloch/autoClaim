import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

# --- Configuration ---
st.set_page_config(page_title="Assurance Chat", page_icon="💬")
st.title("💬 Agent de Déclaration de Sinistre")

# --- Initialisation du client OpenRouter ou OpenAI ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

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

    # Appel du modèle via OpenRouter
    with st.chat_message("assistant"):
        with st.spinner("Rédaction de la réponse..."):
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Ajouter la réponse dans l’historique
    st.session_state.messages.append({"role": "assistant", "content": reply})
