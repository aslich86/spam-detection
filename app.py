import streamlit as st
import pandas as pd
import plotly.express as px
import pickle

# Konfigurasi Halaman ala Cybersecurity
st.set_page_config(page_title="Email Threat Scanner", page_icon="🛡️", layout="wide")

@st.cache_resource
def load_model():
    try:
        with open('email_spam_model.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

data_pack = load_model()

if data_pack is None:
    st.error("⚠️ File 'email_spam_model.pkl' tidak ditemukan di folder ini!")
    st.stop()

model_spam = data_pack['model']
df = data_pack['data_sampel']

# --- HEADER ---
st.title("🛡️ Email Threat Intelligence Scanner")
st.markdown("Sistem deteksi dini ancaman *spam* dan *social engineering* menggunakan Machine Learning.")
st.markdown("---")

# --- FITUR UTAMA: LIVE SCANNER ---
st.subheader("🔎 Live Email Scanner")
st.info("Paste teks email yang mencurigakan untuk diinvestigasi oleh AI.")

email_input = st.text_area("Isi Teks Email:", height=150, 
                           placeholder="Contoh: CONGRATULATIONS! You have won $1,000,000. Click the link below to claim your prize...")

if st.button("Scan Ancaman", type="primary"):
    if email_input:
        hasil = model_spam.predict([email_input])[0]
        probabilitas = model_spam.predict_proba([email_input])[0]
        prob_max = max(probabilitas) * 100
        
        # Asumsi output dari Kaggle adalah 'spam' atau '1'
        if str(hasil).lower() in ['spam', '1']:
            st.error(f"🚨 **ANCAMAN TERDETEKSI: SPAM / PHISHING** (Tingkat Keyakinan: {prob_max:.1f}%)")
            st.markdown("⚠️ **Rekomendasi Keamanan:** Abaikan pesan ini. Jangan klik tautan atau mengunduh lampiran apapun.")
        else:
            st.success(f"✅ **STATUS AMAN: BUKAN SPAM** (Tingkat Keyakinan: {prob_max:.1f}%)")
            st.markdown("ℹ️ Tidak ditemukan pola bahasa manipulatif pada email ini.")
    else:
        st.warning("Mohon masukkan teks email terlebih dahulu untuk dipindai.")

st.markdown("---")

# --- ANALITIK DATABASE ---
st.subheader("📊 Analitik Database Ancaman")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Distribusi Kategori Email**")
    # Mengambil kolom label otomatis (kolom ke-2)
    kolom_label = df.columns[1]
    df_dist = df[kolom_label].value_counts().reset_index()
    df_dist.columns = ['Kategori', 'Jumlah']
    
    fig = px.pie(df_dist, values='Jumlah', names='Kategori', hole=0.4,
                 color_discrete_sequence=['#ef4444', '#10b981'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Log Sampel Dataset**")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)