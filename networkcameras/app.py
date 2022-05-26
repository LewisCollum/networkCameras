import uvicorn
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from .camera import Camera

app = FastAPI()


@app.get("/camera/{index}")
def camera_stream(index: int):
    return StreamingResponse(Camera(index), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/camera/{index}/health", responses={404: {"model": str}})
def camera_availability(index: int):
    try:
        Camera(index)
        return f"Camera {index} available"
    except RuntimeError as error:
        raise HTTPException(status_code=404, detail=str(error))


def main():
    uvicorn.run("networkcameras.app:app", reload=True)
