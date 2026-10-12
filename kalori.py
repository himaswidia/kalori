import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Catat makanan harianmu dengan mudah melalui Google Form resmi di bawah"
    " ini!"
)

# --- 1. TOMBOL LINK MENUJU GOOGLE FORM (100% Aman & Tanpa Blokir) ---
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"

st.markdown("### 📝 Input Data Makanan Baru")
st.markdown(
    "Klik tombol di bawah untuk membuka form pencatatan makanan dan upload"
    " foto:"
)
st.link_button("👉 Buka Google Form Catat Kalori", GOOGLE_FORM_URL)

st.markdown("---")

# --- 2. MENAMPILKAN RIWAYAT & TOTAL KALORI DARI GOOGLE SHEETS ---
SHEET_ID = "1UW-qYpzKF8U0z1AmqGjlgqXf8O1Ppk7xwx5CHIpAeB4"
SHEET_NAME = "Form_Responses_1"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"


@st.cache_data(ttl=5)
def load_data():
  try:
    df = pd.read_csv(url)
    return df
  except:
    return None


df = load_data()

st.subheader("📜 Riwayat Makanan & Total Kalori")

if df is not None and not df.empty:
  df.columns = df.columns.str.strip()

  # Otomatis mencari kolom yang berisi kata 'kalori'
  kolom_kalori = [col for col in df.columns if "kalori" in col.lower()]
  if kolom_kalori:
    col_nama = kolom_kalori[0]
    df[col_nama] = pd.to_numeric(df[col_nama], errors="coerce").fillna(0)
    total_kalori = int(df[col_nama].sum())
    st.metric(
        label="🔥 Total Kalori Masuk Keseluruhan", value=f"{total_kalori} kcal"
    )

  st.dataframe(df, use_container_width=True)
else:
  st.info(
      "Belum ada data masuk atau pastikan Google Sheets sudah diset ke 'Siapa"
      " saja yang memiliki link dapat melihat'."
  )
