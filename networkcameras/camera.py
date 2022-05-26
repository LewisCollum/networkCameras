import cv2
from collections import defaultdict


class Camera:
    cameras = {}
    users = defaultdict(lambda: 0)

    def __init__(self, source):
        self.source = source
        if self.source not in self.cameras:
            self.cameras[self.source] = self.getCamera(source)
        self.users[self.source] += 1
        print(f"Starting Camera {self.source}, user count is now {self.users[self.source]}")
        self.running = True

    def getCamera(self, source):
        camera = cv2.VideoCapture(source)
        if not camera.isOpened():
            raise RuntimeError(f"Cannot find camera {source}")
        return camera

    def stop(self):
        self.running = False

        if self.source in self.cameras:
            self.users[self.source] -= 1

        print(f"Releasing Camera {self.source}, user count is now {self.users[self.source]}")

        if self.users[self.source] == 0:
            self.cameras[self.source].release()
            del self.cameras[self.source]
            del self.users[self.source]

    def __del__(self):
        self.stop()

    def __next__(self):
        if self.running:
            success, frame = self.cameras[self.source].read()
            if success:
                frame = self.toImage(frame)
                response = self.toResponse(frame)
                return response

    def toImage(self, frame):
        return cv2.imencode(".jpg", frame)[1].tobytes()

    def toResponse(self, frame):
        return b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
