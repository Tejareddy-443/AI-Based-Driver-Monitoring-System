from event_logger import log_event


print("Testing event logger...")

log_event("DROWSINESS", 2.45)
log_event("YAWNING", 1.32)
log_event("DISTRACTION_LEFT", 3.10)
log_event("DISTRACTION_RIGHT", 2.75)

print("Event logging test completed.")