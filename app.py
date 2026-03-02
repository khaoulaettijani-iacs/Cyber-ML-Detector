#Dependencies
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

#Page configuration
st.set_page_config(
    page_title="Brute-force Attack Detection",
    page_icon="🛡️",
    layout="centered",
)

# CUSTOM CSS —  terminal aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700&display=swap');

html, body, [class*="css"] {
    background-color: #0d0f14;
    color: #c9d1d9;
    font-family: 'Share Tech Mono', monospace;
}

h1, h2, h3 { font-family: 'Orbitron', monospace; }

.stButton>button {
    background: linear-gradient(135deg, #00ff9f22, #00bfff22);
    border: 1px solid #00ff9f88;
    color: #00ff9f;
    font-family: 'Orbitron', monospace;
    font-size: 14px;
    letter-spacing: 2px;
    padding: 12px 32px;
    border-radius: 4px;
    transition: all 0.3s;
    width: 100%;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #00ff9f44, #00bfff44);
    border-color: #00ff9f;
    box-shadow: 0 0 20px #00ff9f55;
}

.stSlider [data-baseweb="slider"] { color: #00ff9f; }

div[data-testid="stMetricValue"] { font-family: 'Orbitron', monospace; font-size: 2rem; }

.result-box {
    padding: 24px;
    border-radius: 8px;
    text-align: center;
    margin-top: 20px;
    font-family: 'Orbitron', monospace;
}
.result-normal {
    background: #00ff9f11;
    border: 2px solid #00ff9f;
    color: #00ff9f;
}
.result-attack {
    background: #ff004411;
    border: 2px solid #ff0044;
    color: #ff0044;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 10px #ff004444; }
    50%  { box-shadow: 0 0 30px #ff0044aa; }
    100% { box-shadow: 0 0 10px #ff004444; }
}
.label { font-size: 11px; color: #8b949e; letter-spacing: 2px; text-transform: uppercase; }
.value { font-size: 28px; font-weight: bold; margin: 8px 0; }
.subtitle { font-size: 13px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# Load the trained model
@st.cache_resource
def load_model():
    with open("model.pkl", "rb") as f:
        return pickle.load(f)

try:
    model = load_model()
    model_loaded = True
except FileNotFoundError:
    model_loaded = False

# Header
st.markdown("# 🛡️ BRUTE-FORCE DETECTOR")
st.markdown("**ML-powered login threat detection** · Random Forest Classifier")
st.divider()

if not model_loaded:
    st.error(" `model.pkl` not found! Run `python model.py` first to train and save the model.")
    st.stop()
# Input Panel
st.markdown("###  Input Login Activity Features")

col1, col2 = st.columns(2)

with col1:
    login_attempts = st.slider(
        "🔢 Login Attempts",
        min_value=1, max_value=50, value=5,
        help="Total number of login attempts from this session"
    )
    failed_attempts = st.slider(
        "❌ Failed Attempts",
        min_value=0, max_value=login_attempts, value=1,
        help="Number of failed login attempts"
    )

with col2:
    avg_time_between = st.slider(
        "⏱️ Avg Time Between Attempts (sec)",
        min_value=0.1, max_value=300.0, value=60.0, step=0.1,
        help="Average seconds between consecutive login attempts"
    )
    ip_change_frequency = st.slider(
        "🌐 IP Change Frequency (0–1)",
        min_value=0.0, max_value=1.0, value=0.05, step=0.01,
        help="How often the IP address changes (0 = never, 1 = every attempt)"
    )

# Auto-compute failed ratio
failed_ratio = failed_attempts / max(login_attempts, 1)
st.markdown(f"**📊 Computed Failed Ratio:** `{failed_ratio:.2%}`")

st.divider()

# PREDICT BUTTON
predict_clicked = st.button("⚡ ANALYZE THREAT")

if predict_clicked:
    features = np.array([[login_attempts, failed_attempts, failed_ratio,
                          avg_time_between, ip_change_frequency]])

    prediction  = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    attack_prob = probabilities[1] * 100
    normal_prob = probabilities[0] * 100

    st.divider()
    st.markdown("### 🔍 Detection Result")

    # ── Result box ──
    if prediction == 0:
        st.markdown(f"""
        <div class="result-box result-normal">
            <div class="label">threat status</div>
            <div class="value">✅ NORMAL ACTIVITY</div>
            <div class="subtitle">This session appears to be legitimate user behavior.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-box result-attack">
            <div class="label">threat status</div>
            <div class="value">🚨 BRUTE-FORCE ATTACK DETECTED</div>
            <div class="subtitle">Suspicious login pattern identified. Recommend blocking this session.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Probability metrics ──
    m1, m2, m3 = st.columns(3)
    m1.metric("Attack Risk %", f"{attack_prob:.1f}%")
    m2.metric("Normal Confidence", f"{normal_prob:.1f}%")
    m3.metric("Prediction", "🚨 Attack" if prediction == 1 else "✅ Normal")

    # ── Risk gauge bar ──
    st.markdown("**🎯 Attack Probability Gauge**")
    bar_color = "#ff0044" if attack_prob > 50 else "#00ff9f"
    st.progress(int(attack_prob), text=f"Attack Risk: {attack_prob:.1f}%")

    st.divider()

# FOOTER
st.divider()
st.markdown(
    "<p style='text-align:center; color:#444; font-size:11px;'>"
    "🛡️ Brute-Force Detector · Built with scikit-learn + Streamlit · Personal ML Project"
    "</p>",
    unsafe_allow_html=True
)
