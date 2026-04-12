import streamlit as st
from datetime import datetime, date
import json
import os
import pandas as pd
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Chantier V10 PRO BTP", layout="centered")

st.title("🚜 APP CHANTIER V10 PRO BTP")

# ======================
# FICHIERS DE SAUVEGARDE
# ======================
ENGINS_FILE = "engins.json"
HISTORY_FILE = "historique.csv"

# ======================
# CHARGEMENT ENGINS (PERSISTANT)
# ======================
def load_engins():
    if os.path.exists(ENGINS_FILE):
        with open(ENGINS_FILE, "r") as f:
            return json.load(f)
    return ["OS", "PB-MAN", "PV1"]

def save_engins(data):
    with open(ENGINS_FILE, "w") as f:
        json.dump(data, f)

if "engins" not in st.session_state:
    st.session_state.engins = load_engins()

# ======================
# INFOS CHANTIER
# ======================
date_chantier = st.date_input("📅 Date", value=date.today())
chantier = st.text_input("🏗️ Chantier")
client = st.text_input("👤 Client")
carburant = st.text_input("⛽ Carburant (L)")

# ======================
# ENGINS (SAUVEGARDE PERSISTANTE)
# ======================
st.subheader("🚜 Engins (sauvegardés)")

engin_selectionne = st.multiselect(
    "Choisir les engins utilisés",
    st.session_state.engins
)

new_engin = st.text_input("➕ Ajouter un engin")

if st.button("Ajouter engin"):
    if new_engin and new_engin not in st.session_state.engins:
        st.session_state.engins.append(new_engin)
        save_engins(st.session_state.engins)
        st.success("✔ Engin ajouté et sauvegardé")

# ======================
# HEURES
# ======================
h_debut = st.time_input("🕗 Heure début")
h_fin = st.time_input("🕔 Heure fin")

total_heures = 0
if h_debut and h_fin:
    d1 = datetime.combine(date_chantier, h_debut)
    d2 = datetime.combine(date_chantier, h_fin)
    total_heures = (d2 - d1).total_seconds() / 3600

# ======================
# TRAVAUX
# ======================
travaux = st.text_area("🧱 Travaux effectués")

# ======================
# PHOTOS
# ======================
photos = st.file_uploader(
    "📸 Photos chantier",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ======================
# SIGNATURE
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
# HISTORIQUE
# ======================
def save_history(row):
    df = pd.DataFrame([row])
    if os.path.exists(HISTORY_FILE):
        df.to_csv(HISTORY_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(HISTORY_FILE, index=False)

# ======================
# PDF PRO
# ======================
def create_pdf():

    file = "rapport_chantier.pdf"
    doc = SimpleDocTemplate(file)

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("RAPPORT CHANTIER V10 PRO BTP", styles["Title"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"Date : {date_chantier}", styles["Normal"]))
    story.append(Paragraph(f"Chantier : {chantier}", styles["Normal"]))
    story.append(Paragraph(f"Client : {client}", styles["Normal"]))
    story.append(Paragraph(f"Engins : {', '.join(engin_selectionne)}", styles["Normal"]))
    story.append(Paragraph(f"Carburant : {carburant} L", styles["Normal"]))
    story.append(Paragraph(f"Heures : {round(total_heures,2)} h", styles["Normal"]))

    story.append(Spacer(1, 10))

    # PHOTOS
    if photos:
        story.append(Paragraph("📸 Photos chantier", styles["Heading2"]))
        for i, p in enumerate(photos):
            img = PILImage.open(p)
            path = f"photo_{i}.png"
            img.save(path)
            story.append(Image(path, width=300, height=200))

    # SIGNATURE
    if signature.image_data is not None:
        sig = PILImage.fromarray(signature.image_data)
        sig_path = "signature.png"
        sig.save(sig_path)

        story.append(Spacer(1, 10))
        story.append(Paragraph("✍️ Signature ouvrier", styles["Heading2"]))
        story.append(Image(sig_path, width=200, height=80))

    doc.build(story)
    return file


# ======================
# EXPORT EXCEL
# ======================
def export_excel():
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
        excel_file = "historique.xlsx"
        df.to_excel(excel_file, index=False)
        return excel_file
    return None


# ======================
# GENERATION
# ======================
if st.button("📄 Générer rapport V10"):

    pdf = create_pdf()

    save_history({
        "Date": str(date_chantier),
        "Chantier": chantier,
        "Client": client,
        "Engins": ",".join(engin_selectionne),
        "Heures": round(total_heures,2),
        "Carburant": carburant
    })

    st.success("✔ Rapport généré")

    with open(pdf, "rb") as f:
        st.download_button("📥 Télécharger PDF", f, file_name="chantier_v10.pdf")

# ======================
# HISTORIQUE APP
# ======================
st.markdown("---")
st.subheader("📊 Historique chantier")

if os.path.exists(HISTORY_FILE):
    df = pd.read_csv(HISTORY_FILE)
    st.dataframe(df)

    excel = export_excel()
    if excel:
        with open(excel, "rb") as f:
            st.download_button("📥 Export Excel", f, file_name="historique.xlsx")
else:
    st.info("Aucun historique pour le moment")