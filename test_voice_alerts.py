from alerts import (
    play_drowsiness_alert,
    play_yawn_alert,
    play_distraction_alert
)

import time

print("Testing drowsiness alert...")
play_drowsiness_alert()
time.sleep(4)

print("Testing yawn alert...")
play_yawn_alert()
time.sleep(4)

print("Testing distraction alert...")
play_distraction_alert()
time.sleep(4)

print("\nAll three alerts tested.")