import os
from dotenv import load_dotenv
from flask import Flask, Response, render_template
import cv2
from inference_sdk import InferenceHTTPClient
import time
import json
import logging
from collections import deque
import threading
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")

if not API_KEY:
    logging.error("ROBOFLOW_API_KEY not found in environment variables")
    raise ValueError("ROBOFLOW_API_KEY is not set")

# Initialize Flask app
app = Flask(__name__)

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
)

# Initialize camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Cache for storing recent predictions
prediction_cache = deque(maxlen=10)  # Reduced cache size for quicker updates
last_inference_time = 0
INFERENCE_INTERVAL = 0.5  # Perform inference every 0.5 seconds for quicker updates
SKIP_FRAMES = 1  # Process every frame for smoother tracking

# Smoothing factor for bounding box movement
SMOOTHING_FACTOR = 0.7  # Increased for smoother transitions

# Motion detection parameters
motion_detector = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=25)

def smooth_bbox(prev_bbox, new_bbox):
    return {
        'x': prev_bbox['x'] * (1 - SMOOTHING_FACTOR) + new_bbox['x'] * SMOOTHING_FACTOR,
        'y': prev_bbox['y'] * (1 - SMOOTHING_FACTOR) + new_bbox['y'] * SMOOTHING_FACTOR,
        'width': prev_bbox['width'] * (1 - SMOOTHING_FACTOR) + new_bbox['width'] * SMOOTHING_FACTOR,
        'height': prev_bbox['height'] * (1 - SMOOTHING_FACTOR) + new_bbox['height'] * SMOOTHING_FACTOR
    }

def apply_predictions(frame, predictions):
    weapons_detected = False
    for prediction in predictions:
        if 'x' in prediction and 'y' in prediction and 'width' in prediction and 'height' in prediction:
            x = int(prediction['x'])
            y = int(prediction['y'])
            width = int(prediction['width'])
            height = int(prediction['height'])
            
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), 2)
            
            class_name = prediction.get('class', 'Unknown')
            confidence = prediction.get('confidence', 0)
            label = f"{class_name} {confidence:.2f}"
            
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            weapons_detected = True
    
    if weapons_detected:
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)
        alert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"ALERT: Weapon detected at {alert_time}"
        cv2.putText(frame, alert_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame

import tempfile

def perform_inference(frame):
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            cv2.imwrite(temp_file.name, frame)
            result = CLIENT.infer(temp_file.name, model_id="weapon-detection-3esci/1")
        
        if isinstance(result, dict) and 'predictions' in result:
            new_predictions = result['predictions']
            if prediction_cache:
                smoothed_predictions = []
                for new_pred in new_predictions:
                    matched = False
                    for old_pred in prediction_cache[-1]:
                        if new_pred.get('class') == old_pred.get('class'):
                            smoothed_pred = smooth_bbox(old_pred, new_pred)
                            smoothed_predictions.append(smoothed_pred)
                            matched = True
                            break
                    if not matched:
                        smoothed_predictions.append(new_pred)
                prediction_cache.append(smoothed_predictions)
            else:
                prediction_cache.append(new_predictions)
    except Exception as e:
        logging.error(f"Error during inference: {str(e)}")
    finally:
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

def generate_frames():
    global last_inference_time
    frame_count = 0
    while True:
        success, frame = camera.read()
        if not success:
            logging.error("Failed to capture frame from camera")
            break
        else:
            frame_count += 1
            if frame_count % SKIP_FRAMES != 0:
                continue

            current_time = time.time()
            
            # Perform motion detection
            motion_mask = motion_detector.apply(frame)
            motion_detected = np.sum(motion_mask) > motion_mask.size * 0.005  # Reduced threshold for more frequent detections
            
            # Perform inference if enough time has passed and motion is detected
            if current_time - last_inference_time >= INFERENCE_INTERVAL and motion_detected:
                threading.Thread(target=perform_inference, args=(frame,)).start()
                last_inference_time = current_time
            
            # Apply cached predictions to the frame
            if prediction_cache:
                frame = apply_predictions(frame, prediction_cache[-1])
            
            # Encode the frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(threaded=True)