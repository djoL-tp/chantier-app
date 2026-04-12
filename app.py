import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
import pandas as pd

st.title("📋 Rapport de chantier BTP V11")

# -------------------------
# 📅 DATE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")
st.write("Date :", date_jour)

# -------------------------
# 📍 CHANTIER (SAISIE LIBRE)
# -------------------------
chantier = st.text_input("Nom du chantier")

# -------------------------
# 🌍 GPS (manuel + bouton)
# -------------------------
st.subheader("Localisation")

localisation = st.text_input("Adresse ou lieu")

if st.button("📍 Utiliser ma position"):
    st.info("👉 Active la localisation dans ton navigateur (Streamlit ne récupère pas automatiquement le GPS iPhone sans plugin)")

# -------------------------
# 🚜 ENGIN
# -------------------------
engin = st.text_input("Engin utilisé")

# -------------------------
# 🧾 TRAVAIL
# -------------------------
travail = st.text_area("Travail effectué")

# -------------------------
# 📸 PHOTOS
# -------------------------
st.subheader("Photos chantier")

photos = st.file_uploader("Ajouter des photos", accept_multiple_files=True)

# -------------------------
# ⏱️ HORAIRES
# -------------------------
st.subheader("Horaires")

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


def format_duree(duree):
    heures = duree.seconds // 3600
    minutes = (duree.seconds % 3600) // 60
    return f"{heures}h{minutes:02d}"


total = calcul_duree(debut_matin, fin_matin) + calcul_duree(debut_aprem, fin_aprem)

st.write("🕒 Total :", format_duree(total))

# -------------------------
# ✍️ SIGNATURE
# -------------------------
st.subheader("Signature")

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
    img = PILImage.fromarray(canvas_result.image_data.astype('uint8'))
    signature_path = "signature.png"
    img.save(signature_path)

# -------------------------
# 💾 DONNÉES
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
    if os.path.exists("historique.json"):
        with open("historique.json", "r") as f:
            historique = json.load(f)
    else:
        historique = []

    historique.append(data)

    with open("historique.json", "w") as f:
        json.dump(historique, f, indent=4)

    st.success("Enregistré ✅")

# -------------------------
# 📄 PDF COMPLET
# -------------------------
def generer_pdf():
    doc = SimpleDocTemplate("rapport.pdf")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("RAPPORT DE CHANTIER", styles['Title']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Date : {data['date']}", styles['Normal']))
    elements.append(Paragraph(f"Chantier : {data['chantier']}", styles['Normal']))
    elements.append(Paragraph(f"Lieu : {data['localisation']}", styles['Normal']))
    elements.append(Paragraph(f"Engin : {data['engin']}", styles['Normal']))
    elements.append(Paragraph(f"Heures : {data['heures']}", styles['Normal']))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Travail effectué :", styles['Heading2']))
    elements.append(Paragraph(data['travail'], styles['Normal']))

    # SIGNATURE
    if signature_path:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature :", styles['Heading2']))
        elements.append(Image(signature_path, width=200, height=100))

    # PHOTOS
    if photos:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Photos chantier :", styles['Heading2']))
        for photo in photos:
            image = PILImage.open(photo)
            path = f"photo_{photo.name}"
            image.save(path)
            elements.append(Image(path, width=300, height=200))
            elements.append(Spacer(1, 10))

    doc.build(elements)


if st.button("📄 Générer PDF"):
    generer_pdf()

    with open("rapport.pdf", "rb") as f:
        st.download_button("📥 Télécharger le PDF", f, "rapport_chantier.pdf")

# -------------------------
# 📊 EXCEL
# -------------------------
if st.button("📊 Export Excel"):
    df = pd.DataFrame([data])
    df.to_excel("rapport.xlsx", index=False)

    with open("rapport.xlsx", "rb") as f:
        st.download_button("📥 Télécharger Excel", f, "rapport.xlsx")

# -------------------------
# 📊 HISTORIQUE
# -------------------------
if os.path.exists("historique.json"):
    with open("historique.json", "r") as f:
        historique = json.load(f)

    st.subheader("📊 Historique")
    st.write(historique)