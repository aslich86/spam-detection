import streamlit as st
import pandas as pd
import plotly.express as px
import pickle

st.set_page_config(page_title="Multi-Threat Intelligence Scanner", page_icon="🛡️", layout="wide")

# Fungsi Loading Model yang Fleksibel
@st.cache_resource
def load_all_models():
    models = {}
    try:
        with open('email_spam_model.pkl', 'rb') as f:
            models['en'] = pickle.load(f)
    except FileNotFoundError:
        models['en'] = None
        
    try:
        with open('indo_sms_model.pkl', 'rb') as f:
            models['id'] = pickle.load(f)
    except FileNotFoundError:
        models['id'] = None
    return models

all_models = load_all_models()

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("Settings")
    mode = st.radio(
        "Pilih Mode Detektor:",
        ["🇬🇧 English Email", "🇮🇩 Indonesian SMS"],
        help="Pilih dataset dan bahasa yang sesuai untuk hasil akurasi maksimal."
    )
    st.markdown("---")
    st.caption("AIdvisory Ecosystem - Cybersecurity Module")

# Memilih data berdasarkan mode
if "English" in mode:
    target_data = all_models['en']
    lang_code = 'en'
    label_spam = "SPAM / PHISHING"
else:
    target_data = all_models['id']
    lang_code = 'id'
    label_spam = "PENIPUAN / SPAM"

# Proteksi jika file pkl belum ada
if target_data is None:
    st.error(f"⚠️ Model untuk {mode} belum diunggah ke folder project!")
    st.stop()

model_active = target_data['model']
df_sample = target_data['data_sampel']

# --- HEADER ---
st.title(f"🛡️ {mode} Threat Scanner")
st.markdown(f"Sistem investigasi teks otomatis menggunakan *Machine Learning* untuk mendeteksi pola manipulasi bahasa.")
st.markdown("---")

# --- FITUR UTAMA: LIVE SCANNER ---
st.subheader("🔎 Forensic Scanner")
input_placeholder = "Paste email content here..." if lang_code == 'en' else "Contoh: Selamat! Anda mendptkan hadiah 100jt dr Shopee..."
email_input = st.text_area("Input Teks untuk Diperiksa:", height=150, placeholder=input_placeholder)

if st.button("Scan Ancaman", type="primary"):
    if email_input:
        hasil = model_active.predict([email_input])[0]
        probabilitas = model_active.predict_proba([email_input])[0]
        prob_max = max(probabilitas) * 100
        
        # Logika deteksi berdasarkan label (mendukung string 'spam' atau angka 1)
        is_spam = str(hasil).lower() in ['spam', '1', 'penipuan']
        
        if is_spam:
            st.error(f"🚨 **ANCAMAN TERDETEKSI: {label_spam}** (Keyakinan: {prob_max:.1f}%)")
            st.warning("🚨 **REKOMENDASI:** Jangan klik link, jangan transfer uang, dan jangan berikan data pribadi!")
        else:
            st.success(f"✅ **STATUS AMAN: NORMAL** (Keyakinan: {prob_max:.1f}%)")
            st.info("Pesan ini tidak menunjukkan pola manipulatif atau ancaman siber yang umum.")
    else:
        st.warning("Masukkan teks terlebih dahulu!")

st.markdown("---")

# --- ANALITIK ---
st.subheader("📊 Intelligence Data Insights")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Komposisi Dataset**")
    kolom_label = df_sample.columns[1]
    df_dist = df_sample[kolom_label].value_counts().reset_index()
    df_dist.columns = ['Status', 'Total']
    
    fig = px.pie(df_dist, values='Total', names='Status', hole=0.5,
                 color_discrete_sequence=['#ef4444', '#10b981'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"**Riwayat Sampel {mode}**")
    st.dataframe(df_sample.head(20), use_container_width=True, hide_index=True)
