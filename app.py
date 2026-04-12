import streamlit as st
from datetime import datetime, timedelta
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_drawable_canvas import st_canvas

st.title("📋 Rapport de chantier BTP")

# -------------------------
# 📅 DATE FRANÇAISE
# -------------------------
date_jour = datetime.now().strftime("%d/%m/%Y")
st.write("Date :", date_jour)

# -------------------------
# 🚜 ENGIN (SAISIE LIBRE)
# -------------------------
st.subheader("Engin utilisé")
engin = st.text_input("Nom de l'engin")

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


duree_matin = calcul_duree(debut_matin, fin_matin)
duree_aprem = calcul_duree(debut_aprem, fin_aprem)
total = duree_matin + duree_aprem

st.write("🕒 Total travaillé :", format_duree(total))

# -------------------------
# ✍️ SIGNATURE
# -------------------------
st.subheader("Signature ouvrier")

canvas_result = st_canvas(
    stroke_width=3,
    stroke_color="black",
    background_color="white",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# -------------------------
# 💾 DONNÉES
# -------------------------
data = {
    "date": date_jour,
    "engin": engin,
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
# 📄 PDF
# -------------------------
def generer_pdf():
    doc = SimpleDocTemplate("rapport.pdf")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("RAPPORT DE CHANTIER", styles['Title']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Date : {data['date']}", styles['Normal']))
    elements.append(Paragraph(f"Engin : {data['engin']}", styles['Normal']))
    elements.append(Paragraph(f"Heures : {data['heures']}", styles['Normal']))

    doc.build(elements)


if st.button("📄 Générer PDF"):
    generer_pdf()
    st.success("PDF généré ✅")

# -------------------------
# 📊 HISTORIQUE
# -------------------------
if os.path.exists("historique.json"):
    with open("historique.json", "r") as f:
        historique = json.load(f)

    st.subheader("📊 Historique")
    st.write(historique)