import pygame
import os
import time


# ============================================================
# Initialize Pygame Audio
# ============================================================

pygame.mixer.init()


# ============================================================
# Audio File Paths
# ============================================================

DROWSINESS_SOUND = os.path.join("assets", "drowsiness.wav")
YAWN_SOUND = os.path.join("assets", "yawn.wav")
DISTRACTION_SOUND = os.path.join("assets", "distraction.wav")
PHONE_SOUND = os.path.join("assets", "phone.wav")
SEATBELT_SOUND = os.path.join("assets", "seatbelt.wav")


# ============================================================
# Alert Cooldown
# ============================================================

ALERT_COOLDOWN = 3.0


# Store last alert time for each event
last_drowsiness_alert = 0
last_yawn_alert = 0
last_distraction_alert = 0
last_phone_alert = 0
last_seatbelt_alert = 0

# ============================================================
# Common Sound Function
# ============================================================

def play_sound(sound_file):

    if not os.path.exists(sound_file):

        print(f"[ERROR] Sound file not found: {sound_file}")

        return

    try:

        pygame.mixer.music.load(sound_file)

        pygame.mixer.music.play()

        print(f"[ALERT] Playing: {sound_file}")

    except Exception as e:

        print(f"[ERROR] Could not play sound: {sound_file}")

        print("Details:", e)


# ============================================================
# Drowsiness Alert
# ============================================================

def play_drowsiness_alert():

    global last_drowsiness_alert

    current_time = time.time()

    if current_time - last_drowsiness_alert >= ALERT_COOLDOWN:

        play_sound(DROWSINESS_SOUND)

        last_drowsiness_alert = current_time


# ============================================================
# Yawning Alert
# ============================================================

def play_yawn_alert():

    global last_yawn_alert

    current_time = time.time()

    if current_time - last_yawn_alert >= ALERT_COOLDOWN:

        play_sound(YAWN_SOUND)

        last_yawn_alert = current_time


# ============================================================
# Distraction Alert
# ============================================================

def play_distraction_alert():

    global last_distraction_alert

    current_time = time.time()

    if current_time - last_distraction_alert >= ALERT_COOLDOWN:

        play_sound(DISTRACTION_SOUND)

        last_distraction_alert = current_time


# ============================================================
# Mobile Phone Alert
# ============================================================

def play_phone_alert():

    global last_phone_alert

    current_time = time.time()

    if current_time - last_phone_alert >= ALERT_COOLDOWN:

        play_sound(PHONE_SOUND)

        last_phone_alert = current_time

def play_seatbelt_alert():

    global last_seatbelt_alert

    current_time = time.time()

    if current_time - last_seatbelt_alert >= ALERT_COOLDOWN:

        play_sound(SEATBELT_SOUND)

        last_seatbelt_alert = current_time