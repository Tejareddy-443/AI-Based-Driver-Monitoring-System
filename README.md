# AI Driver Safety System

This project is a real-time driver monitoring application built with Python, OpenCV, MediaPipe, and YOLO. It detects unsafe driving behavior such as drowsiness, yawning, distraction, mobile phone usage, and missing seatbelt compliance, then plays audio alerts and updates the driver's live safety score.

## Features

- Drowsiness detection using eye aspect ratio (EAR)
- Yawning detection using mouth aspect ratio (MAR)
- Distraction monitoring with head pose and face orientation analysis
- Mobile phone detection using a YOLO model
- Seatbelt detection with a visual alert and safety score reduction
- Real-time safety score and risk level tracking
- Audio warnings for each unsafe event
- Event logging to CSV for incidents and duration tracking
- Webcam dashboard with live status overlay

## Project structure

- main.py - main application loop and live webcam monitoring
- config.py - thresholds, timings, and detector settings
- alerts.py - plays alert sounds for the detected events
- create_voice_alerts.py - generates the WAV voice alerts from text
- event_logger.py - logs incidents into events.csv
- safety_score.py - maintains score and risk state
- phone_detection.py - YOLO-based phone detection logic
- seatbelt_detection.py - YOLO-based seatbelt detection logic
- drowsiness.py - drowsiness detection reference logic
- distraction.py - distraction detection reference logic
- head_pose.py - head pose analysis reference logic
- face_landmarker.task - MediaPipe face landmark model asset
- yolo11n.pt - YOLO object detection model
- seatbelt_best.pt - Seatbelt detection model
- assets/ - generated speech alert audio files
- events.csv - runtime incident log
- driversafetyenv/ - local Python virtual environment

## Tech stack

- Python 3.10+
- OpenCV
- MediaPipe
- NumPy
- PyGame
- Ultralytics YOLO
- pyttsx3 for TTS alert generation

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```bash
   python -m venv driversafetyenv
   driversafetyenv\Scripts\activate
   ```

3. Install project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make sure your webcam is available and the required local model files are present.

## Run the application

```bash
python main.py
```

The app opens the webcam and starts monitoring driver behavior. Press Q to exit the live dashboard.

## Alert system

The project generates local voice alerts in the assets folder. These include:

- drowsiness.wav
- yawn.wav
- distraction.wav
- phone.wav
- seatbelt.wav

If the audio files are missing, generate them with:

```bash
python create_voice_alerts.py
```

The current distraction message is:

> Please keep your eyes on the road.

## Event logging and scoring

Detected events are logged in events.csv with details such as:

- date
- time
- event type
- duration (seconds)

Current event types include:

- DROWSINESS
- YAWNING
- DISTRACTION
- PHONE_USAGE
- NO_SEATBELT

Scoring behavior:

- Drowsiness: -15
- Yawning: -5
- Distraction: -10
- Phone usage: -15
- No seatbelt: -10

Risk level ranges:

- 80 to 100: SAFE
- 60 to 79: MODERATE
- 40 to 59: WARNING
- Below 40: HIGH RISK

## Git and local files

A .gitignore file is used to keep local-only and generated files out of the repository, including:

- virtual environment folders
- Python cache files
- generated logs
- local model files
- exported audio files
- machine-specific runtime artifacts

This keeps the repository clean and avoids uploading local environment data to GitHub.

## Notes

- This project is intended for local real-time monitoring on a machine with a webcam.
- Large model files and generated voice files are stored locally and are not meant to be committed.
- The app is designed for active driver monitoring and alerting, not for remote deployment or cloud processing.
