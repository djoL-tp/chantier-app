import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="V17 PRO MAX BTP", layout="centered")

# ------------------------
# INITIALISATION
# ------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# ------------------------
# TITRE
# ------------------------
st.title("📋 Rapport Chantier V17 PRO MAX")

# ------------------------
# FORMULAIRE
# ------------------------
with st.form("formulaire"):

    date = st.date_input("📅 Date", datetime.today())

    ouvrier = st.text_input("👷 Ouvrier")
    chantier = st.text_input("🏗️ Chantier")

    heure_debut = st.time_input("⏰ Heure début")
    heure_fin = st.time_input("⏰ Heure fin")

    description = st.text_area("📝 Description")

    submit = st.form_submit_button("Enregistrer")

# ------------------------
# ENREGISTREMENT
# ------------------------
if submit:

    debut = datetime.combine(date, heure_debut)
    fin = datetime.combine(date, heure_fin)

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

# ------------------------
# AFFICHAGE TABLEAU
# ------------------------
if st.session_state.data:

    df = pd.DataFrame(st.session_state.data)

    st.subheader("📊 Historique")
    st.dataframe(df, use_container_width=True)

    # ------------------------
    # STATS
    # ------------------------
    df["date_dt"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

    semaine = df[df["date_dt"] >= pd.Timestamp.today() - pd.Timedelta(days=7)]
    mois = df[df["date_dt"] >= pd.Timestamp.today() - pd.Timedelta(days=30)]

    st.subheader("📈 Statistiques")

    col1, col2 = st.columns(2)

    col1.metric("🗓️ Heures semaine", f"{semaine['duree'].sum():.2f} h")
    col2.metric("📅 Heures mois", f"{mois['duree'].sum():.2f} h")

    # ------------------------
    # PDF
    # ------------------------
    if st.button("📄 Générer PDF"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Rapport Chantier", ln=True)

        pdf.set_font("Arial", "", 12)

        for row in st.session_state.data:

            # AMPLITUDE HORAIRE
            amplitude = f"{row['debut']} → {row['fin']}"

            pdf.ln(5)
            pdf.cell(0, 10, f"Date : {row['date']}", ln=True)
            pdf.cell(0, 10, f"Ouvrier : {row['ouvrier']}", ln=True)
            pdf.cell(0, 10, f"Chantier : {row['chantier']}", ln=True)

            # 👉 ICI TA NOUVELLE LIGNE DEMANDÉE
            pdf.cell(0, 10, f"Amplitude : {amplitude}", ln=True)

            pdf.cell(0, 10, f"Durée : {row['duree']} h", ln=True)

            pdf.multi_cell(0, 10, f"Description : {row['description']}")
            pdf.cell(0, 10, "-"*40, ln=True)

        pdf.output("rapport.pdf")

        with open("rapport.pdf", "rb") as f:
            st.download_button("📥 Télécharger PDF", f, file_name="rapport.pdf")