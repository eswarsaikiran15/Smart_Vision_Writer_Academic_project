import streamlit as st
import requests
import os
import time
from PIL import Image
from io import BytesIO
from ml_pipeline import process_image 

SAVE_DIR = "captured_images"

# Ensure the directory exists
if not os.path.exists(SAVE_DIR): 
    os.makedirs(SAVE_DIR)

st.set_page_config(page_title="Smart Vision Pro", layout="wide")

# Initialize memory in session state (Removed duplicate block)
if "last_analyzed_file" not in st.session_state:
    st.session_state.last_analyzed_file = None

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("Configuration")
    esp_ip = st.text_input("ESP32-CAM IP", value="10.55.42.76")
    blip_tokens = st.slider("BLIP Description Detail", 20, 100, 50)
    auto_mode = st.checkbox("Auto-Analyze PIR Detection", value=True)
    
    if st.button("🗑️ Clear Gallery"):
        # Reset memory so the app doesn't look for a file we just deleted
        st.session_state.last_analyzed_file = None
        
        for f in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                # This skips files currently being read by Streamlit or Flask
                continue
        
        st.cache_data.clear() 
        st.success("Gallery Cleared!")
        st.rerun()

st.title("🚀 IoT + AI: Smart Vision Analyzer")

# --- SCENARIOS & LABELS ---
scenario = st.selectbox("Choose Use Case", [
    "General Caption Only", "Classroom Analyzer (Boys/Girls)", "Sky & Weather Describer",
    "Food Recognition (Mess/Thali)", "Person Activity Detector", "Elderly Fall Detection",
    "Plant Health Monitor", "Custom Labels"
])

label_map = {
    "Classroom Analyzer (Boys/Girls)": ["boys", "girls", "teacher", "empty classroom"],
    "Sky & Weather Describer": ["clear sky", "sunset", "clouds", "rainy"],
    "Food Recognition (Mess/Thali)": ["thali", "pizza", "burger", "idli vada"],
    "Person Activity Detector": ["waving", "victory", "sleeping", "reading"],
    "Elderly Fall Detection": ["standing", "sitting", "falling", "lying down"],
    "Plant Health Monitor": ["healthy", "diseased", "dry soil", "overwatered"]
}

labels = label_map.get(scenario, None)
if scenario == "Custom Labels":
    custom = st.text_input("Labels (comma separated)", "cat, dog")
    labels = [x.strip() for x in custom.split(",")]

# --- CORE ANALYSIS FUNCTION ---
def run_analysis(img_bytes, source_name):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    file_path = os.path.join(SAVE_DIR, f"{source_name}_{timestamp}.jpg")
    with open(file_path, "wb") as f:
        f.write(img_bytes)

    st.image(Image.open(BytesIO(img_bytes)), width='stretch')

    with st.spinner("Analyzing..."):
        results = process_image(file_path, labels, max_words=blip_tokens)
        
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 BLIP Caption")
        st.info(results['caption'])
    with c2:
        st.subheader("🔍 CLIP Predictions")
        for label, score in results['predictions']:
            st.write(f"**{label}**: `{score.item():.3f}`")
            st.progress(float(score.item()))

# --- AUTO-DETECTION LOGIC ---
st.subheader("🔔 Latest PIR Detection")
all_pir_images = sorted([f for f in os.listdir(SAVE_DIR) if f.startswith("img_")], reverse=True)

if all_pir_images:
    latest_file = all_pir_images[0]
    latest_img_path = os.path.join(SAVE_DIR, latest_file)
    
    # Check if this image has already been analyzed
    if latest_file != st.session_state.last_analyzed_file:
        st.session_state.last_analyzed_file = latest_file
        st.write(f"New motion detected: {latest_file}")
        with open(latest_img_path, "rb") as f:
            run_analysis(f.read(), "pir_auto")
    else:
        # Just display it; do not waste CPU running ML models again
        st.write(f"Monitoring... Last motion was: {latest_file}")
        st.image(Image.open(latest_img_path), width='stretch')
else:
    st.write("Waiting for PIR sensor signal...")

# --- INPUT TABS ---
st.markdown("---")
t1, t2 = st.tabs(["📸 Manual Capture", "📁 Upload Image"])
with t1:
    if st.button("Capture Now"):
        try:
            res = requests.get(f"http://{esp_ip}/capture", timeout=10)
            if res.status_code == 200: run_analysis(res.content, "esp32")
        except: st.error("ESP32 Offline.")
with t2:
    up = st.file_uploader("Upload", type=["jpg", "png"])
    if up: run_analysis(up.getvalue(), "pc")

# --- SAVED GALLERY ---
st.markdown("---")
st.subheader("📁 Saved Analysis Gallery")
# Filter listdir to only show actual files
images = sorted([f for f in os.listdir(SAVE_DIR) if os.path.isfile(os.path.join(SAVE_DIR, f))], reverse=True)
if images:
    cols = st.columns(4)
    for idx, img_file in enumerate(images[:12]):
        with cols[idx % 4]:
            st.image(os.path.join(SAVE_DIR, img_file), width='stretch', caption=img_file)
else:
    st.write("No images saved yet.")

# --- REFRESH LOOP ---
if auto_mode:
    time.sleep(10)
    st.rerun()
