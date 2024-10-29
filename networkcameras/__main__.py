import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from .camera import Camera

app = FastAPI()

@app.get("/reboot")
def reboot():
    os.system("sudo reboot")

@app.get("/camera/{index}", responses={404: {"model": str}})
async def camera_stream(index: int):
    camera = findCamera(index)
    return StreamingResponse(camera.stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/camera/{index}/health", responses={404: {"model": dict}})
def camera_availability(index: int):
    camera = findCamera(index)
    return {
        "index": index,
        "available": True,
        "user_count": camera.userCount() - 1
    }

@app.get("/cameras")
def camera_list():
    available = []
    for i in range(10):
        try:
            camera = Camera(i)
            available.append({
                "index": i,
                "user_count": camera.userCount() - 1
            })
        except RuntimeError: pass
    return available

@app.delete("/cameras")
def clear_cameras():
    Camera.clear()
    return "Cleared all cameras and users"


def findCamera(index):
    try:
        return Camera(index)
    except RuntimeError:
        raise HTTPException(
            status_code=404,
            detail={
                "index": index,
                "available": False
            })


def main():
    uvicorn.run("networkcameras.__main__:app", host="0.0.0.0", reload=True)

if __name__=="__main__":
    main()
