import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from .camera import Camera

app = FastAPI()

def main():
    uvicorn.run("networkcameras.app:app", host="0.0.0.0", reload=True)


@app.get("/camera/{index}", responses={404: {"model": str}})
async def camera_stream(index: int):
    camera = findCamera(index)
    return StreamingResponse(camera.stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/camera/{index}/health", responses={404: {"model": str}})
def camera_availability(index: int):
    findCamera(index)
    return f"Camera {index} available"


def findCamera(index):
    try:
        return Camera(index)
    except RuntimeError as error:
        raise HTTPException(status_code=404, detail=str(error))
