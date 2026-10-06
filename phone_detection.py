# ============================================================
# MOBILE PHONE DETECTION USING YOLO
# ============================================================

from ultralytics import YOLO
import cv2


class PhoneDetector:

    def __init__(self, model_path="yolo11n.pt"):
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        print("YOLO model loaded successfully.")

    def detect(self, frame):
        """
        Detect mobile phone in the given frame.

        Returns:
            phone_detected : True/False
            annotated_frame : frame with detection box
        """

        results = self.model(frame, verbose=False)

        phone_detected = False

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                class_name = self.model.names[class_id]

                # YOLO COCO class name for mobile phone
                if class_name == "cell phone" and confidence >= 0.50:

                    phone_detected = True

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist()
                    )

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"PHONE {confidence:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

        return phone_detected, frame