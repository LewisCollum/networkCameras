import cv2
from collections import defaultdict
import asyncio


class Camera:
    cameras = {}
    users = defaultdict(lambda: 0)

    def __init__(self, source):
        self.source = source
        if not self.cameraIsOpened():
            self.registerCamera()
            print(f"Registered Camera {self.source}")
        self.registerUser()
        print(f"Registered User for Camera {self.source}, count is now {self.userCount()}.")

    def __del__(self):
        if self.cameraIsOpened():
            self.dropUser()
            print(f"Dropped User for Camera {self.source}, count is now {self.userCount()}.")

            if self.noUsers():
                self.dropCamera()
                print(f"Dropped Camera {self.source} since there are no users.")

    async def stream(self):
        try:
            while True:
                yield self.readAsResponse()
                await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            pass


    def readAsResponse(self):
        success, frame = self.cameras[self.source].read()
        return self.frameToResponse(frame) if success else ""

    def frameToResponse(self, frame):
        image = self.frameToImage(frame)
        return self.imageToResponse(image)

    def frameToImage(self, frame):
        return cv2.imencode(".jpg", frame)[1].tobytes()

    def imageToResponse(self, frame):
        return b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    def registerCamera(self):
        self.cameras[self.source] = self.getCamera()

    def getCamera(self):
        camera = cv2.VideoCapture(self.source)
        if not camera.isOpened():
            raise RuntimeError(f"Cannot find Camera {self.source}")
        return camera

    def registerUser(self):
        self.users[self.source] += 1

    def dropUser(self):
        self.users[self.source] -= 1

    def userCount(self):
        return self.users[self.source]

    def cameraIsOpened(self):
        return self.source in self.cameras

    def noUsers(self):
        return self.users[self.source] == 0

    def dropCamera(self):
        self.cameras[self.source].release()
        del self.cameras[self.source]
        del self.users[self.source]

