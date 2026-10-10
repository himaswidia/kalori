from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Catat makanan, upload foto, dan pantau kalori harianmu dengan mudah di"
    " sini."
)

# Form Input Interaktif (Aman & Tanpa Error Secrets)
with st.form("form_kalori", clear_on_submit=True):
  st.subheader("➕ Tambah Catatan Makanan")
  tanggal = st.date_input("Tanggal", value=datetime.now())
  nama_makanan = st.text_input("Nama Makanan & Minuman")
  jumlah_kalori = st.number_input(
      "Jumlah Kalori (kcal)", min_value=0, step=10, value=100
  )

  # Fitur Upload Foto Makanan
  uploaded_file = st.file_uploader(
      "Upload Foto Makanan (JPG/PNG)", type=["jpg", "jpeg", "png"]
  )

  submit_button = st.form_submit_button(label="Simpan Catatan")

  if submit_button:
    if nama_makanan.strip() != "":
      nama_foto = uploaded_file.name if uploaded_file is not None else "Tanpa Foto"
      st.success(f"Berhasil dicatat: {nama_makanan} ({jumlah_kalori} kcal)!")

      # Jika ada foto yang di-upload, tampilkan preview-nya langsung di layar
      if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption=f"Foto: {nama_makanan}",
            use_container_width=True,
        )

      st.info(
          "💡 Tips: Data di atas siap disalin atau dicatat ke Google Sheets"
          " utama kamu."
      )
    else:
      st.warning("Nama makanan tidak boleh kosong!")

# Membaca Data dari Google Sheets Publik (Menggunakan Sheet ID kamu)
SHEET_ID = "1UW-qYpzKF8U0z1AmqGjlgqXf8O1Ppk7xwx5CHIpAeB4"
SHEET_NAME = "kalori"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"


@st.cache_data(ttl=10)
def load_data():
  try:
    df = pd.read_csv(url)
    return df
  except:
    return None


df = load_data()

if df is not None and not df.empty:
  df.columns = df.columns.str.strip()
  if "Jumlah Kalori" in df.columns:
    df["Jumlah Kalori"] = pd.to_numeric(
        df["Jumlah Kalori"], errors="coerce"
    ).fillna(0)
    total_kalori = int(df["Jumlah Kalori"].sum())
    st.metric(
        label="🔥 Total Kalori Masuk Keseluruhan", value=f"{total_kalori} kcal"
    )

  st.subheader("📜 Riwayat Makanan dari Google Sheets")
  st.dataframe(df, use_container_width=True)
else:
  st.info(
      "Belum ada data riwayat di Google Sheets, atau pastikan link Google"
      " Sheets sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )