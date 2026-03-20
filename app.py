import streamlit as st
import pandas as pd
import requests
import time

# --- CONFIGURATION ---
# Put your Blynk Auth Token here!
BLYNK_TOKEN = "YOUR_BLYNK_AUTH_TOKEN" 
# This URL fetches the latest value from Virtual Pin 1 (V1)
BLYNK_URL = f"https://blynk.cloud/external/api/get?token={'ERBzDf_UFfvaaqmUjbiArUBRd8wUVV5W'}&v1"

st.set_page_config(page_title="AI Health Wearable", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫀 Live Health AI Analytics")
st.subheader("Mobile Cloud Gateway Architecture")

# Initialize Chart Data
if "heart_data" not in st.session_state:
    st.session_state.heart_data = pd.DataFrame(columns=["Time", "BPM"])

# --- FETCH DATA FROM BLYNK CLOUD ---
def get_live_bpm():
    try:
        response = requests.get(BLYNK_URL, timeout=3)
        if response.status_code == 200:
            # Blynk returns data like ["75"], so we strip the brackets and convert to int
            clean_value = response.text.replace('[', '').replace(']', '').replace('"', '')
            return int(float(clean_value))
    except Exception as e:
        return None
    return 0

# --- DASHBOARD LOGIC ---
current_bpm = get_live_bpm()

if current_bpm and current_bpm > 40:
    now = time.strftime("%H:%M:%S")
    new_row = pd.DataFrame({"Time": [now], "BPM": [current_bpm]})
    st.session_state.heart_data = pd.concat([st.session_state.heart_data, new_row], ignore_index=True).tail(20)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Live Heart Rate (via Cloud)", value=f"{current_bpm} BPM")
    with col2:
        stress = "🔥 High Stress" if current_bpm > 95 else "🍀 Normal"
        st.metric(label="AI Analysis", value=stress)

    st.line_chart(st.session_state.heart_data.set_index("Time"))
    
    # Auto-refresh the dashboard every 2 seconds
    time.sleep(2)
    st.rerun()
else:
    st.info("☁️ Waiting for data from the Mobile Gateway... Make sure your phone is sending data to Blynk.")
    # Slower refresh when idle to save resources
    time.sleep(3)
    st.rerun()

st.divider()
st.caption("Architecture: nRF52840 ➔ Mobile Phone Gateway ➔ Blynk IoT Cloud ➔ Streamlit Dashboard")