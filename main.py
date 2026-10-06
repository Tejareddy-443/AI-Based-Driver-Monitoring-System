import cv2
import mediapipe as mp
import numpy as np
import math
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    EAR_THRESHOLD,
    DROWSINESS_DURATION,
    MAR_THRESHOLD,
    YAWN_DURATION,
    YAW_THRESHOLD,
    PITCH_THRESHOLD,
    DISTRACTION_DURATION,
    PHONE_DURATION
)

from phone_detection import PhoneDetector

from alerts import (
    play_drowsiness_alert,
    play_yawn_alert,
    play_distraction_alert,
    play_phone_alert
)

from event_logger import log_event

from safety_score import SafetyScore


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(p1, p2):
    """
    Calculate Euclidean distance between two points.
    """

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def calculate_ear(points):
    """
    Calculate Eye Aspect Ratio (EAR).
    """

    p1, p2, p3, p4, p5, p6 = points

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0.0

    ear = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)

    return ear


def calculate_mar(points):
    """
    Calculate Mouth Aspect Ratio (MAR).
    """

    p1, p2, p3, p4, p5, p6 = points

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0.0

    mar = (
        vertical_1 + vertical_2
    ) / (2.0 * horizontal)

    return mar


# ============================================================
# MEDIAPIPE FACE LANDMARKER
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
# MOBILE PHONE DETECTOR
# ============================================================

print()
print("==========================================")
print("     LOADING MOBILE PHONE DETECTOR")
print("==========================================")
print()

phone_detector = PhoneDetector()

print()
print("Mobile phone detector ready.")
print()


# ============================================================
# SAFETY SCORE
# ============================================================

safety_score = SafetyScore()


# ============================================================
# WEBCAM
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Could not open webcam.")

    face_landmarker.close()

    exit()


# ============================================================
# CAMERA WINDOW
# ============================================================

WINDOW_NAME = "AI Driver Safety System"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    1100,
    700
)


# ============================================================
# LANDMARK INDEXES
# ============================================================

# Left eye landmarks
LEFT_EYE = [
    33,
    160,
    158,
    133,
    153,
    144
]


# Right eye landmarks
RIGHT_EYE = [
    362,
    385,
    387,
    263,
    373,
    380
]


# Mouth landmarks
MOUTH_POINTS = [
    61,
    81,
    13,
    291,
    311,
    14
]


# ============================================================
# HEAD POSE MODEL POINTS
# ============================================================

MODEL_POINTS = np.array(

    [
        (0.0, 0.0, 0.0),              # Nose
        (0.0, -330.0, -65.0),         # Chin
        (-225.0, 170.0, -135.0),       # Left eye
        (225.0, 170.0, -135.0),        # Right eye
        (-150.0, -150.0, -125.0),     # Left mouth
        (150.0, -150.0, -125.0)       # Right mouth
    ],

    dtype=np.float64
)


LANDMARK_IDS = [
    1,      # Nose
    152,    # Chin
    33,     # Left eye
    263,    # Right eye
    61,     # Left mouth
    291     # Right mouth
]


# ============================================================
# TIMERS
# ============================================================

eyes_closed_start_time = None

mouth_open_start_time = None

distraction_start_time = None

phone_start_time = None


# ============================================================
# DETECTION STATES
# ============================================================

drowsiness_detected = False

yawning_detected = False

distraction_detected = False

phone_detected = False


# ============================================================
# EVENT LOGGING STATES
# ============================================================

drowsiness_logged = False

yawn_logged = False

distraction_logged = False

phone_logged = False


# ============================================================
# DISPLAY / CALCULATION VARIABLES
# ============================================================

frame_timestamp_ms = 0

previous_direction = "FORWARD"

closed_duration = 0.0

mouth_open_duration = 0.0

distraction_duration = 0.0

phone_duration = 0.0


average_ear = 0.0

mar = 0.0

yaw = 0.0

pitch = 0.0

roll = 0.0

