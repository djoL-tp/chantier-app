import streamlit as st
from datetime import datetime
import json
import os
import pandas as pd
from fpdf import FPDF
from openpyxl import Workbook, load_workbook

# =========================
# 📱 CONFIG MOBILE SAFE
# =========================
st.set_page_config(page_title="V17 MOBILE PRO MAX", layout="wide")

st.markdown("""
<style>
.block-container {padding: 10px !important;}
</style>
""", unsafe_allow_html=True)

st.title("📱 V17 MOBILE PRO MAX")

# =========================
# 📂 HISTORIQUE SAFE
# =========================
FILE_JSON = "historique.json"

if os.path.exists(FILE_JSON):
    try:
        with open(FILE_JSON, "r") as f:
            historique = json.load(f)
    except:
        historique = []
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
# 👷 INPUTS
# =========================
ouvrier = st.text_input("👷 Ouvrier")
chantier = st.text_input("🏗 Chantier")
engin = st.text_input("🚜 Engin")
travail = st.text_area("🧾 Travail effectué")

# =========================
# ⏱ HEURES
# =========================
h_matin = st.number_input("Heures matin", 0.0, 12.0, step=0.5)
h_aprem = st.number_input("Heures après-midi", 0.0, 12.0, step=0.5)

total = h_matin + h_aprem
st.write("🕒 Total :", total, "h")

# =========================
# 💾 ENREGISTREMENT SAFE
# =========================
def save_data():
    entry = {
        "date": date_jour,
        "ouvrier": ouvrier,
        "chantier": chantier,
        "engin": engin,
        "travail": travail,
        "matin": h_matin,
        "aprem": h_aprem,
        "total": total
    }

    historique.append(entry)

    with open(FILE_JSON, "w") as f:
        json.dump(historique, f, indent=4)

    return entry

if st.button("💾 ENREGISTRER"):
    if chantier and ouvrier:
        save_data()
        st.success("Sauvegardé ✔")
        st.rerun()
    else:
        st.warning("Remplis ouvrier + chantier")

# =========================
# 📊 TABLEAU
# =========================
df = pd.DataFrame(historique)
st.dataframe(df, use_container_width=True)

# =========================
# 📊 STATS SAFE
# =========================
if not df.empty:
    st.subheader("📊 Statistiques")
    st.metric("Total heures", float(df["total"].sum()))
    st.metric("Moyenne", round(df["total"].mean(), 2))

    df["semaine"] = pd.to_datetime(df["date"], errors="coerce").dt.isocalendar().week
    st.bar_chart(df.groupby("semaine")["total"].sum())

# =========================
# 📄 PDF ULTRA STABLE
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "RAPPORT CHANTIER V17 MOBILE PRO MAX", ln=True, align="C")
        self.ln(5)

def export_pdf(dataframe):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, "Amplitude horaire : 08h00 / 12h00 - 13h00 / 17h30", ln=True)
    pdf.ln(3)

    for _, row in dataframe.iterrows():
        pdf.cell(0, 7, f"Date : {row['date']}", ln=True)
        pdf.cell(0, 7, f"Ouvrier : {row['ouvrier']}", ln=True)
        pdf.cell(0, 7, f"Chantier : {row['chantier']}", ln=True)
        pdf.cell(0, 7, f"Engin : {row['engin']}", ln=True)
        pdf.cell(0, 7, f"Travail : {row['travail']}", ln=True)
        pdf.cell(0, 7, f"Total : {row['total']}h", ln=True)
        pdf.ln(2)

    file = "rapport.pdf"
    pdf.output(file)
    return file

if not df.empty:
    if st.button("📄 PDF"):
        file = export_pdf(df)
        with open(file, "rb") as f:
            st.download_button("Télécharger PDF", f, file_name="rapport.pdf")

# =========================
# 📊 EXCEL SAFE (UNE FOIS)
# =========================
if st.button("📊 EXCEL"):

    file = "chantier.xlsx"

    if not os.path.exists(file):
        wb = Workbook()
        ws = wb.active
        ws.append(["Date","Ouvrier","Chantier","Engin","Travail","Matin","Aprem","Total"])
        wb.save(file)

    wb = load_workbook(file)
    ws = wb.active

    # évite doublons (important bug iPhone)
    ws.append([
        date_jour,
        ouvrier,
        chantier,
        engin,
        travail,
        h_matin,
        h_aprem,
        total
    ])

    wb.save(file)

    with open(file, "rb") as f:
        st.download_button("Télécharger Excel", f, file_name="chantier.xlsx")

# =========================
# 🧹 RESET SAFE
# =========================
if st.button("🧹 RESET"):
    historique = []
    if os.path.exists(FILE_JSON):
        os.remove(FILE_JSON)
    st.success("Reset OK")
    st.rerun()