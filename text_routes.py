from flask import Flask, request, jsonify
from etext import send_mms_via_email
import os
from dotenv import load_dotenv
import requests
import tempfile

load_dotenv()

app = Flask(__name__)

@app.route('/send-mms', methods=['POST'])
def send_mms():
    data = request.json
    phone_number = data.get('phone_number')
    last_seen = data.get('last_seen')
    suspect_description = data.get('suspect_description')
    weapon = data.get('weapon')
    image_url = data.get('image_url')

    message = (
        f"ALERT: Active {weapon} reported in the building. "
        f"Last seen: {last_seen}. "
        f"Suspect description: {suspect_description}. "
        "Please find the nearest safe area and secure yourself immediately. "
        "Avoid open areas and remain silent. Wait for further instructions from authorities."
    )
    mime_maintype = "image"
    mime_subtype = "png"
    provider = "AT&T"

    sender_credentials = (
        os.getenv("SMTPLIB_SENDER_EMAIL"),
        os.getenv("SMTPLIB_SENDER_CREDENTIALS")
    )

    # Download the image to a temporary file
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(response.content)
            file_path = temp_file.name

        send_mms_via_email(
            phone_number,
            message,
            file_path,
            mime_maintype,
            mime_subtype,
            provider,
            sender_credentials
        )

        return jsonify({"status": "success", "message": "MMS sent successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        # Delete the temporary file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(debug=True)
