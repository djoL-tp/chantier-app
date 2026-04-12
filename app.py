import streamlit as st
from datetime import datetime

st.title("🚜 App Chantier Simple")

chantier = st.text_input("🏗️ Chantier")
client = st.text_input("👤 Client")
engin = st.selectbox("🚜 Engin", ["Mini-pelle", "Chargeur", "Camion"])
travaux = st.text_area("🧱 Travaux")

if "start" not in st.session_state:
    st.session_state.start = None

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Début"):
        st.session_state.start = datetime.now()
        st.success("Démarré")

with col2:
    if st.button("⏸ Pause"):
        st.warning("Pause enregistrée")

with col3:
    if st.button("⏹ Fin"):
        if st.session_state.start:
            end = datetime.now()
            duree = end - st.session_state.start

            st.write("📄 Rapport chantier")
            st.write("Chantier :", chantier)
            st.write("Client :", client)
            st.write("Engin :", engin)
            st.write("Travaux :", travaux)
            st.write("Temps :", duree)

            st.session_state.start = None