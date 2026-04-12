import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
import base64

st.title("📋 Rapport de chantier BTP")

# -------------------------
# 📅 DATE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")
st.write("Date :", date_jour)

# -------------------------
# 📍 CHANTIER
# -------------------------
st.subheader("Chantier")

chantiers = ["Maison Dupont", "Lotissement Les Vignes", "Voirie centre ville"]

chantier = st.selectbox("Choisir un chantier", chantiers)
nouveau_chantier = st.text_input("Ou ajouter un chantier")

if nouveau_chantier:
    chantier = nouveau_chantier

# -------------------------
# 🌍 GEOLOCALISATION
# -------------------------
st.subheader("Localisation")

localisation = st.text_input("Adresse ou lieu du chantier")

# -------------------------
# 🚜 ENGIN
# -------------------------
engin = st.text_input("Engin utilisé")

# -------------------------
# 🧾 TRAVAIL EFFECTUÉ
# -------------------------
st.subheader("Travail effectué")

travail = st.text_area("Description des tâches")

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
# 💾 SAUVEGARDE
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
# 📄 PDF AVEC SIGNATURE
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

    if signature_path:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature :", styles['Heading2']))
        elements.append(Image(signature_path, width=200, height=100))

    doc.build(elements)


if st.button("📄 Générer PDF"):
    generer_pdf()

    with open("rapport.pdf", "rb") as f:
        st.download_button(
            "📥 Télécharger le PDF",
            f,
            file_name="rapport_chantier.pdf"
        )

# -------------------------
# 📊 HISTORIQUE
# -------------------------
if os.path.exists("historique.json"):
    with open("historique.json", "r") as f:
        historique = json.load(f)

    st.subheader("📊 Historique")
    st.write(historique)