from ultralytics import YOLO


class SeatbeltDetector:

    def __init__(self, model_path="seatbelt_best.pt"):

        print("Loading seatbelt model...")

        self.model = YOLO(model_path)

        print("Seatbelt model loaded successfully.")

        print("Classes:", self.model.names)

    def detect(self, frame):

        results = self.model(frame, verbose=False)

        best_class = None
        best_confidence = 0.0

        for result in results:

            if result.probs is None:
                continue

            class_id = int(result.probs.top1)
            confidence = float(result.probs.top1conf)

            best_class = self.model.names[class_id]
            best_confidence = confidence

        if best_class == "seat_belt":
            seatbelt_detected = True

        else:
            seatbelt_detected = False

        return (
            seatbelt_detected,
            best_class,
            best_confidence
        )