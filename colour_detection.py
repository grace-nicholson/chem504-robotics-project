import cv2
import numpy as np
import time
from datetime import datetime

class ColourDetector:
    def __init__(self, port=0):
        self.port = port
        self.current_state = None
        self.previous_state = None
        self.state_start_time = None
        self.transitions = []  # stores all state changes with durations

        # HSV colour ranges
        self.colour_ranges = {
            'GREEN': {
                'lower': np.array([35, 50, 50]),
                'upper': np.array([85, 255, 255])
            },
            'RED': [
                # red wraps around in HSV so needs two ranges
                {'lower': np.array([0, 50, 50]),   'upper': np.array([10, 255, 255])},
                {'lower': np.array([170, 50, 50]), 'upper': np.array([180, 255, 255])}
            ],
            'YELLOW': {
                'lower': np.array([20, 50, 50]),
                'upper': np.array([35, 255, 255])
            }
        }

    def detect_colour(self, frame):
        """Detect dominant colour in the centre region of the frame."""
        height, width = frame.shape[:2]

        # crop to centre region where vial will be
        cx, cy = width // 2, height // 2
        roi_size = 100
        roi = frame[cy - roi_size:cy + roi_size, cx - roi_size:cx + roi_size]

        # convert to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # count pixels for each colour
        pixel_counts = {}

        # green
        mask_green = cv2.inRange(hsv,
                                  self.colour_ranges['GREEN']['lower'],
                                  self.colour_ranges['GREEN']['upper'])
        pixel_counts['GREEN'] = cv2.countNonZero(mask_green)

        # red (two ranges combined)
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

        # find dominant colour
        dominant = max(pixel_counts, key=pixel_counts.get)

        # only return a state if enough pixels detected (avoid noise)
        if pixel_counts[dominant] > 500:
            return dominant, pixel_counts
        return 'UNKNOWN', pixel_counts

    def update_state(self, new_state):
        """Track state changes and record transition durations."""
        if new_state != self.current_state and new_state != 'UNKNOWN':
            # record how long previous state lasted
            if self.current_state is not None and self.state_start_time is not None:
                duration = time.time() - self.state_start_time
                transition = {
                    'from_state': self.current_state,
                    'to_state': new_state,
                    'duration': round(duration, 2),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                self.transitions.append(transition)
                print(f"[{transition['timestamp']}] {self.current_state} → {new_state} "
                      f"(lasted {duration:.2f} sec)")

            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_start_time = time.time()
            print(f"State changed to: {new_state}")

    def draw_overlay(self, frame, state, pixel_counts):
        """Draw colour detection overlay on frame."""
        height, width = frame.shape[:2]

        # draw ROI box in centre
        cx, cy = width // 2, height // 2
        roi_size = 100
        cv2.rectangle(frame,
                      (cx - roi_size, cy - roi_size),
                      (cx + roi_size, cy + roi_size),
                      (255, 255, 255), 2)

        # colour for the state label
        colour_map = {
            'GREEN':   (0, 255, 0),
            'RED':     (0, 0, 255),
            'YELLOW':  (0, 255, 255),
            'UNKNOWN': (128, 128, 128)
        }
        label_colour = colour_map.get(state, (255, 255, 255))

        # draw state text
        cv2.putText(frame, f"State: {state}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, label_colour, 2)

        # draw pixel counts
        y = 80
        for colour, count in pixel_counts.items():
            cv2.putText(frame, f"{colour}: {count}px", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour_map[colour], 1)
            y += 25

        # draw duration of current state
        if self.state_start_time:
            elapsed = time.time() - self.state_start_time
            cv2.putText(frame, f"Duration: {elapsed:.1f}s", (10, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame

    def print_summary(self):
        """Print full transition summary at the end."""
        print("\n===== COLOUR TRANSITION SUMMARY =====")
        if not self.transitions:
            print("No transitions recorded.")
            return
        for t in self.transitions:
            print(f"[{t['timestamp']}] {t['from_state']} → {t['to_state']} "
                  f"| Duration: {t['duration']} sec")
        print("=====================================\n")

    def run(self):
        """Run live colour detection from camera."""
        cap = cv2.VideoCapture(self.port)
        if not cap.isOpened():
            print("Error opening camera")
            return

        print("Colour detection started. Press Q to stop.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            state, pixel_counts = self.detect_colour(frame)
            self.update_state(state)
            frame = self.draw_overlay(frame, state, pixel_counts)

            cv2.imshow('Colour Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.print_summary()


if __name__ == "__main__":
    detector = ColourDetector(port=0)
    detector.run()




#to put in the moving_vial_2
from colour_detection import ColourDetector
import threading

# in main() after cam setup
detector = ColourDetector(port=0)
detection_thread = threading.Thread(target=detector.run, daemon=True)
detection_thread.start()

# ... all robot movements ...

# in finally block
finally:
    cam.stop_recording()
    stirrer.stop_stirring()
    detector.print_summary()