import cv2
import mediapipe as mp
import math
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import MAR_THRESHOLD, YAWN_DURATION


# ============================================================
# Calculate Euclidean distance between two points
# ============================================================

def distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


# ============================================================
# Calculate Mouth Aspect Ratio (MAR)
# ============================================================

def calculate_mar(mouth_points):

    p1, p2, p3, p4, p5, p6 = mouth_points

    # Vertical mouth distances
    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    # Horizontal mouth distance
    horizontal = distance(p1, p4)

    # Prevent division by zero
    if horizontal == 0:
        return 0.0

    # MAR formula
    mar = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)

    return mar


# ============================================================
# MediaPipe Face Landmarker
# ============================================================

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


face_landmarker = vision.FaceLandmarker.create_from_options(
    options
)


# ============================================================
# Open Webcam
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("Error: Could not open webcam.")

    exit()


# ============================================================
# Mouth Landmark Indexes
#
# 61  -> Left mouth corner
# 81  -> Upper/inner-left mouth
# 13  -> Upper inner lip
# 291 -> Right mouth corner
# 311 -> Lower/inner-right mouth
# 14  -> Lower inner lip
# ============================================================

MOUTH_POINTS = [
    61,
    81,
    13,
    291,
    311,
    14
]


# ============================================================
# Yawning Detection Variables
# ============================================================

mouth_open_start_time = None

yawning_detected = False

mouth_open_duration = 0.0

frame_timestamp_ms = 0


# ============================================================
# Main Loop
# ============================================================

while True:

    # --------------------------------------------------------
    # Read webcam frame
    # --------------------------------------------------------

    ret, frame = cap.read()


    if not ret:

        print("Error: Could not read frame.")

        break


    # --------------------------------------------------------
    # Flip webcam horizontally
    # --------------------------------------------------------

    frame = cv2.flip(frame, 1)


    # Get frame dimensions

    height, width, _ = frame.shape


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # Create MediaPipe Image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # Detect Face Landmarks
    # --------------------------------------------------------

    result = face_landmarker.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    # Increase timestamp

    frame_timestamp_ms += 33


    # ========================================================
    # FACE DETECTED
    # ========================================================

    if result.face_landmarks:

        landmarks = result.face_landmarks[0]


        # ----------------------------------------------------
        # Extract mouth landmark coordinates
        # ----------------------------------------------------

        mouth_points = []


        for index in MOUTH_POINTS:

            landmark = landmarks[index]

            x = int(landmark.x * width)

            y = int(landmark.y * height)

            mouth_points.append((x, y))


        # ----------------------------------------------------
        # Calculate MAR
        # ----------------------------------------------------

        mar = calculate_mar(mouth_points)


        # ----------------------------------------------------
        # Determine mouth state
        # ----------------------------------------------------

        if mar >= MAR_THRESHOLD:

            mouth_state = "OPEN"

        else:

            mouth_state = "CLOSED"


        # ====================================================
        # YAWNING DETECTION
        # ====================================================

        if mouth_state == "OPEN":

            # -----------------------------------------------
            # Start timer
            # -----------------------------------------------

            if mouth_open_start_time is None:

                mouth_open_start_time = time.time()


            # -----------------------------------------------
            # Calculate how long mouth is open
            # -----------------------------------------------

            mouth_open_duration = (
                time.time()
                - mouth_open_start_time
            )


            # -----------------------------------------------
            # Check yawning duration
            # -----------------------------------------------

            if mouth_open_duration >= YAWN_DURATION:

                yawning_detected = True

            else:

                yawning_detected = False


        else:

            # ------------------------------------------------
            # Mouth closed
            # ------------------------------------------------

            mouth_open_start_time = None

            mouth_open_duration = 0.0

            yawning_detected = False


        # ====================================================
        # Draw Mouth Landmarks
        # ====================================================

        for point in mouth_points:

            cv2.circle(
                frame,
                point,
                4,
                (255, 0, 0),
                -1
            )


        # ====================================================
        # Display MAR
        # ====================================================

        cv2.putText(
            frame,
            f"MAR: {mar:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


        # ====================================================
        # Display MAR Threshold
        # ====================================================

        cv2.putText(
            frame,
            f"Threshold: {MAR_THRESHOLD:.2f}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        # ====================================================
        # Display Mouth State
        # ====================================================

        cv2.putText(
            frame,
            f"Mouth: {mouth_state}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )


        # ====================================================
        # Display Open Duration
        # ====================================================

        cv2.putText(
            frame,
            f"Open Duration: {mouth_open_duration:.1f}s",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        # ====================================================
        # Display Yawning Status
        # ====================================================

        if yawning_detected:

            cv2.putText(
                frame,
                "YAWNING DETECTED!",
                (20, 195),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )

        else:

            cv2.putText(
                frame,
                "STATUS: NORMAL",
                (20, 195),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )


    # ========================================================
    # NO FACE DETECTED
    # ========================================================

    else:

        # Reset variables

        mouth_open_start_time = None

        mouth_open_duration = 0.0

        yawning_detected = False


        # Display warning

        cv2.putText(
            frame,
            "NO FACE DETECTED",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2
        )


    # ========================================================
    # Display Webcam
    # ========================================================

    cv2.imshow(
        "Driver Safety System - Yawning Detection",
        frame
    )


    # ========================================================
    # Press Q to Exit
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# Cleanup
# ============================================================

cap.release()

cv2.destroyAllWindows()

face_landmarker.close()