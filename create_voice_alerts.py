import pyttsx3
import os


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
    exit()


# ============================================================
# SPEECH SETTINGS
# ============================================================

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)


# ============================================================
# VOICE ALERT MESSAGES
# ============================================================

alerts = {
    "drowsiness.wav":
        "Wake up! Please keep your eyes open.",

    "yawn.wav":
        "You appear tired. Please stay alert.",

    "distraction.wav":
        "Please keep your eyes on the road.",

    "phone.wav":
        "Warning! Mobile phone detected. Please stop using your phone while driving."
}


# ============================================================
# GENERATE VOICE ALERTS
# ============================================================

print()
print("==========================================")
print("       CREATING VOICE ALERTS")
print("==========================================")
print()


for filename, message in alerts.items():

    output_path = os.path.join(
        "assets",
        filename
    )

    print(f"Creating: {filename}")

    try:

        engine.save_to_file(
            message,
            output_path
        )

        print(f"Message: {message}")
        print(f"Output: {output_path}")
        print()

    except Exception as e:

        print(f"ERROR creating {filename}")
        print("Details:", e)


# ============================================================
# GENERATE ALL AUDIO FILES
# ============================================================

try:

    engine.runAndWait()

except Exception as e:

    print("ERROR while generating audio files.")
    print("Details:", e)
    exit()


# ============================================================
# CHECK GENERATED FILES
# ============================================================

print()
print("==========================================")
print("       CHECKING AUDIO FILES")
print("==========================================")
print()


all_created = True


for filename in alerts.keys():

    output_path = os.path.join(
        "assets",
        filename
    )

    if os.path.exists(output_path):

        file_size = os.path.getsize(output_path)

        if file_size > 0:

            print(f"[OK] {filename}")

        else:

            print(f"[ERROR] {filename} is empty.")
            all_created = False

    else:

        print(f"[ERROR] {filename} was not created.")
        all_created = False


# ============================================================
# CLEANUP
# ============================================================

try:
    engine.stop()
except Exception:
    pass


# ============================================================
# FINAL MESSAGE
# ============================================================

print()

if all_created:

    print("==========================================")
    print(" ALL VOICE ALERTS CREATED SUCCESSFULLY")
    print("==========================================")

    print()
    print("Files created:")

    for filename in alerts.keys():
        print(f" - assets\\{filename}")

else:

    print("==========================================")
    print(" SOME AUDIO FILES WERE NOT CREATED")
    print("==========================================")

print()