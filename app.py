import streamlit as st
from datetime import datetime, timedelta
import json
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from streamlit_drawable_canvas import st_canvas
from PIL import Image as PILImage

from supabase import create_client

# -------------------------
# ☁️ SUPABASE INIT
# -------------------------
SUPABASE_URL = "https://XXXX.supabase.co"
SUPABASE_KEY = "TON_ANON_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="V16 PRO MAX", layout="wide")
st.title("📋 Chantier V16 PRO MAX SUPABASE")

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
# 📸 PHOTOS
# -------------------------
st.subheader("📸 Photos chantier")

photos = st.file_uploader(
    "Ajouter photos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

legendes = []

if photos:
    for i, p in enumerate(photos):
        leg = st.text_input(f"Légende photo {i+1}", key=f"leg{i}")
        legendes.append(leg)

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
# 💾 SAVE SUPABASE + LOCAL
# -------------------------
if st.button("💾 ENREGISTRER CLOUD"):

    # LOCAL BACKUP
    historique = []

    if os.path.exists("historique.json"):
        with open("historique.json", "r") as f:
            historique = json.load(f)

    historique.append(data)

    with open("historique.json", "w") as f:
        json.dump(historique, f, indent=4)

    # CLOUD SUPABASE
    supabase.table("chantiers").insert(data).execute()

    st.success("Sauvegarde cloud + local OK ☁️")

# -------------------------
# 📄 PDF
# -------------------------
def pdf():
    doc = SimpleDocTemplate("rapport.pdf")
    styles = getSampleStyleSheet()
    e = []

    e.append(Paragraph("RAPPORT CHANTIER V16 PRO MAX", styles["Title"]))
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

    if photos:
        e.append(Spacer(1, 20))
        e.append(Paragraph("Photos :", styles["Heading2"]))

        for i, p in enumerate(photos):
            img = PILImage.open(p)
            img.thumbnail((800, 800))
            path = f"p{i}.jpg"
            img.save(path)

            e.append(Image(path, width=300, height=200))

            if i < len(legendes):
                e.append(Paragraph(legendes[i], styles["Normal"]))

    doc.build(e)

# -------------------------
# 📄 DOWNLOAD PDF
# -------------------------
if st.button("📄 PDF"):
    pdf()
    with open("rapport.pdf", "rb") as f:
        st.download_button("Télécharger PDF", f, "rapport.pdf")

# -------------------------
# 📊 EXCEL
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
        st.download_button("Télécharger Excel", f, "chantier.xlsx")

# -------------------------
# ☁️ CLOUD VIEW
# -------------------------
st.subheader("☁️ Historique Cloud")

res = supabase.table("chantiers").select("*").execute()

st.write(res.data)