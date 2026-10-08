import os
import pyttsx3


# ============================================================
# CREATE ASSETS FOLDER
# ============================================================

os.makedirs("assets", exist_ok=True)


# ============================================================
# INITIALIZE TEXT-TO-SPEECH ENGINE
# ============================================================

try:
    engine = pyttsx3.init()
except Exception as e:
    print("ERROR: Could not initialize text-to-speech engine.")
    print("Details:", e)
    raise


# ============================================================
# SPEECH SETTINGS
# ============================================================

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)


# ============================================================
# ALERT MESSAGES
# ============================================================

alerts = {
    "drowsiness.wav": "Wake up! Please keep your eyes open.",
    "yawn.wav": "You appear tired. Please stay alert.",
    "distraction.wav": "Please keep your eyes on the road.",
    "phone.wav": "Warning! Mobile phone detected. Please stop using your phone while driving.",
    "seatbelt.wav": "Please fasten your seatbelt for safety."
}


# ============================================================
# GENERATE AUDIO FILES
# ============================================================

print()
print("==========================================")
print("       CREATING VOICE ALERTS")
print("==========================================")
print()

for filename, message in alerts.items():
    output_path = os.path.join("assets", filename)
    print(f"Creating: {filename}")

    try:
        engine.save_to_file(message, output_path)
        print(f"Message: {message}")
        print(f"Output: {output_path}")
        print()
    except Exception as e:
        print(f"ERROR creating {filename}")
        print("Details:", e)

try:
    engine.runAndWait()
except Exception as e:
    print("ERROR while generating audio files.")
    print("Details:", e)
    raise


# ============================================================
# CONFIRM CREATION
# ============================================================

print()
print("==========================================")
print("       CHECKING AUDIO FILES")
print("==========================================")
print()

for filename in alerts.keys():
    output_path = os.path.join("assets", filename)
    if os.path.exists(output_path):
        print(f"[OK] {filename}")
    else:
        print(f"[ERROR] {filename} was not created.")

print()
print("Voice alerts generation complete.")
print()
