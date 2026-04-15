import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="Chantier PRO MAX", layout="wide")

# -------------------------
# INIT
# -------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# -------------------------
# TITRE
# -------------------------
st.title("📋 Suivi de chantier ULTRA PRO")

# -------------------------
# FORMULAIRE
# -------------------------
with st.form("formulaire"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date", datetime.today())
        ouvrier = st.text_input("Nom ouvrier")
        chantier = st.text_input("Chantier")

    with col2:
        debut_matin = st.time_input("Début matin")
        fin_matin = st.time_input("Fin matin")
        debut_aprem = st.time_input("Début après-midi")
        fin_journee = st.time_input("Fin journée")

    travail = st.text_area("Travail effectué")

    photo = st.file_uploader("📸 Photo chantier", type=["jpg", "png"])
    signature = st.file_uploader("✍️ Signature", type=["png"])

    submit = st.form_submit_button("Ajouter")

    if submit:
        h_matin = (datetime.combine(date, fin_matin) - datetime.combine(date, debut_matin)).seconds / 3600
        h_aprem = (datetime.combine(date, fin_journee) - datetime.combine(date, debut_aprem)).seconds / 3600
        total = h_matin + h_aprem

        st.session_state.data.append({
            "date": date.strftime("%d/%m/%Y"),
            "ouvrier": ouvrier,
            "chantier": chantier,
            "matin": round(h_matin, 2),
            "aprem": round(h_aprem, 2),
            "total": round(total, 2),
            "travail": travail,
            "photo": photo,
            "signature": signature
        })

# -------------------------
# DATA
# -------------------------
df = pd.DataFrame(st.session_state.data)

if not df.empty:
    st.subheader("📊 Données")
    st.dataframe(df.drop(columns=["photo", "signature"]), use_container_width=True)

    # -------------------------
    # STATS
    # -------------------------
    st.subheader("📈 Statistiques")

    total_heure = df["total"].sum()
    st.metric("Total heures", f"{round(total_heure,2)} h")

# -------------------------
# PDF EXPORT PRO
# -------------------------
def export_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()

    # 🔥 POLICE UNICODE (OBLIGATOIRE)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
    pdf.set_font("DejaVu", size=10)

    # TITRE
    pdf.set_font("DejaVu", size=16)
    pdf.cell(0, 10, "RAPPORT DE CHANTIER", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("DejaVu", size=10)

    total_general = 0

    for _, row in dataframe.iterrows():

        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, f"{row['date']} - {row['ouvrier']} - {row['chantier']}", ln=True, fill=True)

        # MATIN
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 6, f"Matin : {row['matin']} h", ln=True)

        # APREM
        pdf.cell(0, 6, f"Après-midi : {row['aprem']} h", ln=True)

        pdf.set_text_color(0, 0, 0)

        pdf.cell(0, 6, f"Total : {row['total']} h", ln=True)

        pdf.multi_cell(0, 6, f"Travail effectué : {row['travail']}")

        # PHOTO
        if row["photo"] is not None:
            image = Image.open(row["photo"])
            img_path = f"/tmp/photo_{_}.jpg"
            image.save(img_path)
            pdf.image(img_path, w=100)

        # SIGNATURE
        if row["signature"] is not None:
            sign = Image.open(row["signature"])
            sign_path = f"/tmp/sign_{_}.png"
            sign.save(sign_path)
            pdf.image(sign_path, w=50)

        pdf.ln(5)

        total_general += row["total"]

    pdf.ln(5)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 10, f"TOTAL GENERAL : {round(total_general,2)} h", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# -------------------------
# EXPORT
# -------------------------
if not df.empty:

    col1, col2 = st.columns(2)

    with col1:
        pdf_file = export_pdf(df)
        st.download_button(
            "📄 Télécharger PDF PRO",
            pdf_file,
            file_name="rapport_chantier.pdf",
            mime="application/pdf"
        )

    with col2:
        excel_buffer = io.BytesIO()
        df.drop(columns=["photo", "signature"]).to_excel(excel_buffer, index=False)
        st.download_button(
            "📊 Télécharger Excel",
            excel_buffer.getvalue(),
            file_name="rapport_chantier.xlsx"
        )