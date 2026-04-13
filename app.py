import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="V17 PRO MAX", layout="wide")

st.title("🚧 V17 PRO MAX - Chantier")

# =========================
# FONCTION DATE FR
# =========================
def date_fr():
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    now = datetime.now()
    return f"{jours[now.weekday()]} {now.day} {mois[now.month - 1]} {now.year}"

# =========================
# SESSION DATA
# =========================
if "data" not in st.session_state:
    st.session_state.data = []

# =========================
# FORMULAIRE
# =========================
st.subheader("📝 Saisie journée")

col1, col2, col3 = st.columns(3)

with col1:
    chantier = st.text_input("Chantier")
    engin = st.text_input("Engin")

with col2:
    h_matin = st.number_input("Heures matin", 0.0, 12.0, step=0.5)
    h_aprem = st.number_input("Heures après-midi", 0.0, 12.0, step=0.5)

with col3:
    h_soir = st.number_input("Heures soir", 0.0, 12.0, step=0.5)

total = h_matin + h_aprem + h_soir

# Amplitude horaire (simple)
if total > 0:
    amplitude = f"{h_matin + h_aprem + h_soir} h travaillées"
else:
    amplitude = "0 h"

if st.button("➕ Ajouter journée"):
    st.session_state.data.append({
        "Date": date_fr(),
        "Chantier": chantier,
        "Engin": engin,
        "Matin": h_matin,
        "Après-midi": h_aprem,
        "Soir": h_soir,
        "Total": total,
        "Amplitude": amplitude
    })
    st.success("Ajouté ✔️")

# =========================
# TABLEAU
# =========================
st.subheader("📊 Données")

df = pd.DataFrame(st.session_state.data)
st.dataframe(df, use_container_width=True)

# =========================
# STATS
# =========================
if not df.empty:
    st.subheader("📈 Statistiques")

    st.metric("Total heures", df["Total"].sum())
    st.metric("Moyenne par jour", round(df["Total"].mean(), 2))

# =========================
# EXPORT EXCEL
# =========================
def export_excel(dataframe):
    file = "chantier.xlsx"
    dataframe.to_excel(file, index=False)
    return file

# =========================
# EXPORT PDF
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "RAPPORT CHANTIER V17 PRO MAX", ln=True, align="C")

def export_pdf(dataframe):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for i, row in dataframe.iterrows():
        ligne = f"{row['Date']} | {row['Chantier']} | {row['Engin']} | {row['Total']}h"
        pdf.cell(0, 8, ligne, ln=True)

    file = "chantier.pdf"
    pdf.output(file)
    return file

# =========================
# BOUTONS EXPORT
# =========================
if not df.empty:
    colA, colB = st.columns(2)

    with colA:
        if st.button("📥 Export Excel"):
            file = export_excel(df)
            with open(file, "rb") as f:
                st.download_button("Télécharger Excel", f, file_name="chantier.xlsx")

    with colB:
        if st.button("📄 Export PDF"):
            file = export_pdf(df)
            with open(file, "rb") as f:
                st.download_button("Télécharger PDF", f, file_name="chantier.pdf")