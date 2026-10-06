import cv2
import mediapipe as mp
import math

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# --------------------------------------------------
# Calculate Euclidean distance between two points
# --------------------------------------------------

def distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


# --------------------------------------------------
# Calculate Eye Aspect Ratio
# --------------------------------------------------

def calculate_ear(eye_points):

    p1, p2, p3, p4, p5, p6 = eye_points

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)

    return ear


# --------------------------------------------------
# MediaPipe Face Landmarker
# --------------------------------------------------

base_options = python.BaseOptions(
    model_asset_path="face_landmarker.task"
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

face_landmarker = vision.FaceLandmarker.create_from_options(options)


# --------------------------------------------------
# Webcam
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()


frame_timestamp_ms = 0


# --------------------------------------------------
# MediaPipe eye landmark indexes
# --------------------------------------------------

LEFT_EYE = [33, 160, 158, 133, 153, 144]

RIGHT_EYE = [362, 385, 387, 263, 373, 380]


# --------------------------------------------------
# Main loop
# --------------------------------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Mirror image
    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert frame to MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Detect landmarks
    result = face_landmarker.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )

    frame_timestamp_ms += 33


    # --------------------------------------------------
    # If face detected
    # --------------------------------------------------

    if result.face_landmarks:

        landmarks = result.face_landmarks[0]


        # ----------------------------------------------
        # Convert eye landmarks to pixel coordinates
        # ----------------------------------------------

        left_eye_points = []

        for index in LEFT_EYE:

            landmark = landmarks[index]

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            left_eye_points.append((x, y))


        right_eye_points = []

        for index in RIGHT_EYE:

            landmark = landmarks[index]

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            right_eye_points.append((x, y))


        # ----------------------------------------------
        # Calculate EAR
        # ----------------------------------------------

        left_ear = calculate_ear(left_eye_points)

        right_ear = calculate_ear(right_eye_points)

        average_ear = (left_ear + right_ear) / 2.0


        # ----------------------------------------------
        # Determine eye state
        # ----------------------------------------------

        EAR_THRESHOLD = 0.22

        if left_ear < EAR_THRESHOLD:
             left_eye_state = "CLOSED"
        else:
            left_eye_state = "OPEN"

        if right_ear < EAR_THRESHOLD:
            right_eye_state = "CLOSED"
        else:
            right_eye_state = "OPEN"


        if left_eye_state == "OPEN" and right_eye_state == "OPEN":
            eye_state = "BOTH OPEN"

        elif left_eye_state == "CLOSED" and right_eye_state == "CLOSED":
            eye_state = "BOTH CLOSED"

        else:
            eye_state = "ONE EYE CLOSED"


        # ----------------------------------------------
        # Draw eye points
        # ----------------------------------------------

        for point in left_eye_points:

            cv2.circle(
                frame,
                point,
                3,
                (0, 255, 0),
                -1
            )


        for point in right_eye_points:

            cv2.circle(
                frame,
                point,
                3,
                (0, 255, 0),
                -1
            )


        # ----------------------------------------------
        # Display EAR
        # ----------------------------------------------

        cv2.putText(
            frame,
            f"Left EAR: {left_ear:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right EAR: {right_ear:.2f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Average EAR: {average_ear:.2f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        # ----------------------------------------------
        # Display eye state
        # ----------------------------------------------

        cv2.putText(
            frame,
            f"Eyes: {eye_state}",
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0) if eye_state == "OPEN" else (0, 0, 255),
            2
        )


    else:

        cv2.putText(
            frame,
            "NO FACE DETECTED",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )


    # --------------------------------------------------
    # Display window
    # --------------------------------------------------

    cv2.imshow(
        "Driver Safety System - Eye Detection",
        frame
    )


    # Press Q to exit

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()

face_landmarker.close()