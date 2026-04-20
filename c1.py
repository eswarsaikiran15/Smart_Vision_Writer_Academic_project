import requests
import cv2
import numpy as np

# Use the IP address you confirmed
IP_ADDRESS = "10.123.52.76"
capture_url = f"http://{IP_ADDRESS}/capture"

def save_snapshot(filename="snapshot.jpg"):
    try:
        # Send request to the ESP32-CAM to take a photo
        print("Taking snapshot...")
        response = requests.get(capture_url, timeout=5)

        if response.status_code == 200:
            # Method 1: Save directly to a file
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Success! Image saved as {filename}")

            # Method 2: Convert to OpenCV format (if you want to process it with ML)
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            # Show the captured image
            cv2.imshow("Captured Snapshot", img)
            cv2.waitKey(2000) # Show for 2 seconds
            cv2.destroyAllWindows()
            
            return img
        else:
            print(f"Failed to get image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_snapshot("my_project_image.jpg")