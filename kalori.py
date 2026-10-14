from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Daily Habit & Health Tracker", page_icon="🎯", layout="centered"
)

st.title("🎯 Daily Habit & Health Tracker")
st.write(
    "Catat jurnal makanan, rutinitas olahraga, dan pantau kebiasaan sehatmu"
    " setiap hari!"
)

# Tombol menuju Google Form (silakan sesuaikan link form baru jika sudah dibuat)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"

st.markdown("### 📝 Input Jurnal & Kebiasaan Baru")
st.link_button("👉 Buka Google Form Pencatatan", GOOGLE_FORM_URL)

st.markdown("---")

# --- MEMBACA DATA DARI GOOGLE SHEETS ---
# Menggunakan Google Sheets ID yang sama
SHEET_ID = "1uvO_4PJnCkCOUJEl4DpPnabBW6AtjBEnho2ypiRH-GE"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"


@st.cache_data(ttl=2)
def load_data():
  try:
    df = pd.read_csv(url)
    return df
  except Exception as e:
    return None


df = load_data()

if df is not None and not df.empty:
  # Membersihkan spasi pada nama kolom
  df.columns = df.columns.str.strip()

  # Mencari kolom tanggal secara otomatis
  kolom_tanggal = [
      col for col in df.columns if "tanggal" in col.lower() or "date" in col.lower()
  ]

  if kolom_tanggal:
    col_tgl_nama = kolom_tanggal[0]
    df["Tanggal_Saja"] = df[col_tgl_nama].astype(str).str.split(" ").str[0]

    st.subheader("📅 Rekap Kebiasaan & Aktivitas Harian")

    daftar_tanggal = sorted(df["Tanggal_Saja"].unique(), reverse=True)
    pilih_tanggal = st.selectbox("Pilih Tanggal:", options=daftar_tanggal)

    # Filter data berdasarkan tanggal yang dipilih
    df_harian = df[df["Tanggal_Saja"] == pilih_tanggal]

    st.write(f"Catatan aktivitas & makanan pada tanggal **{pilih_tanggal}**:")
    
    st.dataframe(
        df_harian.drop(columns=["Tanggal_Saja"]),
        use_container_width=True,
        hide_index=True,
    )

    # Menampilkan tautan preview foto jika ada kolom foto/file
    kolom_foto = [col for col in df_harian.columns if "foto" in col.lower() or "file" in col.lower() or "gambar" in col.lower()]
    if kolom_foto:
      col_foto_nama = kolom_foto[0]
      for index, row in df_harian.iterrows():
        link_foto = row[col_foto_nama]
        if pd.notna(link_foto) and str(link_foto).startswith("http"):
          st.markdown(f"📸 **Dokumentasi/Foto:** [Buka Gambar di Google Drive]({link_foto})")

else:
  st.warning(
      "Belum ada data di Google Sheets, atau pastikan status sharing file"
      " sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )
