import cv2
import numpy as np
import time
from datetime import datetime
from ultralytics import YOLO

class ColourDetector:
    def __init__(self, port=0, model_path='runs/detect/vial_detector/weights/best.pt'):
        self.port = port
        self.current_state = None
        self.previous_state = None
        self.state_start_time = None
        self.transitions = []

        # load trained YOLO model
        print("Loading vial detection model...")
        self.model = YOLO(model_path)
        print("Model loaded!")

        # HSV colour ranges
        self.colour_ranges = {
            'GREEN': {
                'lower': np.array([35, 50, 50]),
                'upper': np.array([85, 255, 255])
            },
            'RED': [
                {'lower': np.array([0, 50, 50]),   'upper': np.array([10, 255, 255])},
                {'lower': np.array([170, 50, 50]), 'upper': np.array([180, 255, 255])}
            ],
            'YELLOW': {
                'lower': np.array([20, 50, 50]),
                'upper': np.array([35, 255, 255])
            }
        }

    def detect_vial(self, frame):
        """
        STEP 1 - Use trained YOLO model to detect vial.
        Much more robust than HoughCircles especially when vial is moving.
        """
        results = self.model(frame, verbose=False)

        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                # get the most confident detection
                best = max(boxes, key=lambda b: b.conf)
                confidence = float(best.conf)

                # only accept if confidence is high enough
                if confidence > 0.5:
                    x1, y1, x2, y2 = map(int, best.xyxy[0])

                    # draw bounding box around vial
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                    cv2.putText(frame, f"Vial {confidence:.0%}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                    # crop strictly inside the vial box
                    vial_roi = frame[y1:y2, x1:x2]
                    return vial_roi, (x1, y1, x2, y2), frame

        # no vial detected
        cv2.putText(frame, "Vial NOT detected", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return None, None, frame

    def detect_colour_inside_vial(self, vial_roi):
        """
        STEP 2 - Detect colour strictly inside the detected vial only.
        """
        if vial_roi is None or vial_roi.size == 0:
            return 'UNKNOWN', {}

        hsv = cv2.cvtColor(vial_roi, cv2.COLOR_BGR2HSV)
        pixel_counts = {}

        # green
        mask_green = cv2.inRange(hsv,
                                  self.colour_ranges['GREEN']['lower'],
                                  self.colour_ranges['GREEN']['upper'])
        pixel_counts['GREEN'] = cv2.countNonZero(mask_green)

        # red
        mask_red1 = cv2.inRange(hsv,
                                 self.colour_ranges['RED'][0]['lower'],
                                 self.colour_ranges['RED'][0]['upper'])
        mask_red2 = cv2.inRange(hsv,
                                 self.colour_ranges['RED'][1]['lower'],
                                 self.colour_ranges['RED'][1]['upper'])
        pixel_counts['RED'] = cv2.countNonZero(mask_red1 + mask_red2)

        # yellow
        mask_yellow = cv2.inRange(hsv,
                                   self.colour_ranges['YELLOW']['lower'],
                                   self.colour_ranges['YELLOW']['upper'])
        pixel_counts['YELLOW'] = cv2.countNonZero(mask_yellow)

        dominant = max(pixel_counts, key=pixel_counts.get)

        if pixel_counts[dominant] > 300:
            return dominant, pixel_counts
        return 'UNKNOWN', pixel_counts

    def update_state(self, new_state):
        if new_state != self.current_state and new_state != 'UNKNOWN':
            if self.current_state is not None and self.state_start_time is not None:
                duration = time.time() - self.state_start_time
                transition = {
                    'from_state': self.current_state,
                    'to_state':   new_state,
                    'duration':   round(duration, 2),
                    'timestamp':  datetime.now().strftime('%H:%M:%S')
                }
                self.transitions.append(transition)
                print(f"[{transition['timestamp']}] {self.current_state} "
                      f"→ {new_state} (lasted {duration:.2f} sec)")

            self.current_state    = new_state
            self.state_start_time = time.time()
            print(f"New state: {new_state}")

    def draw_overlay(self, frame, state, pixel_counts, vial_found):
        colour_map = {
            'GREEN':   (0, 255, 0),
            'RED':     (0, 0, 255),
            'YELLOW':  (0, 255, 255),
            'UNKNOWN': (128, 128, 128)
        }

        if vial_found:
            cv2.putText(frame, "VIAL: DETECTED", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "VIAL: NOT DETECTED", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return frame

        label_colour = colour_map.get(state, (255, 255, 255))
        cv2.putText(frame, f"COLOUR: {state}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, label_colour, 2)

        y = 115
        for colour, count in pixel_counts.items():
            cv2.putText(frame, f"  {colour}: {count}px", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, colour_map[colour], 1)
            y += 22

        if self.state_start_time:
            elapsed = time.time() - self.state_start_time
            cv2.putText(frame, f"Duration: {elapsed:.1f}s", (10, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame

    def print_summary(self):
        print("\n===== COLOUR TRANSITION SUMMARY =====")
        if not self.transitions:
            print("No transitions recorded.")
            return
        for t in self.transitions:
            print(f"[{t['timestamp']}] {t['from_state']} → {t['to_state']} "
                  f"| Duration: {t['duration']} sec")
        print("=====================================\n")

    def run(self):
        cap = cv2.VideoCapture(self.port)
        if not cap.isOpened():
            print("Error opening camera")
            return

        print("Running. Press Q to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # STEP 1 - detect vial using YOLO
            vial_roi, vial_pos, frame = self.detect_vial(frame)

            # STEP 2 - detect colour inside vial only
            if vial_roi is not None:
                state, pixel_counts = self.detect_colour_inside_vial(vial_roi)
                self.update_state(state)
            else:
                state        = 'UNKNOWN'
                pixel_counts = {}

            # STEP 3 - draw overlay
            frame = self.draw_overlay(frame, state, pixel_counts, vial_pos is not None)

            cv2.imshow('Vial Colour Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.print_summary()


if __name__ == "__main__":
    detector = ColourDetector(port=0)
    detector.run()