import streamlit as st 

# title of the app
st.title("Déclaration de sinistre Automobile")

# description of the app
st.markdown("""
Cette application permet de déclarer un sinistre automobile en analysant divers facteurs et en fournissant des informations.
""")

# input fields for user to enter details about the claim
st.header("Informations sur le sinistre")
date_of_accident = st.date_input("Date de l'accident")
location = st.text_input("Lieu de l'accident")
description = st.text_area("Description de l'accident")
vehicle_damage = st.selectbox("Dommages au véhicule", ["Léger", "Modéré", "Grave"])
injuries = st.selectbox("Blessures", ["Aucune", "Légères", "Graves"])
police_report = st.checkbox("Constat réalisé")

# button to submit the claim
if st.button("Soumettre la déclaration"):
    st.success("Votre déclaration de sinistre a été soumise avec succès!")
    st.write("Détails du sinistre:")
    st.write(f"Date de l'accident: {date_of_accident}")
    st.write(f"Lieu de l'accident: {location}")
    st.write(f"Description: {description}")
    st.write(f"Dommages au véhicule: {vehicle_damage}")
    st.write(f"Blessures: {injuries}")
    st.write(f"Constat réalisé: {'Oui' if police_report else 'Non'}")
