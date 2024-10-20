from uagents import Agent, Context
from flask import Flask, request, jsonify
from flask_cors import CORS
import pyautogui
import base64
from io import BytesIO
import threading
import time
import geocoder
import os

app = Flask(__name__)
CORS(app)

tom = Agent(name="tom", seed="used by masta")
jerry = Agent(name="jerry", seed="helper")

device_coordinates = {"latitude": 0, "longitude": 0}
screenshot_folder = "weapon_screenshots"

if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    global device_coordinates
    data = request.json
    device_coordinates = {
        "latitude": data['latitude'],
        "longitude": data['longitude']
    }
    return jsonify({"status": "success"})

@app.route('/weapon_detected', methods=['POST'])
def weapon_detected():
    screenshot = pyautogui.screenshot()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"weapon_detected_{timestamp}.png"
    filepath = os.path.join(screenshot_folder, filename)
    screenshot.save(filepath)
    # Notify Jerry about the weapon detection
    jerry.send(jerry.address, {"type": "weapon_detected", "filename": filename})
    return jsonify({"status": "success", "filename": filename})

@tom.on_interval(period=2.0)
async def track_coordinates(ctx: Context):
    g = geocoder.ip('me')
    if g.ok:
        actual_coordinates = {"latitude": g.lat, "longitude": g.lng}
        ctx.logger.info(f"Actual device coordinates: {actual_coordinates}")
    else:
        ctx.logger.info("Failed to get actual coordinates")

@jerry.on_interval(period=2.0)
async def search_for_weapon_or_suspect(ctx: Context):
    ctx.logger.info("Searching for weapon or suspect")

# @jerry.on_message()
# async def handle_weapon_detection(ctx: Context, sender: str, msg: dict):
#     if msg.get("type") == "weapon_detected":
#         filename = msg.get('filename')
#         ctx.logger.info(f"Weapon detected! Screenshot saved as {filename}")

def run_agents():
    # tom.run()
    jerry.run()

if __name__ == "__main__":
    threading.Thread(target=run_agents, daemon=True).start()
    app.run(port=5000)