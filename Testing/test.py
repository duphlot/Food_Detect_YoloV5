from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import cv2

app = FastAPI()

camera = cv2.VideoCapture(0)

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Camera Feed</title>
        </head>
        <body>
            <h1>Camera Feed</h1>
            <img src="/video_feed" width="640" height="480">
        </body>
    </html>
    """

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Xử lý ảnh nếu cần
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)