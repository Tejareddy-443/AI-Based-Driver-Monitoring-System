import csv
import os
from datetime import datetime


# ============================================================
# EVENT LOG FILE
# ============================================================

LOG_FILE = "events.csv"


# ============================================================
# CREATE CSV FILE IF IT DOES NOT EXIST
# ============================================================

def initialize_log():

    if not os.path.exists(LOG_FILE):

        with open(
            LOG_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date",
                "Time",
                "Event",
                "Duration (seconds)"
            ])


# ============================================================
# LOG EVENT
# ============================================================

def log_event(event_name, duration):

    initialize_log()

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            date,
            time,
            event_name,
            round(duration, 2)
        ])

    print(
        f"[EVENT LOGGED] {event_name} | "
        f"Duration: {duration:.2f}s"
    )