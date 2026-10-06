import cv2
import mediapipe as mp
import numpy as np
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    YAW_THRESHOLD,
    PITCH_THRESHOLD,
    DISTRACTION_DURATION
)


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
# Webcam
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("Error: Could not open webcam.")

    exit()


# ============================================================
# 3D Facial Model Points
# ============================================================

MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),   # Left eye
    (225.0, 170.0, -135.0),    # Right eye
    (-150.0, -150.0, -125.0), # Left mouth
    (150.0, -150.0, -125.0)   # Right mouth
], dtype=np.float64)


# ============================================================
# MediaPipe Landmark IDs
# ============================================================

LANDMARK_IDS = [
    1,      # Nose
    152,    # Chin
    33,     # Left eye
    263,    # Right eye
    61,     # Left mouth
    291     # Right mouth
]


# ============================================================
# Variables
# ============================================================

frame_timestamp_ms = 0

distraction_start_time = None

distraction_detected = False

distraction_duration = 0.0

previous_direction = "FORWARD"


# ============================================================
# Main Loop
# ============================================================

while True:

    # --------------------------------------------------------
    # Read frame
    # --------------------------------------------------------

    ret, frame = cap.read()


    if not ret:

        print("Error: Could not read frame.")

        break


    # --------------------------------------------------------
    # Mirror webcam
    # --------------------------------------------------------

    frame = cv2.flip(frame, 1)


    height, width, _ = frame.shape


    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # Create MediaPipe image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # --------------------------------------------------------
    # Detect landmarks
    # --------------------------------------------------------

    result = face_landmarker.detect_for_video(
        mp_image,
        frame_timestamp_ms
    )


    frame_timestamp_ms += 33


    # ========================================================
    # FACE DETECTED
    # ========================================================

    if result.face_landmarks:

        landmarks = result.face_landmarks[0]


        # ----------------------------------------------------
        # Get image points
        # ----------------------------------------------------

        image_points = []


        for landmark_id in LANDMARK_IDS:

            landmark = landmarks[landmark_id]

            x = landmark.x * width

            y = landmark.y * height

            image_points.append(
                (x, y)
            )


        image_points = np.array(
            image_points,
            dtype=np.float64
        )


        # ----------------------------------------------------
        # Camera matrix
        # ----------------------------------------------------

        focal_length = width

        center = (
            width / 2,
            height / 2
        )


        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)


        # ----------------------------------------------------
        # Distortion coefficients
        # ----------------------------------------------------

        distortion_coefficients = np.zeros(
            (4, 1),
            dtype=np.float64
        )


        # ----------------------------------------------------
        # Solve PnP
        # ----------------------------------------------------

        success, rotation_vector, translation_vector = cv2.solvePnP(
            MODEL_POINTS,
            image_points,
            camera_matrix,
            distortion_coefficients,
            flags=cv2.SOLVEPNP_ITERATIVE
        )


        if success:

            # ------------------------------------------------
            # Rotation matrix
            # ------------------------------------------------

            rotation_matrix, _ = cv2.Rodrigues(
                rotation_vector
            )


            # ------------------------------------------------
            # Euler angles
            # ------------------------------------------------

            angles = cv2.RQDecomp3x3(
                rotation_matrix
            )


            pitch = angles[0][0]

            yaw = angles[0][1]

            roll = angles[0][2]


            # =================================================
            # Fix pitch wraparound
            # =================================================

            if pitch > 90:

                pitch -= 180

            elif pitch < -90:

                pitch += 180


            # =================================================
            # Determine head direction
            # =================================================

            if yaw < -YAW_THRESHOLD:

                direction = "LEFT"

            elif yaw > YAW_THRESHOLD:

                direction = "RIGHT"

            elif pitch > PITCH_THRESHOLD:

                direction = "DOWN"

            elif pitch < -PITCH_THRESHOLD:

                direction = "UP"

            else:

                direction = "FORWARD"


            # =================================================
            # Distraction Timer
            # =================================================

            if direction != "FORWARD":

                # --------------------------------------------
                # If direction just changed
                # --------------------------------------------

                if previous_direction != direction:

                    distraction_start_time = time.time()

                    distraction_duration = 0.0

                    distraction_detected = False


                # --------------------------------------------
                # Start timer if necessary
                # --------------------------------------------

                if distraction_start_time is None:

                    distraction_start_time = time.time()


                # --------------------------------------------
                # Calculate duration
                # --------------------------------------------

                distraction_duration = (
                    time.time()
                    - distraction_start_time
                )


                # --------------------------------------------
                # Check distraction threshold
                # --------------------------------------------

                if distraction_duration >= DISTRACTION_DURATION:

                    distraction_detected = True

                else:

                    distraction_detected = False


            else:

                # --------------------------------------------
                # Driver looking forward
                # --------------------------------------------

                distraction_start_time = None

                distraction_duration = 0.0

                distraction_detected = False


            # Update previous direction

            previous_direction = direction


            # =================================================
            # Draw facial points
            # =================================================

            for point in image_points:

                x = int(point[0])

                y = int(point[1])

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )


            # =================================================
            # Display Yaw
            # =================================================

            cv2.putText(
                frame,
                f"Yaw: {yaw:.1f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )


            # =================================================
            # Display Pitch
            # =================================================

            cv2.putText(
                frame,
                f"Pitch: {pitch:.1f}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )


            # =================================================
            # Display Head Direction
            # =================================================

            if direction == "FORWARD":

                direction_color = (0, 255, 0)

            else:

                direction_color = (0, 0, 255)


            cv2.putText(
                frame,
                f"Head: {direction}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                direction_color,
                3
            )


            # =================================================
            # Display Distraction Duration
            # =================================================

            cv2.putText(
                frame,
                f"Distraction Time: {distraction_duration:.1f}s",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )


            # =================================================
            # Display Status
            # =================================================

            if distraction_detected:

                cv2.putText(
                    frame,
                    "DISTRACTION DETECTED!",
                    (20, 205),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.95,
                    (0, 0, 255),
                    3
                )

            else:

                cv2.putText(
                    frame,
                    "STATUS: NORMAL",
                    (20, 205),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )


    # ========================================================
    # NO FACE DETECTED
    # ========================================================

    else:

        distraction_start_time = None

        distraction_duration = 0.0

        distraction_detected = False

        previous_direction = "FORWARD"


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
    # Display
    # ========================================================

    cv2.imshow(
        "Driver Safety System - Distraction Detection",
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