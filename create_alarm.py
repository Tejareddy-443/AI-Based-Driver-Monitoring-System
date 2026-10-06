import wave
import math
import struct


# ============================================================
# Alarm settings
# ============================================================

sample_rate = 44100
duration = 1.0

frequency1 = 900
frequency2 = 1400

volume = 0.5


# ============================================================
# Create WAV file
# ============================================================

file_path = "assets/alarm.wav"

with wave.open(file_path, "w") as wav_file:

    wav_file.setnchannels(1)

    wav_file.setsampwidth(2)

    wav_file.setframerate(sample_rate)

    total_samples = int(sample_rate * duration)

    for i in range(total_samples):

        time_value = i / sample_rate

        # Alternate between two frequencies
        if int(time_value * 4) % 2 == 0:
            frequency = frequency1
        else:
            frequency = frequency2

        sample = volume * math.sin(
            2 * math.pi * frequency * time_value
        )

        value = int(sample * 32767)

        wav_file.writeframes(
            struct.pack("<h", value)
        )


print("Alarm created successfully!")
print("File:", file_path)