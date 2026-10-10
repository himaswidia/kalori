from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Catat makanan dan pantau kalori harianmu. Data akan langsung tersimpan ke"
    " Google Sheets!"
)


# Koneksi aman ke Google Sheets menggunakan gspread & Secrets
@st.cache_resource
def init_connection():
  scope = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


try:
  client = init_connection()
  # Buka spreadsheet berdasarkan nama atau ID
  sheet = client.open("kalori").sheet1  # atau gunakan nama lembar kerja/sheet kamu
  koneksi_berhasil = True
except Exception as e:
  koneksi_berhasil = False
  st.error(
      "Gagal terhubung ke Google Sheets. Pastikan Secrets sudah diatur dengan"
      f" benar. Detail: {e}"
  )

if koneksi_berhasil:
  # Form Input
  with st.form("form_kalori", clear_on_submit=True):
    st.subheader("➕ Tambah Catatan Makanan")
    tanggal = st.date_input("Tanggal", value=datetime.now())
    nama_makanan = st.text_input("Nama Makanan & Minuman")
    jumlah_kalori = st.number_input(
        "Jumlah Kalori (kcal)", min_value=0, step=10, value=100
    )
    uploaded_file = st.file_uploader(
        "Upload Foto Makanan", type=["jpg", "jpeg", "png"]
    )

    submit_button = st.form_submit_button(label="Simpan Data ke Google Sheets")

    if submit_button:
      if nama_makanan.strip() != "":
        nama_foto = uploaded_file.name if uploaded_file is not None else "-"
        tanggal_str = tanggal.strftime("%Y-%m-%d")

        # Simpan baris baru ke Google Sheets
        sheet.append_row([tanggal_str, nama_makanan, jumlah_kalori, nama_foto])

        st.success(
            f"Berhasil! {nama_makanan} ({jumlah_kalori} kcal) dengan foto"
            f" '{nama_foto}' telah disimpan ke Google Sheets."
        )
      else:
        st.warning("Nama makanan tidak boleh kosong!")

  # Menampilkan Data dari Google Sheets
  st.subheader("📜 Riwayat Makanan")
  try:
    data = sheet.get_all_records()
    if data:
      df = pd.DataFrame(data)
      if "Jumlah Kalori" in df.columns:
        df["Jumlah Kalori"] = pd.to_numeric(
            df["Jumlah Kalori"], errors="coerce"
        ).fillna(0)
        total_kalori = int(df["Jumlah Kalori"].sum())
        st.metric(
            label="🔥 Total Kalori Masuk Keseluruhan",
            value=f"{total_kalori} kcal",
        )
      st.dataframe(df, use_container_width=True)
    else:
      st.info(
          "Google Sheets masih kosong. Silakan tambahkan data pertamamu di"
          " atas!"
      )
  except Exception as e:
    st.info("Belum ada data atau format kolom belum sesuai.")