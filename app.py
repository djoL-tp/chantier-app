import streamlit as st
from datetime import datetime
import json
import os
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# =========================
# 📱 CONFIG MOBILE
# =========================
st.set_page_config(
    page_title="V17 MOBILE PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container {padding: 10px !important;}
</style>
""", unsafe_allow_html=True)

st.title("📱 V17 MOBILE PRO - CHANTIER")

# =========================
# 📂 HISTORIQUE
# =========================
file_json = "historique.json"

if os.path.exists(file_json):
    with open(file_json, "r") as f:
        historique = json.load(f)
else:
    historique = []

# =========================
# 📅 DATE FR
# =========================
def date_fr():
    jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    mois = ["janvier","février","mars","avril","mai","juin",
            "juillet","août","septembre","octobre","novembre","décembre"]

    now = datetime.now()
    return f"{jours[now.weekday()]} {now.day} {mois[now.month-1]} {now.year}"

date_jour = date_fr()
st.write("📅", date_jour)

# =========================
# 🏗 INPUT
# =========================
chantier = st.text_input("🏗 Chantier")
engin = st.text_input("🚜 Engin")
travail = st.text_area("🧾 Travail effectué")

# =========================
# ⏱ HEURES SIMPLIFIÉES (MOBILE OK)
# =========================
h_matin = st.number_input("Heures matin", 0.0, 12.0, step=0.5)
h_aprem = st.number_input("Heures après-midi", 0.0, 12.0, step=0.5)

total = h_matin + h_aprem

st.write("🕒 Total :", total, "h")

# =========================
# 💾 ENREGISTREMENT
# =========================
data = {
    "date": date_jour,
    "chantier": chantier,
    "engin": engin,
    "travail": travail,
    "matin": h_matin,
    "aprem": h_aprem,
    "total": total
}

if st.button("💾 ENREGISTRER"):
    historique.append(data)

    with open(file_json, "w") as f:
        json.dump(historique, f, indent=4)

    st.success("Sauvegardé ✔")
    st.rerun()

# =========================
# 📊 TABLEAU
# =========================
df = pd.DataFrame(historique)
st.dataframe(df, use_container_width=True)

# =========================
# 📄 PDF SIMPLE (ULTRA MOBILE SAFE)
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "RAPPORT CHANTIER V17 MOBILE PRO", ln=True, align="C")
        self.ln(5)

def export_pdf(dataframe):

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # 🔥 AMPLITUDE DEMANDÉE
    pdf.cell(0, 8, "Amplitude horaire : 08h00 / 12h00 - 13h00 / 17h30", ln=True)
    pdf.ln(3)

    for _, row in dataframe.iterrows():
        ligne = f"{row['date']} | {row['chantier']} | {row['engin']} | {row['total']}h"
        pdf.cell(0, 8, ligne, ln=True)

    file = "rapport.pdf"
    pdf.output(file)
    return file

# =========================
# 📄 EXPORT PDF
# =========================
if not df.empty:
    if st.button("📄 PDF"):
        file = export_pdf(df)

        with open(file, "rb") as f:
            st.download_button("Télécharger PDF", f, file_name="rapport.pdf")

# =========================
# 📊 STATS SIMPLES MOBILE
# =========================
if not df.empty:
    st.subheader("📊 Statistiques")
    st.metric("Total heures", df["total"].sum())
    st.metric("Moyenne", round(df["total"].mean(), 2))

# =========================
# 🧹 RESET
# =========================
if st.button("🧹 Effacer"):
    historique = []
    if os.path.exists(file_json):
        os.remove(file_json)
    st.success("Reset OK")
    st.rerun()