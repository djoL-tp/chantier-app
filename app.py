import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

st.set_page_config(page_title="Chantier V17 PRO MAX", layout="wide")

# -------------------------
# INIT
# -------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# -------------------------
# TITRE
# -------------------------
st.title("📋 Chantier V17 PRO MAX")

# -------------------------
# FORMULAIRE
# -------------------------
with st.form("form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date", datetime.today())
        ouvrier = st.text_input("Ouvrier")
        chantier = st.text_input("Chantier")

    with col2:
        h_debut_matin = st.time_input("Début matin")
        h_fin_matin = st.time_input("Fin matin")
        h_debut_aprem = st.time_input("Début après-midi")
        h_fin_journee = st.time_input("Fin journée")

    travail = st.text_area("Travail effectué")

    submit = st.form_submit_button("Ajouter")

    if submit:
        matin = (datetime.combine(date, h_fin_matin) - datetime.combine(date, h_debut_matin)).seconds / 3600
        aprem = (datetime.combine(date, h_fin_journee) - datetime.combine(date, h_debut_aprem)).seconds / 3600
        total = matin + aprem

        amplitude = f"{h_debut_matin.strftime('%H:%M')} / {h_fin_matin.strftime('%H:%M')} - {h_debut_aprem.strftime('%H:%M')} / {h_fin_journee.strftime('%H:%M')}"

        st.session_state.data.append({
            "date": date.strftime("%d/%m/%Y"),
            "ouvrier": ouvrier,
            "chantier": chantier,
            "matin": round(matin, 2),
            "aprem": round(aprem, 2),
            "total": round(total, 2),
            "amplitude": amplitude,
            "travail": travail
        })

# -------------------------
# DATA
# -------------------------
df = pd.DataFrame(st.session_state.data)

if not df.empty:
    st.subheader("📊 Données")
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # STATS
    # -------------------------
    st.subheader("📈 Statistiques")

    df["date_dt"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

    semaine = df[df["date_dt"] >= (datetime.today() - pd.Timedelta(days=7))]
    mois = df[df["date_dt"] >= (datetime.today() - pd.Timedelta(days=30))]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total général", f"{df['total'].sum():.2f} h")
    col2.metric("7 derniers jours", f"{semaine['total'].sum():.2f} h")
    col3.metric("30 derniers jours", f"{mois['total'].sum():.2f} h")

# -------------------------
# PDF EXPORT
# -------------------------
def export_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()

    # 🔥 POLICE UNICODE (clé du problème)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
    pdf.set_font("DejaVu", size=10)

    # TITRE
    pdf.set_font("DejaVu", size=16)
    pdf.cell(0, 10, "RAPPORT CHANTIER", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("DejaVu", size=10)

    total_general = 0

    for _, row in dataframe.iterrows():

        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, f"{row['date']} - {row['ouvrier']} - {row['chantier']}", ln=True, fill=True)

        # 🔴 AMPLITUDE + HEURES
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 6, f"Amplitude : {row['amplitude']}", ln=True)
        pdf.cell(0, 6, f"Matin : {row['matin']} h", ln=True)
        pdf.cell(0, 6, f"Après-midi : {row['aprem']} h", ln=True)

        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, f"Total : {row['total']} h", ln=True)

        # 🔥 TEXTE SANS BUG
        pdf.multi_cell(0, 6, f"Travail effectué : {row['travail']}")

        pdf.ln(4)
        total_general += row["total"]

    pdf.ln(5)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(0, 10, f"TOTAL GENERAL : {total_general:.2f} h", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# -------------------------
# EXPORT
# -------------------------
if not df.empty:

    col1, col2 = st.columns(2)

    with col1:
        pdf_file = export_pdf(df)
        st.download_button(
            "📄 Télécharger PDF",
            pdf_file,
            file_name="rapport_chantier.pdf",
            mime="application/pdf"
        )

    with col2:
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            "📊 Télécharger Excel",
            buffer.getvalue(),
            file_name="rapport_chantier.xlsx"
        )