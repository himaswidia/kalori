from datetime import datetime, date
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Daily Habit & Health Tracker", page_icon="🎯", layout="centered"
)

st.title("🎯 Daily Habit & Health Tracker")
st.write("Pantau konsistensi kebiasaan, makanan, dan aktivitas fisikmu!")

# Tombol Google Form & Google Sheets
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
  FORM_MAKAN_URL = "https://docs.google.com/forms/d/e/1FAIpQLSc1XenVBhorc_SSVog7dnJl-jV0R2vztFMuzutG3PmaoePAlg/viewform"
  st.link_button("📝 Input Jurnal Makan", FORM_MAKAN_URL, use_container_width=True)
with col_f2:
  FORM_OLAHRAGA_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeE-AB9MLf1-Kf3puAKa0kUra7X4oAE6VY8SYvW4v6nO1bEcQ/viewform"
  st.link_button("🏋️ Input Olahraga", FORM_OLAHRAGA_URL, use_container_width=True)
with col_f3:
  SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1uvO_4PJnCkCOUJEl4DpPnabBW6AtjBEnho2ypiRH-GE/edit?usp=sharing"
  st.link_button("✏️ Edit Spreadsheet", SHEET_EDIT_URL, use_container_width=True)

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

# Membersihkan spasi kolom dan menstandarisasi tanggal
for df in [df_makan, df_olahraga]:
  if not df.empty:
    df.columns = df.columns.str.strip()
    kolom_tgl = next((col for col in df.columns if "tanggal" in col.lower() or "date" in col.lower()), None)
    if kolom_tgl:
      df["Tanggal_Saja"] = pd.to_datetime(df[kolom_tgl], errors="coerce").dt.strftime("%Y-%m-%d")
      df["Bulan_Tahun"] = pd.to_datetime(df[kolom_tgl], errors="coerce").dt.strftime("%Y-%m")

# Mendapatkan daftar tanggal unik
semua_tanggal = set()
if not df_makan.empty and "Tanggal_Saja" in df_makan.columns:
  semua_tanggal.update(df_makan["Tanggal_Saja"].dropna().unique())
if not df_olahraga.empty and "Tanggal_Saja" in df_olahraga.columns:
  semua_tanggal.update(df_olahraga["Tanggal_Saja"].dropna().unique())

