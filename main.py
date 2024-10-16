import logging
import warnings
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import torch
import pandas as pd
import os
import datetime
import json
import requests
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("starlette.routing").setLevel(logging.ERROR)

# Suppress FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

app = FastAPI()
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
camera = cv2.VideoCapture(0)
video_writer = None
food_data = pd.read_csv('data/food_data.csv')

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variable for video writer
video_writer = None

# Function to save detected food items to a JSON file
def save_detected_foods(detected_foods):
    with open('static/data/data.json', 'w') as f:
        json.dump(detected_foods, f)

detected_foods = []
detected_food_names = set()  # Set to keep track of detected food names

def generate_frames():
    global video_writer, detected_foods
    while True:
        success, frame = camera.read()
        if not success:
            print("Failed to capture frame")
            break
        else:
            results = model(frame)
            frame = results.render()[0].copy()
            
            for result in results.xyxy[0]:  # Iterate through detected objects
                confidence = result[4].item()  # Confidence score
                if confidence > 0.7:
                    food_name = results.names[int(result[5].item())]
                    if food_name not in detected_food_names:
                        expiry_date = estimate_expiry(food_name)
                        detected_foods.append({"name": food_name, "expiry": expiry_date})
                        detected_food_names.add(food_name)  # Add to set to track detected food names
                        cv2.putText(frame, f'{food_name} Expiry: {expiry_date}', (int(result[0]), int(result[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Save detected foods to JSON file
            save_detected_foods(detected_foods)
            ret, buffer = cv2.imencode('.jpg', frame)
            
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.post('/save_detected_foods')
async def save_detected_foods_endpoint(request: Request):
    detected_foods = await request.json()
    save_detected_foods(detected_foods)
    return {"message": "Detected foods saved successfully."}
    

@app.post('/save_detected_foods')
async def save_detected_foods_endpoint(request: Request):
    detected_foods = await request.json()
    save_detected_foods(detected_foods)
    return {"message": "Detected foods saved successfully."}

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/')
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())

@app.get('/recipes')
async def read_recipes():
    with open("recipes.html") as f:
        return HTMLResponse(content=f.read())
@app.get('/warehouse')
async def read_warehouse():
    with open("warehouse.html") as f:
        return HTMLResponse(content=f.read())
@app.get('/detect')
async def open_dectect():
    with open("detect.html") as f:
        return HTMLResponse(content=f.read())

@app.post('/start_recording')
async def start_recording():
    global video_writer, video_filename
    if video_writer:
        raise HTTPException(status_code=400, detail="Recording is already in progress.")
    video_filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (640, 480))
    return {"message": "Recording started."}

@app.post('/stop_recording')
async def stop_recording():
    global video_writer
    if not video_writer:
        raise HTTPException(status_code=400, detail="No recording is in progress.")
    video_writer.release()
    video_writer = None
    return {"message": "Recording stopped.", "filename": video_filename}

@app.get('/download_video/{filename}')
async def download_video(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Video not found.")
    return StreamingResponse(open(filename, 'rb'), media_type='video/mp4')

@app.get('/download_video/{filename}')
async def download_video(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Video not found.")
    return StreamingResponse(open(filename, 'rb'), media_type='video/x-msvideo')

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