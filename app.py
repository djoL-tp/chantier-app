import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
import pandas as pd
from openpyxl import Workbook, load_workbook

st.set_page_config(page_title="BTP PRO MAX", layout="wide")

st.title("📋 Rapport de chantier V11 PRO MAX")

# -------------------------
# 📅 DATE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")
st.write("📅 Date :", date_jour)

# -------------------------
# 📍 CHANTIER (SAISIE LIBRE)
# -------------------------
chantier = st.text_input("🏗 Chantier")

# -------------------------
# 🌍 LOCALISATION
# -------------------------
localisation = st.text_input("📍 Localisation / Adresse")

# -------------------------
# 🚜 ENGIN
# -------------------------
engin = st.text_input("🚜 Engin utilisé")

# -------------------------
# 🧾 TRAVAIL EFFECTUÉ
# -------------------------
travail = st.text_area("🧾 Travail effectué")

# -------------------------
# ⏱ HORAIRES
# -------------------------
st.subheader("⏱ Horaires")

col1, col2 = st.columns(2)

with col1:
    debut_matin = st.time_input("Début matin")
    fin_matin = st.time_input("Fin matin")

with col2:
    debut_aprem = st.time_input("Début après-midi")
    fin_aprem = st.time_input("Fin après-midi")


def calcul_duree(debut, fin):
    if debut and fin:
        d1 = datetime.combine(datetime.today(), debut)
        d2 = datetime.combine(datetime.today(), fin)
        if d2 > d1:
            return d2 - d1
    return timedelta(0)


def format_duree(d):
    heures = d.seconds // 3600
    minutes = (d.seconds % 3600) // 60
    return f"{heures}h{minutes:02d}"


total = calcul_duree(debut_matin, fin_matin) + calcul_duree(debut_aprem, fin_aprem)

st.write("🕒 Total travaillé :", format_duree(total))

# -------------------------
# ✍️ SIGNATURE
# -------------------------
st.subheader("✍️ Signature")

canvas_result = st_canvas(
    stroke_width=3,
    stroke_color="black",
    background_color="white",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

signature_path = None

if canvas_result.image_data is not None:
    img = PILImage.fromarray(canvas_result.image_data.astype("uint8"))
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
    "heures": format_duree(total)
}

# -------------------------
# 💾 HISTORIQUE JSON
# -------------------------
if st.button("💾 Enregistrer"):
    historique = []

    if os.path.exists("historique.json"):
        with open("historique.json", "r") as f:
            historique = json.load(f)

    historique.append(data)

    with open("historique.json", "w") as f:
        json.dump(historique, f, indent=4)

    st.success("Enregistré ✅")

# -------------------------
# 📄 PDF PRO
# -------------------------
def generer_pdf():
    doc = SimpleDocTemplate("rapport.pdf")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("RAPPORT DE CHANTIER", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Date : {data['date']}", styles["Normal"]))
    elements.append(Paragraph(f"Chantier : {data['chantier']}", styles["Normal"]))
    elements.append(Paragraph(f"Localisation : {data['localisation']}", styles["Normal"]))
    elements.append(Paragraph(f"Engin : {data['engin']}", styles["Normal"]))
    elements.append(Paragraph(f"Heures : {data['heures']}", styles["Normal"]))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Travail effectué :", styles["Heading2"]))
    elements.append(Paragraph(data["travail"], styles["Normal"]))

    if signature_path:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature :", styles["Heading2"]))
        elements.append(Image(signature_path, width=200, height=100))

    doc.build(elements)

# -------------------------
# 📊 EXCEL PRO (HISTORIQUE GLOBAL)
# -------------------------
def heures_to_decimal(h):
    try:
        h1, m1 = h.split("h")
        return float(h1) + float(m1) / 60
    except:
        return 0


if st.button("📊 Export Excel PRO"):

    fichier = "rapport_chantier.xlsx"

    if not os.path.exists(fichier):
        wb = Workbook()
        ws = wb.active
        ws.title = "Chantiers"
        ws.append(["Date", "Chantier", "Localisation", "Engin", "Travail", "Heures"])
        wb.save(fichier)

    wb = load_workbook(fichier)
    ws = wb.active

    ws.append([
        data["date"],
        data["chantier"],
        data["localisation"],
        data["engin"],
        data["travail"],
        heures_to_decimal(data["heures"]),
    ])

    last_row = ws.max_row
    ws["G1"] = "TOTAL HEURES"
    ws["G2"] = f"=SUM(F2:F{last_row})"

    wb.save(fichier)

    with open(fichier, "rb") as f:
        st.download_button("📥 Télécharger Excel PRO", f, file_name="rapport_chantier.xlsx")

# -------------------------
# 📄 PDF DOWNLOAD
# -------------------------
if st.button("📄 Générer PDF"):
    generer_pdf()

    with open("rapport.pdf", "rb") as f:
        st.download_button("📥 Télécharger PDF", f, file_name="rapport.pdf")

# -------------------------
# 📊 HISTORIQUE
# -------------------------
if os.path.exists("historique.json"):
    with open("historique.json", "r") as f:
        historique = json.load(f)

    st.subheader("📊 Historique")
    st.write(historique)
    # -------------------------
# 🗑 SUPPRESSION HISTORIQUE
# -------------------------
st.subheader("🗑 Gestion historique")

if os.path.exists("historique.json"):
    with open("historique.json", "r") as f:
        historique = json.load(f)

    st.write(f"Nombre d’entrées : {len(historique)}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑 Supprimer tout l’historique"):
            st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete", False):
        st.warning("⚠ Tu es sur le point de supprimer tout l’historique")

        col3, col4 = st.columns(2)

        with col3:
            if st.button("❌ Annuler"):
                st.session_state["confirm_delete"] = False

        with col4:
            if st.button("✅ Confirmer suppression"):
                os.remove("historique.json")
                st.success("Historique supprimé ✅")
                st.session_state["confirm_delete"] = False