import cv2
import numpy as np
import os
import time

def zoom_on_face(image_path, zoom_factor=2.5): # change this 
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read the image at {image_path}")

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load the pre-trained face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print("No faces detected in the image")
        return img

    # Get the first detected face
    (x, y, w, h) = faces[0]

    # Calculate the center of the face
    center_x, center_y = x + w // 2, y + h // 2

    # Calculate new dimensions
    new_w, new_h = int(img.shape[1] / zoom_factor), int(img.shape[0] / zoom_factor)

    # Calculate new top-left corner
    new_x = max(center_x - new_w // 2, 0)
    new_y = max(center_y - new_h // 2, 0)

    # Ensure the new region doesn't exceed image boundaries
    new_x = min(new_x, img.shape[1] - new_w)
    new_y = min(new_y, img.shape[0] - new_h)

    # Crop the image
    face_zoom = img[new_y:new_y+new_h, new_x:new_x+new_w]

    # Resize the cropped image to match the original image size
    face_zoom = cv2.resize(face_zoom, (img.shape[1], img.shape[0]))

    return face_zoom

def save_image_to_folder(image, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate a unique filename using timestamp
    timestamp = int(time.time() * 1000)
    filename = f"zoomed_face_{timestamp}.jpg"
    
    # Full path for the output image
    output_path = os.path.join(output_folder, filename)
    
    # Save the image
    result = cv2.imwrite(output_path, image)
    
    if result:
        return output_path
    else:
        raise IOError(f"Failed to save the image to {output_path}")

# Example usage
input_image = "/Users/aahilali/Desktop/watchdog-backend/screenshots/weapon_detected_06d3e254-ca74-4d06-a2c3-c356c9a0ec87.jpg"
output_folder = "/Users/aahilali/Desktop/watchdog-backend/zoomed _in"

try:
    zoomed_face = zoom_on_face(input_image)
    saved_path = save_image_to_folder(zoomed_face, output_folder)
    print(f"Zoomed face saved to {saved_path}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
    print("Please check that the input image exists and the output folder is accessible.")