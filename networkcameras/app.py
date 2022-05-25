import os
import cv2
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from collections import defaultdict
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

class Camera:
    cameras = {}
    users = defaultdict(lambda: 0)
    
    def __init__(self, source):
        self.source = source
        if self.source not in self.cameras:
            self.cameras[self.source] = cv2.VideoCapture(self.source)
        self.users[self.source] += 1
        print(f"Starting Camera {self.source}, user count is now {self.users[self.source]}")        
        self.running = True

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

    def __iter__(self):
        while self.running:
            success, frame = self.cameras[self.source].read()
            if success:
                frame = self.toImage(frame)
                response = self.toResponse(frame)
                yield response
            else:
                yield ""
            eventlet.sleep(0.1)

    def toImage(self, frame):
        return cv2.imencode('.jpg', frame)[1].tobytes()

    def toResponse(self, frame):
        return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'       

    
@app.route('/camera0')
def camera0():
    return Response(Camera(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera1')
def camera1():
    return Response(Camera(1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reboot')
def reboot():
    os.system("sudo reboot")

@app.route('/')
def index():    
    return render_template("index.html")


def main():
    socketio.run(app, host="0.0.0.0", port=5000)
    
if __name__ == '__main__':
    main()
