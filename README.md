# AI Driver Safety System

This project is a real-time driver monitoring application built with Python, OpenCV, MediaPipe, and YOLO. It detects risky driver behavior and raises alerts when the driver appears drowsy, yawning, distracted, or using a mobile phone while driving.

## What this project does

The current implementation includes:

- Drowsiness detection using Eye Aspect Ratio (EAR)
- Yawning detection using Mouth Aspect Ratio (MAR)
- Head pose and distraction tracking using facial landmark geometry
- Mobile phone detection using a YOLO model
- Safety scoring based on repeated risky events
- Voice alerts for drowsiness, yawning, distraction, and phone usage
- CSV event logging for detected incidents
- Dashboard overlay in the webcam window showing live status and score

## Project structure

- `main.py` - main webcam-based driver safety monitoring loop
- `config.py` - detection thresholds and timing values
- `phone_detection.py` - YOLO-based smartphone detection
- `drowsiness.py` - drowsiness logic helpers
- `yawn_detection.py` - yawn detection helpers
- `head_pose.py` - head orientation and distraction logic
- `safety_score.py` - scoring logic and risk levels
- `event_logger.py` - logs events into `events.csv`
- `alerts.py` - sound alerts using pygame
- `create_voice_alerts.py` - utility for creating alert sound files
- `camera_test.py` - webcam check utility
- `test_event_logger.py` - logger validation
- `test_phone_detection.py` - phone detection test
- `test_voice_alerts.py` - voice alert test
- `face_landmarker.task` - MediaPipe face landmark model
- `assets/` - audio alert files
- `driversafetyenv/` - local Python virtual environment

## Technology stack

- Python 3.10+
- OpenCV
- MediaPipe
- NumPy
- Pandas
- Matplotlib
- Pygame
- Ultralytics YOLO

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

   Windows:

   ```bash
   python -m venv driversafetyenv
   driversafetyenv\Scripts\activate
   ```

3. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   pip install ultralytics
   ```

4. Make sure the webcam is available and the model file `face_landmarker.task` is present in the project root.

## Run the application

Start the main monitoring system:

```bash
python main.py
```

The app opens a webcam window, monitors the driver, and shows live status such as:

- Driver normal
- Drowsiness detected
- Yawning detected
- Distraction detected
- Phone detected
- Safety score / 100

Press `Q` to close the application.

## Event logging

Detected events are written into `events.csv` with these columns:

- Date
- Time
- Event
- Duration (seconds)

Examples of logged events:

- `DROWSINESS`
- `YAWNING`
- `DISTRACTION`
- `PHONE_USAGE`

## Safety scoring

The system starts with a score of 100 and reduces points for risky behavior:

- Drowsiness: -15
- Yawning: -5
- Distraction: -10
- Phone usage: -15

The score is mapped to risk states:

- 80 to 100: SAFE
- 60 to 79: MODERATE
- 40 to 59: WARNING
- Below 40: HIGH RISK

## Current status

This project is in a working prototype stage. It includes the main live detection pipeline, alert system, logging, scoring, and local tests for the core features.

## Notes

- Audio files for warnings are expected under the `assets/` directory.
- Mobile detection depends on YOLO model weights and requires the `ultralytics` package.
- This project is designed for local testing and real-time driver monitoring on a machine with a webcam.
