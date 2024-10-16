import warnings
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import torch
import pandas as pd
import os
import datetime

warnings.filterwarnings("ignore")

app = FastAPI()
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
camera = cv2.VideoCapture(0)
video_writer = None
food_data = pd.read_csv('data/food_data.csv')
# Phục vụ file tĩnh (CSS và JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

def generate_frames():
    global video_writer
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            results = model(frame)
            # Dùng copy() để tạo bản sao có thể thay đổi
            frame = results.render()[0].copy()

            detected_foods = results.names  # Lấy tên thực phẩm từ kết quả
            for food in detected_foods:
                expiry_date = estimate_expiry(food)  # Gọi hàm ước tính ngày hết hạn
                cv2.putText(frame, f'Expiry: {expiry_date}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

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
        return HTMLResponse(content=f.read())

@app.post('/start_recording')
async def start_recording():
    global video_writer
    if video_writer:
        raise HTTPException(status_code=400, detail="Recording is already in progress.")
    filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
    return {"message": "Recording started."}

@app.post('/stop_recording')
async def stop_recording():
    global video_writer
    if not video_writer:
        raise HTTPException(status_code=400, detail="No recording is in progress.")
    video_writer.release()
    video_writer = None
    return {"message": "Recording stopped."}

def estimate_expiry(food_name):
    if not isinstance(food_name, str):
        return "Unknown"
    food_info = food_data[food_data['name'].str.lower() == food_name.lower()]
    return food_info['expiry_date'].values[0] if not food_info.empty else "Unknown"

@app.get('/download_video/{filename}')
async def download_video(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Video not found.")
    return StreamingResponse(open(filename, 'rb'), media_type='video/x-msvideo')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
