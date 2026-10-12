import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Catat makanan harianmu melalui Google Form di bawah ini. Data dan foto"
    " akan otomatis tersimpan ke Google Drive & Sheets!"
)

# --- 1. EMBED GOOGLE FORM (100% Aman & Resmi) ---
# Masukkan link Google Form kamu di sini
GOOGLE_FORM_URL = "MASUKKAN_LINK_GOOGLE_FORM_ANDA_DI_SINI"

st.markdown("### 📝 Form Input Makanan")
st.components.v1.iframe(GOOGLE_FORM_URL, height=650, scrolling=True)

st.markdown("---")

# --- 2. MENAMPILKAN RIWAYAT & TOTAL KALORI DARI GOOGLE SHEETS ---
SHEET_ID = (  # Pastikan ID ini sesuai dengan file Google Sheets "kalori" kamu
    "1UW-qYpzKF8U0z1AmqGjlgqXf8O1Ppk7xwx5CHIpAeB4"
)
SHEET_NAME = (  # Nama sheet default dari Google Form biasanya 'Form Responses 1'
    "Form Responses 1"
)
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
