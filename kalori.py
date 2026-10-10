import pandas as pd
import streamlit as st

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write(
    "Laporan harian apa saja yang aku makan dan total kalori yang masuk secara"
    " real-time dari Google Sheets."
)

# ID Google Sheets kamu
SHEET_ID = "1UW-qYpzKF8U0z1AmqGjlgqXf8O1Ppk7xwx5CHIpAeB4"
SHEET_NAME = "kalori"  # Sesuaikan dengan nama tab di bawah Google Sheets kamu jika berbeda
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"


@st.cache_data(ttl=30)  # Cache data selama 30 detik
def load_data():
  try:
    df = pd.read_csv(url)
    return df
  except Exception as e:
    return None


df = load_data()

if df is not None and not df.empty:
  # Bersihkan nama kolom dari spasi berlebih
  df.columns = df.columns.str.strip()

  # Pastikan kolom Jumlah Kalori bertipe angka
  if "Jumlah Kalori" in df.columns:
    df["Jumlah Kalori"] = pd.to_numeric(df["Jumlah Kalori"], errors="coerce").fillna(0)

    # Hitung total kalori
    total_kalori = int(df["Jumlah Kalori"].sum())
    st.metric(
        label="🔥 Total Kalori Masuk Keseluruhan", value=f"{total_kalori} kcal"
    )

  # Tampilkan tabel data
  st.subheader("📜 Riwayat Makanan")
  st.dataframe(df, use_container_width=True)

  # Tampilkan galeri foto jika ada kolom Link Foto
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
      tanggal = row["Tanggal"] if pd.notna(row["Tanggal"]) else ""

      st.write(f"**{makanan}** — *{kalori} kcal* ({tanggal})")

      link_foto = row["Link Foto"]
      if pd.notna(link_foto) and str(link_foto).startswith("http"):
        st.image(str(link_foto), width=300)
      st.divider()
else:
  st.info(
      "Belum ada data di Google Sheets atau pastikan status sharing sudah"
      " diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )