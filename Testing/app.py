import warnings

# Tắt tất cả các cảnh báo
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import torch
import os
import datetime

app = FastAPI()

# Tải YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Khởi động camera
camera = cv2.VideoCapture(0)

# Biến toàn cục để lưu video
video_writer = None

def generate_frames():
    global video_writer
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Sử dụng YOLOv5 để phát hiện đối tượng
            results = model(frame)
            frame = results.render()[0]

            # Ghi nhận video
            if video_writer is not None:
                video_writer.write(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/')
async def read_root():
    with open("index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post('/start_recording')
async def start_recording():
    global video_writer
    if video_writer is not None:
        raise HTTPException(status_code=400, detail="Recording is already in progress.")
    
    # Tạo tên file video với dấu thời gian
    filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    
    return {"message": "Recording started."}

@app.post('/stop_recording')
async def stop_recording():
    global video_writer
    if video_writer is None:
        raise HTTPException(status_code=400, detail="No recording is in progress.")
    
    video_writer.release()
    video_writer = None
    
    return {"message": "Recording stopped."}

@app.get('/download_video/{filename}')
async def download_video(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Video not found.")
    
    return StreamingResponse(open(filename, 'rb'), media_type='video/x-msvideo')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
