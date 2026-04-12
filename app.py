import streamlit as st
from datetime import datetime
from PIL import Image
import base64

st.set_page_config(page_title="Chantier PRO GPS", layout="centered")

st.title("🚜 App Chantier PRO (GPS + Photos)")

# ======================
# INFOS CHANTIER
# ======================
chantier = st.text_input("🏗️ Chantier / Entreprise")
client = st.text_input("👤 Client")

# ======================
# ENGINS (modifiable par toi)
# ======================
engins = st.multiselect(
    "🚜 Engins utilisés (choisis plusieurs)",
    [
        "Mini-pelle",
        "Pelle 8T",
        "Pelle 20T",
        "Chargeur",
        "Bulldozer",
        "Compacteur",
        "Camion 6x4",
        "Camion 8x4",
        "Tracto-pelle",
        "Nacelle",
        "Autre"
    ]
)

# ======================
# HEURES
# ======================
col1, col2 = st.columns(2)

with col1:
    heure_debut = st.time_input("🕗 Heure début")

with col2:
    heure_fin = st.time_input("🕔 Heure fin")

# ======================
# TRAVAUX
# ======================
travaux = st.text_area("🧱 Description des travaux")

# ======================
# GPS (navigateur)
# ======================
st.markdown("### 📍 Localisation chantier")
st.info("Autorise la localisation sur Safari pour récupérer le GPS")

gps_lat = st.text_input("Latitude (auto ou manuel)")
gps_lon = st.text_input("Longitude (auto ou manuel)")

# ======================
# PHOTOS
# ======================
photos = st.file_uploader(
    "📸 Photos chantier",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# ======================
# CALCUL TEMPS
# ======================
if heure_debut and heure_fin:
    debut = datetime.combine(datetime.today(), heure_debut)
    fin = datetime.combine(datetime.today(), heure_fin)

    duree = fin - debut
    heures = duree.total_seconds() / 3600
else:
    heures = None

# ======================
# RAPPORT
# ======================
if st.button("📄 Générer rapport chantier"):

    st.subheader("📄 RAPPORT CHANTIER")

    st.write("🏗️ Chantier :", chantier)
    st.write("👤 Client :", client)
    st.write("🚜 Engins :", ", ".join(engins))
    st.write("🧱 Travaux :", travaux)

    if heures:
        st.write(f"⏱️ Temps total : {heures:.2f} h")

    st.write("📍 GPS :", gps_lat, gps_lon)

    st.markdown("---")
    st.success("✔ Rapport généré")

    # Affichage photos
    if photos:
        st.subheader("📸 Photos chantier")
        for photo in photos:
            st.image(photo)