from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Catat makananmu di sini, dan datanya akan langsung tersimpan otomatis ke"
    " Google Sheets!"
)


# Fungsi untuk menghubungkan ke Google Sheets
def koneksi_gspread():
  # Mengambil kredensial dari rahasia Streamlit (Streamlit Secrets)
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  try:
    # Membaca credentials dari st.secrets (akan kita atur nanti di Streamlit Cloud)
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Buka Google Sheets berdasarkan ID
    sheet_id = "1UW-qYpzKF8U0z1AmqGjlgqXf8O1Ppk7xwx5CHIpAeB4"
    sheet = client.open_by_key(sheet_id).worksheet("kalori")
    return sheet
  except Exception as e:
    return None


sheet = koneksi_gspread()

# Jika koneksi berhasil, tampilkan form input
if sheet is not None:
  with st.form("form_kalori", clear_on_submit=True):
    st.subheader("➕ Tambah Catatan Makanan")
    tanggal = st.date_input("Tanggal", value=datetime.now())
    nama_makanan = st.text_input("Nama Makanan & Minuman")
    jumlah_kalori = st.number_input(
        "Jumlah Kalori (kcal)", min_value=0, step=10, value=100
    )
    link_foto = st.text_input(
        "Link Foto (Opsional - paste link gambar dari Google Drive/Imgur)"
    )

    submit_button = st.form_submit_button(label="Simpan ke Google Sheets")

    if submit_button:
      if nama_makanan.strip() != "":
        # Format tanggal jadi string
        tgl_str = tanggal.strftime("%Y-%m-%d")
        # Masukkan baris baru ke Google Sheets: [Tanggal, Nama Makanan, Jumlah Kalori, Link Foto]
        sheet.append_row([tgl_str, nama_makanan, jumlah_kalori, link_foto])
        st.success(
            f"Berhasil menyimpan '{nama_makanan}' ({jumlah_kalori} kcal) ke"
            " Google Sheets!"
        )
        st.rerun()
      else:
        st.warning("Nama makanan tidak boleh kosong!")

  # Muat data untuk ditampilkan
  try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
      df.columns = df.columns.str.strip()

      if "Jumlah Kalori" in df.columns:
        df["Jumlah Kalori"] = pd.to_numeric(
            df["Jumlah Kalori"], errors="coerce"
        ).fillna(0)
        total_kalori = int(df["Jumlah Kalori"].sum())
        st.metric(
            label="🔥 Total Kalori Masuk Keseluruhan",
            value=f"{total_kalori} kcal",
        )

      st.subheader("📜 Riwayat Makanan")
      st.dataframe(df, use_container_width=True)

      if "Link Foto" in df.columns and "Nama Makanan" in df.columns:
        st.subheader("📸 Galeri Makanan")
        for index, row in df.iterrows():
          makanan = (
              row["Nama Makanan"]
              if pd.notna(row["Nama Makanan"])
              else "Tanpa Nama"
          )
          kalori = (
              int(row["Jumlah Kalori"])
              if pd.notna(row["Jumlah Kalori"])
              else 0
          )
          tgl = row["Tanggal"] if pd.notna(row["Tanggal"]) else ""

          st.write(f"**{makanan}** — *{kalori} kcal* ({tgl})")
          foto = row["Link Foto"]
          if pd.notna(foto) and str(foto).startswith("http"):
            st.image(str(foto), width=300)
          st.divider()
    else:
      st.info("Google Sheets masih kosong. Silakan tambah data lewat form di atas!")
  except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets: {e}")
else:
  st.error(
      "Koneksi ke Google Sheets belum terhubung. Pastikan kamu sudah mengatur"
      " *Secrets* Google Service Account di Streamlit Cloud."
  )