import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage

from openpyxl import Workbook, load_workbook


# =========================
# 📱 MODE MOBILE OPTIMISÉ
# =========================
st.set_page_config(
    page_title="V17 PRO MAX CLEAN",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@media (max-width: 768px){
    .block-container{
        padding: 10px !important;
    }
    h1, h2, h3{
        font-size: 18px !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.title("📋 Chantier V17 PRO MAX CLEAN")


# =========================
# 📊 CHARGEMENT HISTORIQUE
# =========================
file_json = "historique.json"

if os.path.exists(file_json):
    with open(file_json, "r") as f:
        historique = json.load(f)
else:
    historique = []


# =========================
# 📅 DATE
# =========================
st.subheader("📅 Date du chantier")

date_obj = st.date_input("Choisir la date", value=datetime.now())
date_jour = date_obj.strftime("%d/%m/%Y")

st.write("📅 Date :", date_jour)


# =========================
# 🏗 DONNÉES
# =========================
chantier = st.text_input("🏗 Chantier")
localisation = st.text_input("📍 Localisation")
engin = st.text_input("🚜 Engin")
travail = st.text_area("🧾 Travail")


# =========================
# ⏱ HORAIRES
# =========================
col1, col2 = st.columns(2)

with col1:
    debut_matin = st.time_input("Début matin")
    fin_matin = st.time_input("Fin matin")

with col2:
    debut_aprem = st.time_input("Début aprem")
    fin_aprem = st.time_input("Fin aprem")


def calc(d1, d2):
    if d1 and d2:
        a = datetime.combine(datetime.today(), d1)
        b = datetime.combine(datetime.today(), d2)
        if b > a:
            return b - a
    return timedelta(0)


def fmt(td):
    return f"{td.seconds//3600}h{(td.seconds%3600)//60:02d}"


total = calc(debut_matin, fin_matin) + calc(debut_aprem, fin_aprem)

st.write("🕒 Total :", fmt(total))


# =========================
# 📊 STATISTIQUES
# =========================
st.subheader("📊 Statistiques")

if historique:

    df = pd.DataFrame(historique)

    # conversion date
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")

    # heures numériques
    def to_decimal(h):
        try:
            a, b = h.split("h")
            return float(a) + float(b)/60
        except:
            return 0

    df["heures_num"] = df["heures"].apply(to_decimal)

    # ================= SEMAINE =================
    df["semaine"] = df["date"].dt.isocalendar().week
    semaine = df.groupby("semaine")["heures_num"].sum()

    st.write("📅 Heures par semaine")
    st.bar_chart(semaine)

    # ================= MOIS =================
    df["mois"] = df["date"].dt.to_period("M").astype(str)
    mois = df.groupby("mois")["heures_num"].sum()

    st.write("📆 Heures par mois")
    st.bar_chart(mois)

else:
    st.info("Aucune donnée pour statistiques")


# =========================
# 💾 SAUVEGARDE
# =========================
if st.button("💾 ENREGISTRER"):

    data = {
        "date": date_jour,
        "chantier": chantier,
        "localisation": localisation,
        "engin": engin,
        "travail": travail,
        "heures": fmt(total),
        "timestamp": datetime.now().isoformat()
    }

    historique.append(data)

    with open(file_json, "w") as f:
        json.dump(historique, f, indent=4)

    st.success("Sauvegarde OK ✔")
    st.rerun()


# =========================
# 📂 HISTORIQUE
# =========================
st.subheader("📂 Historique")

st.write(historique)


# =========================
# 🧹 SUPPRESSION
# =========================
if st.button("🧹 Effacer tout l'historique"):
    if os.path.exists(file_json):
        os.remove(file_json)

    st.success("Historique supprimé ✔")
    st.rerun()