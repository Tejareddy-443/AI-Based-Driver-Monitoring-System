import cv2

from phone_detection import PhoneDetector


print("==========================================")
print("      MOBILE PHONE DETECTION TEST")
print("==========================================")

detector = PhoneDetector()

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

print("Webcam started.")
print("Show a mobile phone to the camera.")
print("Press Q to exit.")

while True:

    success, frame = camera.read()

    if not success:
        print("ERROR: Could not read frame.")
        break

    # Detect phone
    phone_detected, frame = detector.detect(frame)

    # Display status
    if phone_detected:
        status = "PHONE DETECTED"
        status_color = (0, 0, 255)
    else:
        status = "NO PHONE"
        status_color = (0, 255, 0)

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        status_color,
        2
    )

    cv2.imshow("Mobile Phone Detection", frame)

    # Exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Phone detection test completed.")