if semua_tanggal:
  # Pilih Mode Laporan (Harian atau Bulanan)
  mode_laporan = st.radio("📊 Pilih Jenis Laporan:", ["Laporan Harian", "Laporan Bulanan"], horizontal=True)
  st.markdown("---")

  if mode_laporan == "Laporan Harian":
    st.subheader("📅 Pilih Tanggal Laporan")
    daftar_date_obj = sorted([datetime.strptime(t.strip(), "%Y-%m-%d").date() for t in semua_tanggal if isinstance(t, str) and len(t) == 10], reverse=True)
    
    if daftar_date_obj:
      pilih_tanggal_obj = st.date_input(
          "Pilih tanggal pada kalender:",
          value=daftar_date_obj[0],
          min_value=min(daftar_date_obj),
          max_value=max(daftar_date_obj)
      )
      pilih_tanggal = pilih_tanggal_obj.strftime("%Y-%m-%d")

      st.markdown(f"### 📋 Ringkasan Tanggal: {pilih_tanggal}")

      # Bagian Olahraga Harian
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
          st.caption("ℹ️ Belum ada data olahraga/jam tangan pada tanggal ini (hari istirahat).")

      st.markdown("---")

      # Bagian Makan Harian
      if not df_makan.empty and "Tanggal_Saja" in df_makan.columns:
        df_makan_harian = df_makan[df_makan["Tanggal_Saja"] == pilih_tanggal]
        if not df_makan_harian.empty:
          st.markdown("#### 🍽️ Catatan Jurnal Makanan")
          st.dataframe(
              df_makan_harian.drop(columns=["Tanggal_Saja", "Bulan_Tahun"], errors="ignore"),
              use_container_width=True,
              hide_index=True,
          )
        else:
          st.caption("ℹ️ Belum ada catatan makan pada tanggal ini.")

  else:  # --- LAPORAN BULANAN ---
    st.subheader("📈 Rekap Laporan Bulanan")
    
    # Mengambil daftar bulan unik dari data
    semua_bulan = set()
    if not df_makan.empty and "Bulan_Tahun" in df_makan.columns:
      semua_bulan.update(df_makan["Bulan_Tahun"].dropna().unique())
    if not df_olahraga.empty and "Bulan_Tahun" in df_olahraga.columns:
      semua_bulan.update(df_olahraga["Bulan_Tahun"].dropna().unique())
    
    daftar_bulan = sorted(list(semua_bulan), reverse=True)
    
    if daftar_bulan:
      pilih_bulan = st.selectbox("Pilih Bulan Laporan:", options=daftar_bulan)
      
      st.markdown(f"### 📊 Ringkasan Bulan: {pilih_bulan}")
      
      # Filter data berdasarkan bulan
      df_makan_bulan = df_makan[df_makan["Bulan_Tahun"] == pilih_bulan] if not df_makan.empty else pd.DataFrame()
      df_olahraga_bulan = df_olahraga[df_olahraga["Bulan_Tahun"] == pilih_bulan] if not df_olahraga.empty else pd.DataFrame()
      
      # Metrik Bulanan dari Smartwatch
      if not df_olahraga_bulan.empty:
        col_langkah = next((col for col in df_olahraga_bulan.columns if "langkah" in col.lower() or "step" in col.lower()), None)
        col_kalori = next((col for col in df_olahraga_bulan.columns if "kalori" in col.lower() or "kcal" in col.lower()), None)
        col_status = next((col for col in df_olahraga_bulan.columns if "olahraga" in col.lower() or "status" in col.lower()), None)

        # Menghitung rata-rata harian langkah dan total sesi olahraga
        bm1, bm2, bm3 = st.columns(3)
        if col_langkah:
          df_olahraga_bulan[col_langkah] = pd.to_numeric(df_olahraga_bulan[col_langkah], errors="coerce").fillna(0)
          rata_langkah = int(df_olahraga_bulan.groupby("Tanggal_Saja")[col_langkah].max().mean())
          with bm1:
            st.metric(label="👟 Rata-rata Langkah/Hari", value=f"{rata_langkah:,} steps")

        if col_kalori:
          df_olahraga_bulan[col_kalori] = pd.to_numeric(df_olahraga_bulan[col_kalori], errors="coerce").fillna(0)
          total_kal_bulan = int(df_olahraga_bulan.groupby("Tanggal_Saja")[col_kalori].max().sum())
          with bm2:
            st.metric(label="🔥 Total Kalori Bakar Jam", value=f"{total_kal_bulan:,} kcal")

        if col_status:
          jumlah_gym = df_olahraga_bulan[df_olahraga_bulan[col_status].notna() & (df_olahraga_bulan[col_status] != "-")].shape[0]
          with bm3:
            st.metric(label="🏋️‍♂️ Total Sesi Olahraga", value=f"{jumlah_gym} sesi")

      st.markdown("---")
      
      # Tabel Riwayat Olahraga Bulanan
      if not df_olahraga_bulan.empty:
        st.markdown("#### 🏃‍♂️ Log Aktivitas Olahraga Bulan Ini")
        st.dataframe(
            df_olahraga_bulan.drop(columns=["Tanggal_Saja", "Bulan_Tahun"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )

      # Tabel Jurnal Makanan Bulanan
      if not df_makan_bulan.empty:
        st.markdown("#### 🍽️ Log Jurnal Makanan Bulan Ini")
        st.dataframe(
            df_makan_bulan.drop(columns=["Tanggal_Saja", "Bulan_Tahun"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )
    else:
      st.info("Belum ada data bulan yang tercatat.")

else:
  st.warning(
      "Belum ada data masuk di Google Sheets (makan maupun olahraga), atau pastikan status sharing"
      " file sudah diatur ke 'Siapa saja yang memiliki link dapat melihat'."
  )
