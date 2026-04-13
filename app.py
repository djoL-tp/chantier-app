import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="V17 PRO MAX", layout="centered")

# ------------------------
# INIT
# ------------------------
if "data" not in st.session_state:
    st.session_state.data = []

st.title("📋 V17 PRO MAX")

# ------------------------
# FORMULAIRE
# ------------------------
with st.form("formulaire", clear_on_submit=True):

    date = st.date_input("📅 Date", datetime.today())
    ouvrier = st.text_input("👷 Ouvrier")
    chantier = st.text_input("🏗️ Chantier")
    heure_debut = st.time_input("⏰ Heure début")
    heure_fin = st.time_input("⏰ Heure fin")
    description = st.text_area("📝 Description")

    submit = st.form_submit_button("Enregistrer")

# ------------------------
# DEBUG
# ------------------------
st.write("📦 Données actuelles :", st.session_state.data)

# ------------------------
# SAVE
# ------------------------
if submit:
    debut = datetime.combine(date, heure_debut)
    fin = datetime.combine(date, heure_fin)

    if fin <= debut:
        st.error("❌ Heure fin invalide")
    else:
        duree = (fin - debut).total_seconds() / 3600

        st.session_state.data.append({
            "date": date.strftime("%d/%m/%Y"),
            "ouvrier": ouvrier,
            "chantier": chantier,
            "debut": heure_debut.strftime("%H:%M"),
            "fin": heure_fin.strftime("%H:%M"),
            "duree": round(duree, 2),
            "description": description
        })

        st.success("✅ Enregistré")

        # 👉 FORCE LE REFRESH
        st.rerun()

# ------------------------
# HISTORIQUE
# ------------------------
if len(st.session_state.data) > 0:

    st.subheader("📊 Historique")

    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # ------------------------
    # PDF
    # ------------------------
    if st.button("📄 Générer PDF"):

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "Rapport Chantier", ln=True)

        for row in st.session_state.data:

            amplitude = f"{row['debut']} → {row['fin']}"

            pdf.ln(5)
            pdf.cell(0, 10, f"Date : {row['date']}", ln=True)
            pdf.cell(0, 10, f"Ouvrier : {row['ouvrier']}", ln=True)
            pdf.cell(0, 10, f"Chantier : {row['chantier']}", ln=True)
            pdf.cell(0, 10, f"Amplitude : {amplitude}", ln=True)
            pdf.cell(0, 10, f"Duree : {row['duree']} h", ln=True)
            pdf.multi_cell(0, 10, f"Description : {row['description']}")
            pdf.cell(0, 10, "----------------------", ln=True)

        pdf.output("rapport.pdf")

        with open("rapport.pdf", "rb") as f:
            st.download_button("📥 Télécharger PDF", f, file_name="rapport.pdf")