import threading
import time
import os
import cv2
import numpy as np
from modes import auto_straighten, manual_straighten

class FolderWorker(threading.Thread):
    def __init__(self, in_folder, out_folder, mode="auto", manual_angle=0.0):
        super().__init__(daemon=True)
        self.in_folder = in_folder
        self.out_folder = out_folder
        self.mode = mode
        self.manual_angle = manual_angle
        self.stop_event = threading.Event()
        self.done = set()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            for f in os.listdir(self.in_folder):
                if self.stop_event.is_set():
                    break

                if not f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    continue

                src = os.path.join(self.in_folder, f)
                if src in self.done:
                    continue

                img = cv2.imdecode(np.fromfile(src, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue

                if self.mode == "auto":
                    out, _ = auto_straighten(img)
                else:
                    out, _ = manual_straighten(img, self.manual_angle)

                os.makedirs(self.out_folder, exist_ok=True)
                name = os.path.splitext(f)[0]
                dst = os.path.join(self.out_folder, f"{name}_straight.png")
                _, buf = cv2.imencode(".png", out)
                buf.tofile(dst)

                self.done.add(src)

            time.sleep(1)
