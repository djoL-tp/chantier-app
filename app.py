import streamlit as st
from datetime import datetime
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="V17 PRO MAX", layout="wide")

st.title("🚧 V17 PRO MAX - Chantier")

# =========================
# DATE FR
# =========================
def date_fr():
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    now = datetime.now()
    return f"{jours[now.weekday()]} {now.day} {mois[now.month - 1]} {now.year}"

# =========================
# DATA
# =========================
if "data" not in st.session_state:
    st.session_state.data = []

# =========================
# INPUT
# =========================
st.subheader("📝 Saisie journée")

chantier = st.text_input("Chantier")
engin = st.text_input("Engin")

h_matin = st.number_input("Heures matin", 0.0, 12.0, step=0.5)
h_aprem = st.number_input("Heures après-midi", 0.0, 12.0, step=0.5)

total = h_matin + h_aprem

if st.button("➕ Ajouter"):
    st.session_state.data.append({
        "Date": date_fr(),
        "Chantier": chantier,
        "Engin": engin,
        "Matin": h_matin,
        "Après-midi": h_aprem,
        "Total": total
    })
    st.success("Ajouté ✔️")

# =========================
# TABLE
# =========================
df = pd.DataFrame(st.session_state.data)
st.dataframe(df, use_container_width=True)

# =========================
# PDF
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "RAPPORT CHANTIER V17 PRO MAX", ln=True, align="C")
        self.ln(5)

def export_pdf(dataframe):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for _, row in dataframe.iterrows():

        # 🔥 AJOUT AMPLITUDE FIXE DEMANDÉE
        amplitude = "8h00 / 12h00 - 13h00 / 17h30"

        ligne = (
            f"{row['Date']} | "
            f"{row['Chantier']} | "
            f"{row['Engin']} | "
            f"Matin: {row['Matin']}h | "
            f"Aprem: {row['Après-midi']}h | "
            f"Total: {row['Total']}h | "
            f"{amplitude}"
        )

        pdf.cell(0, 8, ligne, ln=True)

    file = "chantier.pdf"
    pdf.output(file)
    return file

# =========================
# EXPORT
# =========================
if not df.empty:

    if st.button("📄 Export PDF"):
        file = export_pdf(df)
        with open(file, "rb") as f:
            st.download_button("Télécharger PDF", f, file_name="chantier.pdf")