direction = "UNKNOWN"


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # ========================================================
    # READ CAMERA FRAME
    # ========================================================

    ret, frame = cap.read()

    if not ret:

        print("ERROR: Could not read frame.")

        break


    # ========================================================
    # MIRROR FRAME
    # ========================================================

    frame = cv2.flip(
        frame,
        1
    )


    height, width, _ = frame.shape


    # ========================================================
    # MOBILE PHONE DETECTION
    # ========================================================

    phone_found, frame = phone_detector.detect(
        frame
    )


    if phone_found:

        # Start phone timer
        if phone_start_time is None:

            phone_start_time = time.time()


        # Calculate phone duration
        phone_duration = (
            time.time()
            -
            phone_start_time
        )


        # Phone detected continuously
        if phone_duration >= PHONE_DURATION:

            phone_detected = True

        else:

            phone_detected = False


    else:

        # Reset phone detection
        phone_start_time = None

        phone_duration = 0.0

        phone_detected = False

        phone_logged = False


    # ========================================================
    # CONVERT FRAME FOR MEDIAPIPE
    # ========================================================

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    # ========================================================
    # FACE LANDMARK DETECTION
    # ========================================================

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


        # ====================================================
        # EYE DETECTION
        # ====================================================

        left_eye_points = []

        right_eye_points = []


        # ----------------------------------------------------
        # Left Eye
        # ----------------------------------------------------

        for index in LEFT_EYE:

            landmark = landmarks[index]

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            left_eye_points.append(
                (x, y)
            )


        # ----------------------------------------------------
        # Right Eye
        # ----------------------------------------------------

        for index in RIGHT_EYE:

            landmark = landmarks[index]

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            right_eye_points.append(
                (x, y)
            )


        # Calculate EAR

        left_ear = calculate_ear(
            left_eye_points
        )

        right_ear = calculate_ear(
            right_eye_points
        )


        average_ear = (
            left_ear +
            right_ear
        ) / 2.0


        # ====================================================
        # DROWSINESS DETECTION
        # ====================================================

        if average_ear < EAR_THRESHOLD:

            # Start timer
            if eyes_closed_start_time is None:

                eyes_closed_start_time = time.time()


            # Calculate closed duration
            closed_duration = (
                time.time()
                -
                eyes_closed_start_time
            )


            # Check duration
            if closed_duration >= DROWSINESS_DURATION:

                drowsiness_detected = True

            else:

                drowsiness_detected = False


        else:

            eyes_closed_start_time = None

            closed_duration = 0.0

            drowsiness_detected = False

            drowsiness_logged = False


        # ====================================================
        # MOUTH / YAWN DETECTION
        # ====================================================

        mouth_points = []


        for index in MOUTH_POINTS:

            landmark = landmarks[index]

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            mouth_points.append(
                (x, y)
            )


        # Calculate MAR

        mar = calculate_mar(
            mouth_points
        )


        # ====================================================
        # YAWN TIMER
        # ====================================================

        if mar >= MAR_THRESHOLD:

            if mouth_open_start_time is None:

                mouth_open_start_time = time.time()


            mouth_open_duration = (
                time.time()
                -
                mouth_open_start_time
            )


            if mouth_open_duration >= YAWN_DURATION:

                yawning_detected = True

            else:

                yawning_detected = False


        else:

            mouth_open_start_time = None

            mouth_open_duration = 0.0

            yawning_detected = False

            yawn_logged = False


        # ====================================================
        # HEAD POSE DETECTION
        # ====================================================

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


        # ====================================================
        # CAMERA MATRIX
        # ====================================================

        focal_length = width

        center = (
            width / 2,
            height / 2
        )


        camera_matrix = np.array(

            [
                [focal_length, 0, center[0]],

                [0, focal_length, center[1]],

                [0, 0, 1]
            ],

            dtype=np.float64
        )


        distortion_coefficients = np.zeros(
            (4, 1),
            dtype=np.float64
        )


        # ====================================================
        # SOLVE HEAD POSE
        # ====================================================

        success, rotation_vector, translation_vector = cv2.solvePnP(

            MODEL_POINTS,

            image_points,

            camera_matrix,

            distortion_coefficients,

            flags=cv2.SOLVEPNP_ITERATIVE
        )


        if success:

            # Convert rotation vector
            rotation_matrix, _ = cv2.Rodrigues(
                rotation_vector
            )


            # Get angles
            angles = cv2.RQDecomp3x3(
                rotation_matrix
            )


            pitch = angles[0][0]

            yaw = angles[0][1]

            roll = angles[0][2]


            # =================================================
            # FIX PITCH WRAPAROUND
            # =================================================

            if pitch > 90:

                pitch -= 180

            elif pitch < -90:

                pitch += 180


            # =================================================
            # DETERMINE HEAD DIRECTION
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
            # DISTRACTION DETECTION
            # =================================================

            if direction != "FORWARD":

                # Direction changed
                if previous_direction != direction:

                    distraction_start_time = time.time()

                    distraction_duration = 0.0

                    distraction_detected = False


                # Start timer if required
                if distraction_start_time is None:

                    distraction_start_time = time.time()


                # Calculate duration
                distraction_duration = (
                    time.time()
                    -
                    distraction_start_time
                )


                # Check duration
                if distraction_duration >= DISTRACTION_DURATION:

                    distraction_detected = True

                else:

                    distraction_detected = False


            else:

                distraction_start_time = None

                distraction_duration = 0.0

                distraction_detected = False

                distraction_logged = False


            previous_direction = direction


    # ========================================================
    # NO FACE DETECTED
    # ========================================================

    else:

        # Reset face-related timers

        eyes_closed_start_time = None

        mouth_open_start_time = None

        distraction_start_time = None


        # Reset durations

        closed_duration = 0.0

        mouth_open_duration = 0.0

        distraction_duration = 0.0


        # Reset detection states

        drowsiness_detected = False

        yawning_detected = False

        distraction_detected = False


        # Reset logging states

        drowsiness_logged = False

        yawn_logged = False

        distraction_logged = False


        # Reset head pose

        previous_direction = "FORWARD"

        yaw = 0.0

        pitch = 0.0

        roll = 0.0

        direction = "UNKNOWN"


        # Reset measurements

        average_ear = 0.0

        mar = 0.0


    # ========================================================
    # EVENT LOGGING + SAFETY SCORE
    # ========================================================


    # ========================================================
    # DROWSINESS EVENT
    # ========================================================

    if drowsiness_detected:

        # Play drowsiness voice
        play_drowsiness_alert()


        # Log only once per episode
        if not drowsiness_logged:

            log_event(
                "DROWSINESS",
                closed_duration
            )


            # Reduce safety score
            safety_score.add_drowsiness()


            drowsiness_logged = True


    # ========================================================
    # YAWN EVENT
    # ========================================================

    if yawning_detected:

        # Play yawn voice
        play_yawn_alert()


        # Log only once per episode
        if not yawn_logged:

            log_event(
                "YAWNING",
                mouth_open_duration
            )


            # Reduce safety score
            safety_score.add_yawning()


            yawn_logged = True


    # ========================================================
    # DISTRACTION EVENT
    # ========================================================

    if distraction_detected:

        # Play distraction voice
        play_distraction_alert()


        # Log only once per episode
        if not distraction_logged:

            log_event(
                "DISTRACTION",
                distraction_duration
            )


            # Reduce safety score
            safety_score.add_distraction()


            distraction_logged = True


    # ========================================================
    # PHONE EVENT
    # ========================================================

    if phone_detected:

        # Play phone-specific voice
        play_phone_alert()


        # Log only once per phone episode
        if not phone_logged:

            log_event(
                "PHONE_USAGE",
                phone_duration
            )


            # Reduce safety score
            safety_score.add_phone_usage()


            phone_logged = True


    # ========================================================
    # DETERMINE MAIN STATUS
    # ========================================================

    if drowsiness_detected:

        status = "DROWSINESS DETECTED"

        status_color = (0, 0, 255)


    elif yawning_detected:

        status = "YAWNING DETECTED"

        status_color = (0, 165, 255)


    elif distraction_detected:

        status = "DISTRACTION DETECTED"

        status_color = (0, 0, 255)


    elif phone_detected:

        status = "PHONE DETECTED"

        status_color = (0, 0, 255)


    else:

        status = "DRIVER NORMAL"

        status_color = (0, 180, 0)


    # ========================================================
    # SAFETY SCORE
    # ========================================================

    score = safety_score.get_score()

    score_status = safety_score.get_status()


    # ========================================================
    # SAFETY SCORE COLOR
    # ========================================================

    if score >= 80:

        score_color = (0, 200, 0)


    elif score >= 60:

        score_color = (0, 200, 255)


    elif score >= 40:

        score_color = (0, 165, 255)


    else:

        score_color = (0, 0, 255)


    # ========================================================
    # DARK DASHBOARD PANEL
    # ========================================================

    overlay = frame.copy()


    cv2.rectangle(

        overlay,

        (10, 10),

        (440, 500),

        (25, 25, 25),

        -1
    )


    # Blend dashboard with camera
    cv2.addWeighted(

        overlay,

        0.82,

        frame,

        0.18,

        0,

        frame
    )


    # ========================================================
    # TITLE
    # ========================================================

    cv2.putText(

        frame,

        "AI DRIVER SAFETY SYSTEM",

        (25, 45),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.72,

        (255, 255, 255),

        2
    )


    # ========================================================
    # MAIN STATUS BOX
    # ========================================================

    cv2.rectangle(

        frame,

        (20, 60),

        (430, 120),

        status_color,

        -1
    )


    cv2.putText(

        frame,

        status,

        (35, 98),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.68,

        (255, 255, 255),

        2
    )


    # ========================================================
    # FACE ANALYSIS TITLE
    # ========================================================

    cv2.putText(

        frame,

        "FACE ANALYSIS",

        (25, 150),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.58,

        (180, 180, 180),

        2
    )


    # ========================================================
    # EAR
    # ========================================================

    cv2.putText(

        frame,

        f"Eye Ratio (EAR)   : {average_ear:.2f}",

        (30, 180),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.53,

        (255, 255, 255),

        1
    )


    # ========================================================
    # MAR
    # ========================================================

    cv2.putText(

        frame,

        f"Mouth Ratio (MAR) : {mar:.2f}",

        (30, 205),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.53,

        (255, 255, 255),

        1
    )


    # ========================================================
    # HEAD DIRECTION
    # ========================================================

    direction_color = (255, 255, 255)

    if direction != "FORWARD" and direction != "UNKNOWN":

        direction_color = (0, 165, 255)


    cv2.putText(

        frame,

        f"Head Direction    : {direction}",

        (30, 230),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.53,

        direction_color,

        1
    )


    # ========================================================
    # YAW
    # ========================================================

    cv2.putText(

        frame,

        f"Yaw               : {yaw:.1f}",

        (30, 255),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.53,

        (255, 255, 255),

        1
    )


    # ========================================================
    # PITCH
    # ========================================================

    cv2.putText(

        frame,

        f"Pitch             : {pitch:.1f}",

        (30, 280),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.53,

        (255, 255, 255),

        1
    )


    # ========================================================
    # PHONE DETECTION TITLE
    # ========================================================

    cv2.putText(

        frame,

        "PHONE DETECTION",

        (25, 315),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.58,

        (180, 180, 180),

        2
    )


    # ========================================================
    # PHONE STATUS
    # ========================================================

    if phone_detected:

        phone_text = "PHONE: DETECTED"

        phone_color = (0, 0, 255)

    else:

        phone_text = "PHONE: NOT DETECTED"

        phone_color = (0, 200, 0)


    cv2.putText(

        frame,

        phone_text,

        (30, 345),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.62,

        phone_color,

        2
    )


    # ========================================================
    # SAFETY SCORE
    # ========================================================

    cv2.putText(

        frame,

        f"SAFETY SCORE: {score}/100",

        (25, 385),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.62,

        (255, 255, 255),

        2
    )


    # ========================================================
    # SAFETY STATUS
    # ========================================================

    cv2.putText(

        frame,

        f"SAFETY: {score_status}",

        (30, 415),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.62,

        score_color,

        2
    )


    # ========================================================
    # EVENT COUNTERS
    # ========================================================

    counter_text = (

        f"Drowsy: {safety_score.drowsiness_count}   "

        f"Yawn: {safety_score.yawning_count}   "

        f"Distraction: {safety_score.distraction_count}   "

        f"Phone: {safety_score.phone_count}"
    )


    cv2.putText(

        frame,

        counter_text,

        (25, 455),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.43,

        (220, 220, 220),

        1
    )


    # ========================================================
    # EXIT INFORMATION
    # ========================================================

    cv2.putText(

        frame,

        "Press Q to Exit",

        (25, 485),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (160, 160, 160),

        1
    )


    # ========================================================
    # DISPLAY WINDOW
    # ========================================================

    cv2.imshow(

        WINDOW_NAME,

        frame
    )


    # ========================================================
    # EXIT WITH Q
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

face_landmarker.close()


# ============================================================
# FINAL SUMMARY
# ============================================================

print()

print("==========================================")
print("       DRIVER SAFETY SYSTEM CLOSED")
print("==========================================")

print()

print(
    f"Drowsiness Events : "
    f"{safety_score.drowsiness_count}"
)

print(
    f"Yawn Events       : "
    f"{safety_score.yawning_count}"
)

print(
    f"Distraction Events: "
    f"{safety_score.distraction_count}"
)

print(
    f"Phone Events      : "
    f"{safety_score.phone_count}"
)

print()

print(
    f"Final Safety Score: "
    f"{safety_score.get_score()}/100"
)

print(
    f"Safety Status     : "
    f"{safety_score.get_status()}"
)

print()

print("Events saved to events.csv")

print()

print("==========================================")
print("       SYSTEM SHUTDOWN COMPLETE")
print("==========================================")