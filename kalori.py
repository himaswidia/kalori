from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Daily Habit & Health Tracker", page_icon="🎯", layout="centered"
)

st.title("🎯 Daily Habit & Health Tracker")
st.write("Laporan harian kebiasaan, makanan, dan aktivitas fisikmu!")

# Tombol Google Form
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"

st.markdown("### 📝 Input Jurnal & Aktivitas Baru")
st.link_button("👉 Buka Google Form Pencatatan", GOOGLE_FORM_URL)

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

  # Mencari kolom tanggal secara otomatis
  kolom_tanggal = [
      col for col in df.columns if "tanggal" in col.lower() or "date" in col.lower()
  ]

  if kolom_tanggal:
    col_tgl_nama = kolom_tanggal[0]
    df["Tanggal_Saja"] = df[col_tgl_nama].astype(str).str.split(" ").str[0]

    st.subheader("📅 Laporan Harian")

    daftar_tanggal = sorted(df["Tanggal_Saja"].unique(), reverse=True)
    pilih_tanggal = st.selectbox("Pilih Tanggal Laporan:", options=daftar_tanggal)

    # Filter data berdasarkan tanggal yang dipilih
    df_harian = df[df["Tanggal_Saja"] == pilih_tanggal]

    st.markdown(f"### 📋 Ringkasan Tanggal: {pilih_tanggal}")

    # Menampilkan metrik ringkasan dari jam tangan
    kolom_langkah = [col for col in df.columns if "langkah" in col.lower() or "step" in col.lower()]
    kolom_kalori_jam = [col for col in df.columns if "kalori" in col.lower() or "kcal" in col.lower()]

    col1, col2 = st.columns(2)
    
    if kolom_langkah:
      col_langkah_nama = kolom_langkah[0]
      df_harian[col_langkah_nama] = pd.to_numeric(df_harian[col_langkah_nama], errors="coerce").fillna(0)
      total_langkah = int(df_harian[col_langkah_nama].max())
      with col1:
        st.metric(label="👟 Total Langkah", value=f"{total_langkah:,} steps")

    if kolom_kalori_jam:
      col_kal_nama = kolom_kalori_jam[0]
      df_harian[col_kal_nama] = pd.to_numeric(df_harian[col_kal_nama], errors="coerce").fillna(0)
      total_kal_jam = int(df_harian[col_kal_nama].max())
      with col2:
        st.metric(label="🔥 Kalori Jam Tangan", value=f"{total_kal_jam} kcal")

    st.markdown("---")
    st.write("**Catatan Makanan & Aktivitas pada Hari Ini:**")

    # Menampilkan tabel data harian secara rapi dan bersih
    st.dataframe(
        df_harian.drop(columns=["Tanggal_Saja"]),
        use_container_width=True,
        hide_index=True,
    )

else:
  st.warning(
      "Belum ada data masuk di Google Sheets, atau pastikan status sharing"
      " file sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )
