import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
from openpyxl import Workbook, load_workbook

import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="V14 PRO MAX", layout="wide")
st.title("📋 Chantier V14 PRO MAX STABLE")

# -------------------------
# ☁️ FIREBASE FIX COMPLET
# -------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("data/serviceAccountKey.json")

    firebase_admin.initialize_app(cred, {
        "projectId": chantier-app-40475
    })

db = firestore.client()

# -------------------------
# 📅 DATE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")

st.write("📅 Date :", date_jour)

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
engin = st.text_input("🚜 Engin utilisé")

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
st.subheader("✍️ Signature")

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
# 💾 SAVE LOCAL + CLOUD
# -------------------------
if st.button("💾 ENREGISTRER"):

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

    st.success("Sauvegarde OK ☁️ + LOCAL")

# -------------------------
# 📄 PDF
# -------------------------
def pdf():
    doc = SimpleDocTemplate("rapport.pdf")
    styles = getSampleStyleSheet()
    e = []

    e.append(Paragraph("RAPPORT CHANTIER V14 PRO MAX", styles["Title"]))
    e.append(Spacer(1, 20))

    e.append(Paragraph(f"Date : {data['date']}", styles["Normal"]))
    e.append(Paragraph(f"Chantier : {data['chantier']}", styles["Normal"]))
    e.append(Paragraph(f"Localisation : {data['localisation']}", styles["Normal"]))
    e.append(Paragraph(f"Engin : {data['engin']}", styles["Normal"]))
    e.append(Paragraph(f"Heures : {data['heures']}", styles["Normal"]))

    e.append(Spacer(1, 10))
    e.append(Paragraph("Travail :", styles["Heading2"]))
    e.append(Paragraph(data["travail"], styles["Normal"]))

    if signature_path:
        e.append(Spacer(1, 20))
        e.append(Image(signature_path, width=200, height=100))

    doc.build(e)

# -------------------------
# 📄 PDF DOWNLOAD
# -------------------------
if st.button("📄 PDF"):
    pdf()
    with open("rapport.pdf", "rb") as f:
        st.download_button("Télécharger PDF", f, "rapport.pdf")

# -------------------------
# 📊 EXCEL PRO
# -------------------------
def to_decimal(h):
    try:
        a, b = h.split("h")
        return float(a) + float(b)/60
    except:
        return 0


if st.button("📊 EXCEL"):

    file = "chantier.xlsx"

    if not os.path.exists(file):
        wb = Workbook()
        ws = wb.active
        ws.append(["Date", "Chantier", "Localisation", "Engin", "Travail", "Heures"])
        wb.save(file)

    wb = load_workbook(file)
    ws = wb.active

    ws.append([
        data["date"],
        data["chantier"],
        data["localisation"],
        data["engin"],
        data["travail"],
        to_decimal(data["heures"])
    ])

    ws["G1"] = "TOTAL"
    ws["G2"] = f"=SUM(F2:F{ws.max_row})"

    wb.save(file)

    with open(file, "rb") as f:
        st.download_button("Télécharger Excel", f, file_name="chantier.xlsx")

# -------------------------
# ☁️ CLOUD VIEW
# -------------------------
st.subheader("☁️ Cloud Firebase")

docs = db.collection("chantiers").stream()

st.write([d.to_dict() for d in docs])