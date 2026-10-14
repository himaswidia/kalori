from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Daily Habit & Health Tracker", page_icon="🎯", layout="centered"
)

st.title("🎯 Daily Habit & Health Tracker")
st.write("Laporan harian kebiasaan, makanan, dan aktivitas fisikmu!")

# Tombol Google Form untuk Makan dan Olahraga
col_f1, col_f2 = st.columns(2)
with col_f1:
  FORM_MAKAN_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"
  st.link_button("📝 Input Jurnal Makan", FORM_MAKAN_URL, use_container_width=True)
with col_f2:
  FORM_OLAHRAGA_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeE-AB9MLf1-Kf3puAKa0kUra7X4oAE6VY8SYvW4v6nO1bEcQ/viewform"
  st.link_button("🏋️ Input Olahraga & Jam", FORM_OLAHRAGA_URL, use_container_width=True)

st.markdown("---")

# --- MEMBACA DATA DARI KEDUA GOOGLE SHEETS ---
SHEET_MAKAN_ID = "1uvO_4PJnCkCOUJEl4DpPnabBW6AtjBEnho2ypiRH-GE"
SHEET_OLAHRAGA_ID = "1ZKj2uBAd5IyXHxGPEgHhMKq51uerSnQAuSLKqgepaf0"

url_makan = f"https://docs.google.com/spreadsheets/d/{SHEET_MAKAN_ID}/gviz/tq?tqx=out:csv"
url_olahraga = f"https://docs.google.com/spreadsheets/d/{SHEET_OLAHRAGA_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=2)
def load_all_data():
  try:
    df_makan = pd.read_csv(url_makan)
  except Exception:
    df_makan = pd.DataFrame()

  try:
    df_olahraga = pd.read_csv(url_olahraga)
  except Exception:
    df_olahraga = pd.DataFrame()

  return df_makan, df_olahraga

df_makan, df_olahraga = load_all_data()

# Membersihkan spasi kolom jika data tidak kosong
if not df_makan.empty:
  df_makan.columns = df_makan.columns.str.strip()
  kolom_tgl_makan = next((col for col in df_makan.columns if "tanggal" in col.lower() or "date" in col.lower()), None)
  if kolom_tgl_makan:
    df_makan["Tanggal_Saja"] = df_makan[kolom_tgl_makan].astype(str).str.split(" ").str[0]

if not df_olahraga.empty:
  df_olahraga.columns = df_olahraga.columns.str.strip()
  kolom_tgl_olahraga = next((col for col in df_olahraga.columns if "tanggal" in col.lower() or "date" in col.lower()), None)
  if kolom_tgl_olahraga:
    df_olahraga["Tanggal_Saja"] = df_olahraga[kolom_tgl_olahraga].astype(str).str.split(" ").str[0]

# Mendapatkan daftar seluruh tanggal unik dari kedua sheet
semua_tanggal = set()
if not df_makan.empty and "Tanggal_Saja" in df_makan.columns:
  semua_tanggal.update(df_makan["Tanggal_Saja"].dropna().unique())
if not df_olahraga.empty and "Tanggal_Saja" in df_olahraga.columns:
  semua_tanggal.update(df_olahraga["Tanggal_Saja"].dropna().unique())

if semua_tanggal:
  daftar_tanggal = sorted(list(semua_tanggal), reverse=True)

  st.subheader("📅 Laporan Harian Terpadu")
  pilih_tanggal = st.selectbox("Pilih Tanggal Laporan:", options=daftar_tanggal)

  st.markdown(f"### 📋 Ringkasan Tanggal: {pilih_tanggal}")

  # --- BAGIAN 1: DATA OLAHRAGA & JAM TANGAN ---
  if not df_olahraga.empty and "Tanggal_Saja" in df_olahraga.columns:
    df_olahraga_harian = df_olahraga[df_olahraga["Tanggal_Saja"] == pilih_tanggal]
    
    if not df_olahraga_harian.empty:
      st.markdown("#### 🏃‍♂️ Aktivitas Fisik & Smartwatch")
      
      col_langkah = next((col for col in df_olahraga_harian.columns if "langkah" in col.lower() or "step" in col.lower()), None)
      col_kalori = next((col for col in df_olahraga_harian.columns if "kalori" in col.lower() or "kcal" in col.lower()), None)
      col_status = next((col for col in df_olahraga_harian.columns if "olahraga" in col.lower() or "status" in col.lower()), None)

      c1, c2 = st.columns(2)
      if col_langkah:
        df_olahraga_harian[col_langkah] = pd.to_numeric(df_olahraga_harian[col_langkah], errors="coerce").fillna(0)
        total_langkah = int(df_olahraga_harian[col_langkah].max())
        with c1:
          st.metric(label="👟 Total Langkah", value=f"{total_langkah:,} steps")

      if col_kalori:
        df_olahraga_harian[col_kalori] = pd.to_numeric(df_olahraga_harian[col_kalori], errors="coerce").fillna(0)
        total_kal = int(df_olahraga_harian[col_kalori].max())
        with c2:
          st.metric(label="🔥 Kalori Smartwatch", value=f"{total_kal} kcal")

      if col_status:
        status_terakhir = df_olahraga_harian[col_status].dropna().iloc[-1] if not df_olahraga_harian[col_status].dropna().empty else "-"
        st.info(f"🏋️‍♂️ **Status Olahraga Hari Ini:** {status_terakhir}")
    else:
      st.caption("ℹ️ Belum ada data olahraga/jam tangan yang dicatat pada tanggal ini (hari istirahat).")

  st.markdown("---")

  # --- BAGIAN 2: JURNAL MAKAN HARIAN ---
  if not df_makan.empty and "Tanggal_Saja" in df_makan.columns:
    df_makan_harian = df_makan[df_makan["Tanggal_Saja"] == pilih_tanggal]
    
    if not df_makan_harian.empty:
      st.markdown("#### 🍽️ Catatan Jurnal Makanan")
      st.dataframe(
          df_makan_harian.drop(columns=["Tanggal_Saja"], errors="ignore"),
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.caption("ℹ️ Belum ada catatan makan yang dimasukkan pada tanggal ini.")

else:
  st.warning(
      "Belum ada data masuk di Google Sheets (makan maupun olahraga), atau pastikan status sharing"
      " file sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )
