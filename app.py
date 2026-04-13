import streamlit as st
from datetime import datetime
import json
import os
import pandas as pd
from fpdf import FPDF
from openpyxl import Workbook, load_workbook

# =========================
# 📱 CONFIG MOBILE
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
FILE = "historique.json"

if os.path.exists(FILE):
    try:
        with open(FILE, "r") as f:
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
client = st.text_input("🏢 Entreprise / Client")
chantier = st.text_input("🏗 Chantier")
engin = st.text_input("🚜 Engin")
travail = st.text_area("🧾 Travail effectué")

# =========================
# ⏱ HORAIRES
# =========================
st.subheader("⏱ Horaires")

col1, col2 = st.columns(2)

with col1:
    matin_debut = st.time_input("Matin début", value=datetime.strptime("07:30", "%H:%M").time())
    matin_fin = st.time_input("Matin fin", value=datetime.strptime("12:00", "%H:%M").time())

with col2:
    aprem_debut = st.time_input("Après-midi début", value=datetime.strptime("13:30", "%H:%M").time())
    aprem_fin = st.time_input("Après-midi fin", value=datetime.strptime("17:00", "%H:%M").time())

def calc_hours(d1, d2):
    t1 = datetime.combine(datetime.today(), d1)
    t2 = datetime.combine(datetime.today(), d2)
    if t2 > t1:
        return (t2 - t1).seconds / 3600
    return 0

total = calc_hours(matin_debut, matin_fin) + calc_hours(aprem_debut, aprem_fin)

st.write("🕒 Total :", round(total, 2), "h")

# =========================
# 💾 SAUVEGARDE
# =========================
def save_entry():
    return {
        "date": date_jour,
        "ouvrier": ouvrier,
        "client": client,
        "chantier": chantier,
        "engin": engin,
        "travail": travail,
        "matin_debut": matin_debut.strftime("%H:%M"),
        "matin_fin": matin_fin.strftime("%H:%M"),
        "aprem_debut": aprem_debut.strftime("%H:%M"),
        "aprem_fin": aprem_fin.strftime("%H:%M"),
        "total": total
    }

if st.button("💾 ENREGISTRER"):
    if ouvrier and chantier:
        historique.append(save_entry())

        with open(FILE, "w") as f:
            json.dump(historique, f, indent=4)

        st.success("Sauvegardé ✔")
        st.rerun()
    else:
        st.warning("⚠ Ouvrier + Chantier obligatoires")

# =========================
# 📊 DATAFRAME ANTI-BUG
# =========================
df = pd.DataFrame(historique)

cols = [
    "date","ouvrier","client","chantier","engin","travail",
    "matin_debut","matin_fin","aprem_debut","aprem_fin","total"
]

for c in cols:
    if c not in df.columns:
        df[c] = ""

df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)

st.dataframe(df, use_container_width=True)

# =========================
# 📊 STATS
# =========================
if not df.empty:
    st.subheader("📊 Statistiques")
    st.metric("Total heures", float(df["total"].sum()))
    st.metric("Moyenne", round(float(df["total"].mean()), 2))

# =========================
# 📄 PDF
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "V17 MOBILE PRO MAX", ln=True, align="C")
        self.ln(5)

def export_pdf(dataframe):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # 🔥 AMPLITUDE MODIFIÉE
    pdf.cell(0, 8, "Amplitude horaire : 07h30 / 12h00 - 13h30 / 17h00", ln=True)
    pdf.ln(3)

    for _, row in dataframe.iterrows():
        pdf.cell(0, 7, f"Date : {row['date']}", ln=True)
        pdf.cell(0, 7, f"Ouvrier : {row['ouvrier']}", ln=True)
        pdf.cell(0, 7, f"Entreprise / Client : {row['client']}", ln=True)
        pdf.cell(0, 7, f"Chantier : {row['chantier']}", ln=True)
        pdf.cell(0, 7, f"Engin : {row['engin']}", ln=True)

        pdf.cell(0, 7, f"Travail effectué : {row['travail']}", ln=True)

        pdf.cell(0, 7, f"Matin : {row['matin_debut']} - {row['matin_fin']}", ln=True)
        pdf.cell(0, 7, f"Aprem : {row['aprem_debut']} - {row['aprem_fin']}", ln=True)
        pdf.cell(0, 7, f"Total : {row['total']} h", ln=True)
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
# 📊 EXCEL
# =========================
if st.button("📊 EXCEL"):

    file = "chantier.xlsx"

    if not os.path.exists(file):
        wb = Workbook()
        ws = wb.active
        ws.append([
            "Date","Ouvrier","Client","Chantier","Engin","Travail",
            "Matin début","Matin fin","Aprem début","Aprem fin","Total"
        ])
        wb.save(file)

    wb = load_workbook(file)
    ws = wb.active

    ws.append([
        date_jour,
        ouvrier,
        client,
        chantier,
        engin,
        travail,
        matin_debut.strftime("%H:%M"),
        matin_fin.strftime("%H:%M"),
        aprem_debut.strftime("%H:%M"),
        aprem_fin.strftime("%H:%M"),
        total
    ])

    wb.save(file)

    with open(file, "rb") as f:
        st.download_button("Télécharger Excel", f, file_name="chantier.xlsx")

# =========================
# 🧹 RESET
# =========================
if st.button("🧹 RESET"):
    historique = []
    if os.path.exists(FILE):
        os.remove(FILE)
    st.success("Reset OK")
    st.rerun()