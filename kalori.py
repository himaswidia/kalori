from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Laporan Kalori Harian", page_icon="🥗", layout="centered"
)

st.title("🥗 Food & Calorie Tracker")
st.write("Catat dan pantau kalori harianmu dengan praktis!")

# Tombol Google Form
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"

st.markdown("### 📝 Input Data Makanan Baru")
st.link_button("👉 Buka Google Form Catat Kalori", GOOGLE_FORM_URL)

st.markdown("---")

# --- MEMBACA DATA DARI GOOGLE SHEETS ---
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

  # Mencari nama kolom yang relevan secara otomatis
  kolom_kalori = [col for col in df.columns if "kalori" in col.lower()]
  kolom_tanggal = [
      col for col in df.columns if "tanggal" in col.lower() or "date" in col.lower()
  ]

  if kolom_kalori and kolom_tanggal:
    col_kalori_nama = kolom_kalori[0]
    col_tgl_nama = kolom_tanggal[0]

    df[col_kalori_nama] = pd.to_numeric(
        df[col_kalori_nama], errors="coerce"
    ).fillna(0)
    df["Tanggal_Saja"] = df[col_tgl_nama].astype(str).str.split(" ").str[0]

    st.subheader("📅 Rekap Kalori Harian")

    daftar_tanggal = sorted(df["Tanggal_Saja"].unique(), reverse=True)
    pilih_tanggal = st.selectbox("Pilih Tanggal:", options=daftar_tanggal)

    df_harian = df[df["Tanggal_Saja"] == pilih_tanggal]
    kalori_harian = int(df_harian[col_kalori_nama].sum())

    st.metric(
        label=f"🎯 Total Kalori pada Tanggal {pilih_tanggal}",
        value=f"{kalori_harian} kcal",
    )

    st.write(f"Daftar makanan pada tanggal {pilih_tanggal}:")
    
    st.dataframe(
        df_harian.drop(columns=["Tanggal_Saja"]),
        use_container_width=True,
        hide_index=True,
    )

    # Menampilkan tautan preview foto per item jika ada
    kolom_foto = [col for col in df_harian.columns if "foto" in col.lower() or "file" in col.lower()]
    if kolom_foto:
      col_foto_nama = kolom_foto[0]
      for index, row in df_harian.iterrows():
        link_foto = row[col_foto_nama]
        if pd.notna(link_foto) and str(link_foto).startswith("http"):
          st.markdown(f"📸 **Foto {row.get('Nama Makanan', 'Makanan')}:** [Buka Gambar di Google Drive]({link_foto})")

else:
  st.warning(
      "Belum ada data di Google Sheets ini, atau pastikan status sharing file"
      " sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )
