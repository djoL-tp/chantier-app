import streamlit as st
from datetime import datetime, timedelta
import json
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage

from openpyxl import Workbook, load_workbook

st.set_page_config(page_title="V17 PRO MAX CLEAN", layout="wide")
st.title("📋 Chantier V17 PRO MAX (CLEAN)")

# -------------------------
# 📅 DATE MANUELLE
# -------------------------
st.subheader("📅 Date du chantier")

date_jour = st.date_input(
    "Choisir la date",
    value=datetime.now()
).strftime("%d/%m/%Y")

st.write("📅 Date sélectionnée :", date_jour)

# -------------------------
# 📍 CHANTIER
# -------------------------
chantier = st.text_input("🏗 Chantier (saisie manuelle)")

# -------------------------
# 🌍 LOCALISATION
# -------------------------
localisation = st.text_input("📍 Localisation")

# -------------------------
# 🚜 ENGIN
# -------------------------
engin = st.text_input("🚜 Engin utilisé (ligne libre)")

# -------------------------
# 🧾 TRAVAIL
# -------------------------
travail = st.text_area("🧾 Travail effectué")

# -------------------------
# ⏱ HORAIRES
# -------------------------
col1, col2 = st.columns(2)

with col1:
    debut_matin = st.time_input("Début matin")
    fin_matin = st.time_input("Fin matin")

with col2:
    debut_aprem = st.time_input("Début après-midi")
    fin_aprem = st.time_input("Fin après-midi")


def calc(d1, d2):
    if d1 and d2:
        a = datetime.combine(datetime.today(), d1)
        b = datetime.combine(datetime.today(), d2)
        if b > a:
           