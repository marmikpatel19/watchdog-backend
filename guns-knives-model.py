# pip install inference-sdk
#pip install python-dotenv
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")
from inference_sdk import InferenceHTTPClient

#### Deploy Model #####
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
)
# tests on one image
result = CLIENT.infer("/Users/aahilali/Downloads/3954e1b9-8d58-4584-9ab8-21443a4b960d.jpg", model_id="weapon-detection-3esci/1")
#### Deploy Model #####

# Print the entire result
print("Full result:")
print(result)

# If you want to process the result further, you might do something like this:
if isinstance(result, dict) and 'predictions' in result:
    print("\nDetected objects:")
    for prediction in result['predictions']:
        print(f"Class: {prediction.get('class', 'Unknown')}")
        print(f"Confidence: {prediction.get('confidence', 'N/A')}")
        print(f"Bounding box: {prediction.get('bbox', 'N/A')}")
        print("---")