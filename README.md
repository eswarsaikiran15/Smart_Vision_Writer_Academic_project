# 🎯 Smart Vision Writer

> **An IoT-Based Real-Time Image Captioning and Scene Understanding System using AI/ML**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Arduino](https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white)](https://arduino.cc)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 📌 Project Overview

**Smart Vision Writer** is a fully offline IoT-AI integrated surveillance system that combines the **ESP32-CAM** microcontroller with two state-of-the-art transformer-based vision-language models — **BLIP** and **CLIP** — to automatically generate natural language descriptions and zero-shot scene classifications from real-world images.

A **PIR motion sensor (HC-SR501)** detects human presence and triggers the ESP32-CAM to capture a JPEG image. The image is transmitted via **HTTP over a local Wi-Fi network** to a Python Flask server, which runs the complete AI inference pipeline — entirely **offline, without any cloud dependency**.

Results are displayed on an interactive **Streamlit dashboard** with configurable scenario label sets.

```
PIR Sensor → ESP32-CAM → Wi-Fi (HTTP) → Flask Server → BLIP + CLIP → Streamlit Dashboard
```

> **Final Year B.Tech Project** — Department of CSE – Internet of Things  
> Aditya College of Engineering & Technology (A), Surampalem  
> Regulation R20 | IV Year II Semester | 2025–26

---

## ✨ Key Features

- 🔴 **PIR-triggered capture** — HC-SR501 motion sensor detects human presence and auto-triggers the ESP32-CAM
- 📸 **Real-time image capture** — ESP32-CAM streams JPEG images over local Wi-Fi via HTTP
- 📝 **Natural language captioning** — BLIP generates human-readable scene descriptions
- 🏷️ **Zero-shot classification** — CLIP classifies scenes into custom label sets without retraining
- 📡 **Fully offline** — runs on local LAN, no internet or cloud required
- 🎛️ **8 built-in scenarios** — Classroom, Food, Sky, Fall Detection, Plant Health, Traffic Signs, Waste, Activity
- 🖥️ **Streamlit dashboard** — live results with confidence scores, progress bars, and image gallery
- 🔒 **Privacy-first** — all data stays on your local network, nothing leaves the device
- ⚡ **Dual-core architecture** — PIR sensor on Core 0, Camera Server on Core 1 (no interference)
- 💰 **Low cost** — total hardware under ₹800

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SMART VISION WRITER PIPELINE                         │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │  PIR Sensor  │    │  ESP32-CAM   │    │   Local Wi-Fi Network    │  │
│  │  HC-SR501    │───▶│  OV2640      │───▶│   HTTP over LAN          │  │
│  │  GPIO 14     │    │  QVGA JPEG   │    │   No internet needed     │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
│                                                         │               │
│                                                         ▼               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               Flask Server  (receiver.py — port 5000)            │  │
│  │         Receives trigger → Fetches /capture → Saves JPEG         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                        │                        │                       │
│                        ▼                        ▼                       │
│           ┌────────────────────┐   ┌────────────────────────┐          │
│           │    BLIP Model      │   │      CLIP Model         │          │
│           │  Caption Gen.      │   │  Zero-Shot Classify     │          │
│           │  (Salesforce)      │   │  (OpenAI)               │          │
│           └────────────────────┘   └────────────────────────┘          │
│                        │                        │                       │
│                        └───────────┬────────────┘                       │
│                                    ▼                                    │
│           ┌──────────────────────────────────────────────┐             │
│           │       Streamlit Dashboard  (app2.py)          │             │
│           │  Caption + CLIP Scores + Gallery + Scenarios  │             │
│           └──────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Hardware Requirements

| Component | Specification | Purpose | Cost (approx.) |
|-----------|--------------|---------|----------------|
| ESP32-CAM (AI Thinker) | OV2640 2MP, 4MB PSRAM, Wi-Fi | Image capture + HTTP server | ₹500–600 |
| PIR Sensor HC-SR501 | 3.3V, 7m range, adjustable delay | Human motion detection | ₹50–70 |
| MB102 Breadboard Power Supply | 5V/3.3V output | Powers entire circuit | ₹80–120 |
| Breadboard + Jumper Wires | Standard 830-point | Connections | ₹50–80 |
| **Total** | | | **< ₹800** |

### 📌 Wiring Connections

```
MB102 Power Module  →  5V Rail (+) and GND Rail (-)

ESP32-CAM:
  5V pin      →  Red rail (+)
  GND pin     →  Blue rail (-)

PIR HC-SR501:
  VCC         →  Red rail (+)  [5V]
  GND         →  Blue rail (-)
  OUT         →  ESP32 GPIO 14  [no resistor needed — native 3.3V]
```

> **Why PIR instead of HC-SR04 Ultrasonic?**  
> HC-SR04 outputs 5V on ECHO pin which exceeds ESP32 GPIO's 3.3V maximum, causing signal corruption. HC-SR501 PIR natively outputs 3.3V and uses simple `digitalRead()` — immune to FreeRTOS timing interference.

---

## 💻 Software Requirements

- Python 3.8 or higher
- Arduino IDE 2.x with ESP32 board support
- ~4 GB disk space for AI models

### Python Libraries

```bash
pip install streamlit flask requests pillow torch transformers opencv-python numpy
```

---

## 📁 Project Structure

```
SmartVisionWriter/
│
├── CameraWebServer.ino        # ESP32-CAM Arduino firmware
├── board_config.h             # Camera model selection (AI Thinker)
├── camera_pins.h              # GPIO pin definitions
│
├── receiver.py                # Flask server — receives PIR trigger, saves JPEG
├── ml_pipeline.py             # AI pipeline — BLIP caption + CLIP classification
├── app2.py                    # Streamlit dashboard
├── test_clip_blip.py          # Offline model validation script
│
├── captured_images/           # Auto-created — stores captured JPEGs
│
└── README.md
```

---

## 🚀 Setup & Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SmartVisionWriter.git
cd SmartVisionWriter
```

### Step 2 — Install Python dependencies

```bash
pip install streamlit flask requests pillow torch transformers opencv-python numpy
```

### Step 3 — Download AI models (one time, needs internet)

Run this once to cache models locally for offline use:

```python
# Run this script once with internet connection
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import CLIPProcessor, CLIPModel

print("Downloading BLIP...")
BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

print("Downloading CLIP...")
CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

print("Done! Models cached for offline use.")
```

### Step 4 — Flash ESP32-CAM firmware

1. Open `CameraWebServer.ino` in Arduino IDE
2. Set your WiFi credentials:
   ```cpp
   const char* ssid     = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Set your laptop's IP address:
   ```cpp
   // Find this with: ipconfig (Windows) or ifconfig (Linux/Mac)
   const char* python_server_url = "http://YOUR_LAPTOP_IP:5000/trigger";
   ```
4. Select board: **AI Thinker ESP32-CAM**
5. Upload the sketch
6. Open Serial Monitor at **115200 baud** to get the ESP32-CAM's IP address

### Step 5 — Update server IP in app2.py

Open `app2.py` and `receiver.py` and set your ESP32-CAM's IP (from Serial Monitor):

```python
ESP32_IP = "192.168.x.x"  # Replace with your ESP32-CAM IP
```

---

## ▶️ Running the Project

Open **two separate terminals** in your project folder:

**Terminal 1 — Start Flask server:**
```bash
python receiver.py
```
Expected output:
```
Flask server running on port 5000
Waiting for ESP32 trigger...
```

**Terminal 2 — Start Streamlit dashboard:**
```bash
streamlit run app2.py
```
Browser opens at: `http://localhost:8501`

---

## 🎮 Using the Dashboard

1. **Select a scenario** from the sidebar (e.g., Classroom Analyzer, Food Recognition)
2. **Choose input method:**
   - 📷 **ESP32 Capture tab** — click "Capture Now" to trigger via PIR/manual
   - 📁 **Upload Image tab** — upload any image to test offline (no ESP32 needed)
3. **View results:**
   - BLIP-generated natural language caption
   - CLIP top-5 predictions with confidence scores and progress bars
4. **Gallery** — last 12 captured images shown at the bottom

### Built-in Scenarios

| Scenario | Labels |
|----------|--------|
| General Caption | person, outdoor, indoor, food, vehicle, nature |
| Classroom Analyzer | boys in classroom, girls in classroom, teacher teaching, empty classroom |
| Sky Condition | clear sky, sunset, night sky, cloudy sky, rainy sky |
| Food Recognition | south indian thali, north indian food, pizza, burger, idli vada |
| Elderly Fall Detection | person standing, person sitting, person falling, person lying down |
| Plant Health Monitor | healthy plant, diseased plant, dry plant, overwatered plant |
| Traffic Sign Detection | stop sign, speed limit sign, no entry sign, pedestrian crossing |
| Waste Classification | plastic waste, food waste, metal waste, paper waste |

---

## 🤖 AI Pipeline Details

### BLIP — Image Captioning
- **Model:** `Salesforce/blip-image-captioning-base`
- **Architecture:** Vision Transformer (ViT-B/16) encoder + 12-layer transformer language decoder with cross-attention
- **Method:** Beam search (num_beams=5) with repetition penalty 1.3
- **Output:** Natural language sentence describing the scene

### CLIP — Zero-Shot Classification
- **Model:** `openai/clip-vit-base-patch32`
- **Architecture:** Dual-encoder — Vision Transformer + Text Transformer
- **Method:** Cosine similarity in shared 512-dimensional embedding space
- **Formula:** `P(label | image) = softmax(cos(image_emb, text_emb) / τ)`
- **Output:** Top-5 labels with confidence scores

### Offline Mode
Both models run from local HuggingFace cache:
```python
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
```

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Classification Accuracy | **90%** (9/10 test images) |
| BLIP Caption Accuracy | **100%** (10/10 contextually correct) |
| Average Inference Time | **4.2 seconds** (CPU, no GPU) |
| BLIP inference time | ~2.8 seconds |
| CLIP inference time | ~1.4 seconds |
| HTTP transfer time (LAN) | < 0.3 seconds |
| Total hardware cost | **< ₹800** |

### Sample Results

| Image | BLIP Caption | Top CLIP Label | Confidence |
|-------|-------------|----------------|------------|
| Classroom | A group of students sitting at desks in a classroom | boys in classroom | 0.78 |
| Food plate | A plate of south indian food on a wooden table | south indian thali | 0.81 |
| Green plant | A green plant in a pot on a white surface | healthy plant | 0.73 |
| Blue sky | A blue sky with white clouds on a sunny day | clear blue sky | 0.85 |
| Empty room | An empty room with chairs arranged in rows | empty classroom | 0.76 |

---

## 🔧 Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` | Library not installed | `pip install transformers torch streamlit flask` |
| `OSError: Can't load model` | Models not downloaded | Run download script with internet first |
| `Connection refused` on ESP32 | Wrong IP or Flask not running | Check `ipconfig`, start `receiver.py` first |
| PIR triggers constantly | Sensor warming up | Wait 30 seconds after power on |
| `Distance: 0 cm` in serial | (old ultrasonic code) | Switch to PIR sensor |
| Camera init failed | Wiring issue | Check ESP32 power supply (needs stable 5V) |
| Streamlit blank page | Port conflict | Try `streamlit run app2.py --server.port 8502` |

---

## 📐 Technical Deep Dive

### Why PIR Instead of HC-SR04?

| Specification | HC-SR04 Ultrasonic | HC-SR501 PIR |
|--------------|-------------------|--------------|
| Output voltage | 5V on ECHO (unsafe!) | 3.3V native |
| Resistors needed | Yes (voltage divider) | None |
| FreeRTOS compatibility | ❌ pulseIn() breaks | ✅ digitalRead() |
| Detection range | 4m (distance) | 7m (motion) |
| Power | 15 mA | 60 µA |

### Why Edge Server, Not On-Device AI?

BLIP and CLIP have hundreds of millions of parameters. ESP32-CAM has only 4MB PSRAM. On-device inference is physically impossible. The Edge Server pattern keeps hardware cost under ₹800 while achieving 90% accuracy — same architecture used by AWS Greengrass and Azure IoT Edge.

### Dual-Core Design

```cpp
// PIR task pinned to Core 0
xTaskCreatePinnedToCore(pirTask, "PIR", 4096, NULL, 2, NULL, 0);

// Camera server runs on Core 1 (default)
startCameraServer();  // internally uses Core 1
```

This completely eliminates interference between sensor polling and camera streaming.

---

## 🔮 Future Scope

- [ ] **Real-time video captioning** using lightweight distilled transformer models
- [ ] **Voice alerts** — text-to-speech output using gTTS or pyttsx3
- [ ] **Edge deployment** — INT8 quantization for Raspberry Pi (< 1s inference)
- [ ] **Multi-camera support** — multiple ESP32-CAM nodes on one central server
- [ ] **Face recognition** for access control applications
- [ ] **Custom model fine-tuning** on domain-specific datasets

---

## 👥 Team

| Name | Roll Number |
|------|-------------|
| Kamparapu Eswar Sai Kiran | 22MH1A4924 |
| Kancharla Anand Kumar | 22MH1A4925 |
| Siribolu Bala Subhramanyam | 23MH5A4907 |
| Yandrapu Akash | 22MH1A4963 |

**Project Guide:** Mrs. Talluri Sushma, M.Tech (Ph.D)  
Assistant Professor, Department of CSE – IoT & Data Science  
Aditya College of Engineering & Technology (A), Surampalem

---

## 📚 References

1. Li, J., Li, D., Xiong, C., & Hoi, S. (2022). **BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation.** ICML 2022.

2. Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., et al. (2021). **Learning Transferable Visual Models From Natural Language Supervision (CLIP).** ICML 2021.

3. Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). **Attention Is All You Need.** NeurIPS 2017.

4. Dosovitskiy, A., et al. (2021). **An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale (ViT).** ICLR 2021.

5. Patil, S. K., Desai, A. R., & Kulkarni, M. V. (2023). **Low-Cost IoT-Based Surveillance System Using ESP32-CAM.** IJETAE, Vol. 13, No. 4.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Salesforce Research](https://github.com/salesforce/BLIP) for the BLIP model
- [OpenAI](https://github.com/openai/CLIP) for the CLIP model
- [HuggingFace](https://huggingface.co) for the Transformers library
- Department of CSE-IoT, ACET(A) for laboratory facilities and guidance

---

<div align="center">

**Made with ❤️ at Aditya College of Engineering & Technology (A)**

*Smart Vision Writer — Seeing the World, Describing it in Words*

</div>
