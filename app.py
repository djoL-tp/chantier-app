import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
from openpyxl import Workbook, load_workbook

# -------------------------
# ☁️ FIREBASE
# -------------------------
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="V13 PRO MAX", layout="wide")
st.title("📋 Chantier V13 PRO MAX CLOUD")

# -------------------------
# 📅 DATE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")

# -------------------------
# 📍 CHANTIER
# -------------------------
chantier = st.text_input("🏗 Chantier")

# -------------------------
# 🌍 LOCALISATION
# -------------------------
localisation = st.text_input("📍 Localisation")

# -------------------------
# 🚜 ENGIN
# -------------------------
engin = st.text_input("🚜 Engin")

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
            return b - a
    return timedelta(0)


def fmt(d):
    return f"{d.seconds//3600}h{(d.seconds%3600)//60:02d}"


total = calc(debut_matin, fin_matin) + calc(debut_aprem, fin_aprem)

st.write("🕒 Total :", fmt(total))

# -------------------------
# ✍️ SIGNATURE
# -------------------------
canvas = st_canvas(
    stroke_width=3,
    stroke_color="black",
    background_color="white",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="sig"
)

signature_path = None

if canvas.image_data is not None:
    img = PILImage.fromarray(canvas.image_data.astype("uint8"))
    signature_path = "signature.png"
    img.save(signature_path)

# -------------------------
# 📦 DATA
# -------------------------
data = {
    "date": date_jour,
    "chantier": chantier,
    "localisation": localisation,
    "engin": engin,
    "travail": travail,
    "heures": fmt(total),
    "timestamp": datetime.now().isoformat()
}

# -------------------------
# ☁️ + 💾 SAUVEGARDE CLOUD + LOCAL
# -------------------------
if st.button("💾 ENREGISTRER (CLOUD + LOCAL)"):

    # LOCAL
    historique = []

    if os.path.exists("historique.json"):
        with open("historique.json", "r") as f:
            historique = json.load(f)

    historique.append(data)

    with open("historique.json", "w") as f:
        json.dump(historique, f, indent=4)

    # CLOUD FIREBASE
    db.collection("chantiers").add(data)

    st.success("Sauvegarde locale + cloud OK ☁️")

# -------------------------
# 📊 CLOUD VIEW
# -------------------------
st.subheader("☁️ Historique Cloud")

docs = db.collection("chantiers").stream()

cloud = [d.to_dict() for d in docs]

st.write(cloud)