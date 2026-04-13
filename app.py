import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="V17 PRO MAX BTP", layout="centered")

# ------------------------
# INIT DATA
# ------------------------
if "data" not in st.session_state:
    st.session_state.data = []

st.title("📋 V17 PRO MAX BTP")

# ------------------------
# FORMULAIRE
# ------------------------
date = st.date_input("📅 Date", datetime.today())

ouvrier = st.text_input("👷 Ouvrier")

chantier = st.text_input("🏗️ Chantier")

col1, col2 = st.columns(2)

with col1:
    heure_debut = st.time_input("⏰ Début matin")

with col2:
    heure_fin = st.time_input("⏰ Fin journée")

description = st.text_area("📝 Description")

# ------------------------
# ENREGISTRER
# ------------------------
if st.button("💾 Enregistrer"):

    debut = datetime.combine(date, heure_debut)
    fin = datetime.combine(date, heure_fin)

    if fin <= debut:
        st.error("❌ Heure fin doit être après heure début")
    else:
        duree = (fin - debut).total_seconds() / 3600

        st.session_state.data.append({
            "Date": date.strftime("%d/%m/%Y"),
            "Ouvrier": ouvrier,
            "Chantier": chantier,
            "Début": heure_debut.strftime("%H:%M"),
            "Fin": heure_fin.strftime("%H:%M"),
            "Amplitude": f"{heure_debut.strftime('%H:%M')} → {heure_fin.strftime('%H:%M')}",
            "Heures": round(duree, 2),
            "Description": description
        })

        st.success("✅ Enregistré")

# ------------------------
# HISTORIQUE
# ------------------------
if len(st.session_state.data) > 0:

    st.subheader("📊 Historique")

    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # ------------------------
    # STATS
    # ------------------------
    st.subheader("📈 Statistiques")

    st.metric("Total heures", f"{df['Heures'].sum():.2f} h")

    # ------------------------
    # PDF
    # ------------------------
    def generate_pdf(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "RAPPORT CHANTIER V17 PRO MAX", ln=True)

        for row in data:

            pdf.ln(5)
            pdf.cell(0, 10, f"Date : {row['Date']}", ln=True)
            pdf.cell(0, 10, f"Ouvrier : {row['Ouvrier']}", ln=True)
            pdf.cell(0, 10, f"Chantier : {row['Chantier']}", ln=True)
            pdf.cell(0, 10, f"Amplitude : {row['Amplitude']}", ln=True)
            pdf.cell(0, 10, f"Heures : {row['Heures']} h", ln=True)
            pdf.multi_cell(0, 10, f"Description : {row['Description']}")
            pdf.cell(0, 10, "-"*40, ln=True)

        return pdf

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 PDF"):
            pdf = generate_pdf(st.session_state.data)
            pdf.output("rapport.pdf")

            with open("rapport.pdf", "rb") as f:
                st.download_button("📥 Télécharger PDF", f, file_name="rapport.pdf")

    # ------------------------
    # EXCEL
    # ------------------------
    with col2:
        if st.button("📊 Excel"):

            df = pd.DataFrame(st.session_state.data)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Chantier")

            st.download_button(
                "📥 Télécharger Excel",
                output.getvalue(),
                file_name="rapport_chantier.xlsx"
            )