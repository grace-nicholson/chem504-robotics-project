import cv2
import time
import threading

class Camera:
    def __init__(self, port: int, sample_name: str):
        self.finish: bool = False
        self.name = sample_name
        self.port = port
        self._thread = None
        self.current_frame = None  # shared frame
        self._lock = threading.Lock()

    def start_recording(self):
        self.finish = False
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        print("Recording started...")

    def stop_recording(self):
        self.finish = True
        if self._thread is not None:
            self._thread.join()
        print("Recording stopped.")

    def _record_loop(self):
        cap = cv2.VideoCapture(self.port)
        if not cap.isOpened():
            print("Error opening camera")
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.name + '.mp4', fourcc, 20.0, (640, 480))

        while not self.finish:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 0)
                with self._lock:
                    self.current_frame = frame.copy()  # save latest frame
                out.write(frame)

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def capture_image(self, filename):
        """Grab the latest frame from the recording thread instead of opening camera again."""
        with self._lock:
            if self.current_frame is not None:
                cv2.imwrite(filename, self.current_frame)
                print(f"Image saved: {filename}")
            else:
                print(f"No frame available for {filename}")