import cv2
import dlib

def zoom_on_face(image_path, zoom_factor=1.5):
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read the image")

    # Initialize dlib's face detector
    detector = dlib.get_frontal_face_detector()

    # Detect faces in the image
    faces = detector(img)

    if len(faces) == 0:
        print("No faces detected in the image")
        return img

    # Get the first detected face
    face = faces[0]

    # Get the face boundaries
    x, y = face.left(), face.top()
    w, h = face.width(), face.height()

    # Calculate the center of the face
    center_x, center_y = x + w // 2, y + h // 2

    # Calculate new dimensions
    new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)

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

# Example usage
input_image = "/Users/aahilali/Desktop/watchdog-backend/screenshots/weapon_detected_0b68b98e-8605-48ca-96e0-74ff61bcd754.jpg"
output_image = "/Users/aahilali/Desktop/watchdog-backend/zoomed _in"

zoomed_face = zoom_on_face(input_image)
cv2.imwrite(output_image, zoomed_face)
print(f"Zoomed face saved to {output_image}")