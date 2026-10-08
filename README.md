# AI Driver Safety System

This project is a real-time driver monitoring system that uses OpenCV, MediaPipe, and YOLO to detect risky driving behavior. It monitors drowsiness, yawning, distraction, phone usage, and missing seatbelt compliance, then raises audio alerts and updates a live safety score.

## Features

- Drowsiness detection using Eye Aspect Ratio (EAR)
- Yawning detection using Mouth Aspect Ratio (MAR)
- Head pose and distraction detection
- Mobile phone detection with YOLO
- Seatbelt detection with alert and score penalty
- Safety score tracking and status updates
- Voice alerts for each detected risk
- CSV event logging for recorded incidents
- Webcam dashboard overlay with live metrics

## Project structure

- main.py - main application loop and live monitoring dashboard
- config.py - thresholds and timing values
- alerts.py - audio alert logic
- create_voice_alerts.py - generates the warning sound files
- event_logger.py - writes events to events.csv
- safety_score.py - tracks score and risk status
- phone_detection.py - YOLO phone detection logic
- seatbelt_detection.py - YOLO seatbelt detection logic
- drowsiness.py - standalone drowsiness logic reference
- distraction.py - standalone distraction logic reference
- head_pose.py - standalone head pose logic reference
- camera_test.py - webcam validation utility
- test_event_logger.py - event logger checks
- test_phone_detection.py - phone detection checks
- test_seatbelt_detection.py - seatbelt detection checks
- test_voice_alerts.py - alert playback checks
- assets/ - generated voice alert files
- driversafetyenv/ - local virtual environment (ignored by Git)
- face_landmarker.task - MediaPipe face landmark model
- yolo11n.pt - YOLO model weights
- seatbelt_best.pt - seatbelt detection model weights
- events.csv - generated log file

## Tech stack

- Python
- OpenCV
- MediaPipe
- NumPy
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

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install ultralytics
   ```

4. Make sure your webcam is connected and the model files are available locally.

## Run the application

```bash
python main.py
```

The app will open a webcam window and display the live driver safety status. Press Q to exit.

## Events and scoring

Detected events are logged in events.csv with the following fields:

- Date
- Time
- Event
- Duration (seconds)

Examples include:

- DROWSINESS
- YAWNING
- DISTRACTION
- PHONE_USAGE
- NO_SEATBELT

Current score penalties:

- Drowsiness: -15
- Yawning: -5
- Distraction: -10
- Phone usage: -15
- No seatbelt: -10

Risk ranges:

- 80 to 100: SAFE
- 60 to 79: MODERATE
- 40 to 59: WARNING
- Below 40: HIGH RISK

## Git and local files

The repository includes a .gitignore file to prevent unnecessary local files from being uploaded to GitHub, including:

- Python virtual environments
- compiled cache files
- generated logs and runtime data
- large local model files
- generated voice alert audio

This keeps the Git repo small and avoids uploading machine-specific local artifacts.

## Notes

- The project is designed for local testing and real-time monitoring on a machine with a webcam.
- Large model files and generated audio are stored locally and are intentionally ignored by Git.
- If you need to regenerate the alert sound files, run:

  ```bash
  python create_voice_alerts.py
  ```
