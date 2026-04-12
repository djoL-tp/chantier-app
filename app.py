import streamlit as st
from datetime import datetime, date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage
import os

st.set_page_config(page_title="Chantier V8 BTP", layout="centered")

st.title("🚜 APP CHANTIER V8 BTP")

# ======================
# INFOS GENERALES
# ======================
date_chantier = st.date_input("📅 Date", value=date.today())
chantier = st.text_input("🏗️ Chantier")
client = st.text_input("👤 Client")
carburant = st.text_input("⛽ Carburant (L)")
engins = st.text_area("🚜 Engins utilisés")

gps_lat = st.text_input("📍 Latitude")
gps_lon = st.text_input("📍 Longitude")

# ======================
# PHOTOS
# ======================
photos = st.file_uploader(
    "📸 Photos chantier",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ======================
# SIGNATURE OUVRIER
# ======================
st.subheader("✍️ Signature ouvrier")

signature = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=2,
    stroke_color="black",
    background_color="white",
    height=150,
    drawing_mode="freedraw",
    key="signature"
)

# ======================
# PHASES SIMPLIFIEES
# ======================
st.subheader("⏱️ Temps chantier")

h_debut = st.time_input("🕗 Heure début")
h_fin = st.time_input("🕔 Heure fin")

total_heures = 0

if h_debut and h_fin:
    d1 = datetime.combine(date_chantier, h_debut)
    d2 = datetime.combine(date_chantier, h_fin)
    total_heures = (d2 - d1).total_seconds() / 3600


# ======================
# HISTORIQUE
# ======================
def save_history(data):
    file = "historique_chantier.csv"
    exists = os.path.exists(file)

    with open(file, "a", encoding="utf-8") as f:
        if not exists:
            f.write("Date,Chantier,Client,Heures,Carburant\n")
        f.write(",".join(data) + "\n")


# ======================
# PDF GENERATION PRO
# ======================
def create_pdf():

    file = "rapport_chantier.pdf"
    doc = SimpleDocTemplate(file)

    styles = getSampleStyleSheet()
    story = []

    # TITRE
    story.append(Paragraph("RAPPORT CHANTIER V8 BTP", styles["Title"]))
    story.append(Spacer(1, 10))

    # INFOS
    story.append(Paragraph(f"Date : {date_chantier}", styles["Normal"]))
    story.append(Paragraph(f"Chantier : {chantier}", styles["Normal"]))
    story.append(Paragraph(f"Client : {client}", styles["Normal"]))
    story.append(Paragraph(f"Engins : {engins}", styles["Normal"]))
    story.append(Paragraph(f"Carburant : {carburant} L", styles["Normal"]))
    story.append(Paragraph(f"GPS : {gps_lat}, {gps_lon}", styles["Normal"]))
    story.append(Paragraph(f"Temps total : {round(total_heures,2)} h", styles["Normal"]))

    story.append(Spacer(1, 10))

    # PHOTOS
    if photos:
        story.append(Paragraph("📸 Photos chantier", styles["Heading2"]))

        for i, p in enumerate(photos):
            img = PILImage.open(p)
            img_path = f"photo_{i}.png"
            img.save(img_path)

            story.append(Image(img_path, width=300, height=200))
            story.append(Spacer(1, 10))

    # SIGNATURE
    if signature.image_data is not None:
        sig_path = "signature.png"
        PILImage.fromarray(signature.image_data).save(sig_path)

        story.append(Paragraph("✍️ Signature ouvrier", styles["Heading2"]))
        story.append(Image(sig_path, width=200, height=80))

    doc.build(story)
    return file


# ======================
# GENERATION
# ======================
if st.button("📄 Générer PDF V8 BTP"):

    pdf = create_pdf()

    save_history([
        str(date_chantier),
        chantier,
        client,
        str(round(total_heures,2)),
        carburant
    ])

    st.success("✔ PDF généré + sauvegardé")

    with open(pdf, "rb") as f:
        st.download_button("📥 Télécharger PDF", f, file_name="chantier_v8_btp.pdf")


# ======================
# HISTORIQUE
# ======================
st.markdown("---")
st.subheader("📊 Historique chantier")

if os.path.exists("historique_chantier.csv"):
    st.text(open("historique_chantier.csv").read())
else:
    st.info("Aucun historique")