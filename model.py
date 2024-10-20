import cv2
from inference_sdk import InferenceHTTPClient
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the Roboflow client
CLIENT = InferenceHTTPClient(
    api_url=os.getenv("ROBOFLOW_API_URL"),
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

def process_video(input_path, output_path):
    # Open the video file
    video = cv2.VideoCapture(input_path)
    
    if not video.isOpened():
        print(f"Error: Could not open video file at {input_path}")
        return
    
    # Get video properties
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        # Process every 5th frame to reduce API calls and processing time
        # if frame_count % 5 == 0:
        # Save the frame as a temporary image
        temp_image_path = "temp_frame.jpg"
        cv2.imwrite(temp_image_path, frame)
        
        # Run inference on the frame
        result = CLIENT.infer(temp_image_path, model_id="shell-lguwm/1")
        
        # Draw bounding boxes
        for prediction in result['predictions']:
            x, y, w, h = prediction['x'], prediction['y'], prediction['width'], prediction['height']
            x1, y1 = int(x - w/2), int(y - h/2)
            x2, y2 = int(x + w/2), int(y + h/2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{prediction['class']} {prediction['confidence']:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Remove temporary image
        os.remove(temp_image_path)
        
        # Write the frame
        out.write(frame)
        
        frame_count += 1
        
        # Display progress
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames")
    
    # Release video objects
    video.release()
    out.release()
    
    print("Video processing complete")

# Use raw string for file path
input_path = r"...\watchdog-backend\testing-videos\small-gun.mp4" # fill it out
output_path = "testing-videos\output_gun_detection.mp4" # fill it out

# Check if input file exists
if not os.path.exists(input_path):
    print(f"Error: Input file not found at {input_path}")
else:
    process_video(input_path, output_path)