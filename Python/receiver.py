from flask import Flask, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ← Your ESP32 IP (shown in Serial Monitor after flashing)
ESP32_IP = "10.55.42.76"   # NO http:// here — we add it below
SAVE_FOLDER = "captured_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/trigger')
def trigger():
    try:
        url = f"http://{ESP32_IP}/capture"   # http:// added here
        print(f"Fetching image from: {url}")

        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{timestamp}.jpg"
            filepath = os.path.join(SAVE_FOLDER, filename)

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"✅ Image saved: {filepath}")
            return "Success", 200
        else:
            print(f"❌ ESP32 returned status: {response.status_code}")
            return "Capture Failed", 500

    except Exception as e:
        print(f"❌ Error: {e}")
        return str(e), 500

if __name__ == '__main__':
    print("="*40)
    print("Flask server running on port 5000")
    print("Waiting for ESP32 trigger...")
    print("="*40)
    app.run(host='0.0.0.0', port=5000, debug=False)
