import cv2

# The URL of your ESP32-CAM stream
# Usually, the 'CameraWebServer' example uses port 81 for the stream
stream_url = "http://10.123.52.76:81/stream"

def main():
    # Create a VideoCapture object
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        print("Error: Could not open video stream. Check the IP and Port.")
        return

    print("Connected to ESP32-CAM stream. Press 'q' to exit.")

    while True:
        # Read a frame from the stream
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to receive frame. Stream might have dropped.")
            break

        # Display the frame in a window
        cv2.imshow("ESP32-CAM Feed", frame)

        # Press 'q' to quit the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
