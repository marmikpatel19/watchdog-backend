# import os
# import time
# import subprocess
# import shutil
# import base64
# import requests
# from io import BytesIO
# from PIL import Image
# from dotenv import load_dotenv
# from deepgram import DeepgramClient, SpeakOptions
# from flask import Flask, render_template, request, jsonify
# from uagents import Agent, Model, Context
# load_dotenv()

# app = Flask(__name__)

# SYSTEM_PROMPT = """
# You are an AI simulating a highly trained police officer responding to emergency situations. Your primary goals are to ensure public safety, de-escalate dangerous situations, and provide clear, authoritative instructions. Respond as if you are directly communicating with someone in an emergency situation. Be concise, and ask followup questions such as description of person, gun, location, etc.
# """

# with open('system_prompt.txt', 'w') as file:
#     file.write(SYSTEM_PROMPT)

# class LanguageModelProcessor:
#     def __init__(self):
#         self.api_url = "https://api.hyperbolic.xyz/v1/chat/completions"
#         self.api_key = os.getenv("HYPERBOLIC_API_KEY")
#         if not self.api_key:
#             raise ValueError("HYPERBOLIC_API_KEY not found in environment variables")
#         self.headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}",
#         }
#         self.conversation_history = []

#     def load_system_prompt(self):
#         try:
#             with open('system_prompt.txt', 'r') as file:
#                 return file.read().strip()
#         except FileNotFoundError:
#             print("Warning: system_prompt.txt not found. Using default prompt.")
#             return SYSTEM_PROMPT

#     def process(self, text):
#         system_prompt = self.load_system_prompt()
#         self.conversation_history.append({"role": "system", "content": system_prompt})
#         self.conversation_history.append({"role": "user", "content": text})

#         payload = {
#             "messages": self.conversation_history,
#             "model": "meta-llama/Llama-3.2-90B-Vision-Instruct",
#             "max_tokens": 2048,
#             "temperature": 0.7,
#             "top_p": 0.9,
#         }

#         start_time = time.time()
#         response = requests.post(self.api_url, headers=self.headers, json=payload)
#         end_time = time.time()

#         if response.status_code == 200:
#             response_text = response.json()['choices'][0]['message']['content']
#             self.conversation_history.append({"role": "assistant", "content": response_text})
#         else:
#             response_text = f"Error: API request failed with status code {response.status_code}"

#         elapsed_time = int((end_time - start_time) * 1000)
#         print(f"Police Officer AI ({elapsed_time}ms): {response_text}")
#         return response_text

# class TextToSpeech:
#     def __init__(self):
#         self.DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
#         if not self.DG_API_KEY:
#             raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
#         self.MODEL_NAME = "aura-orion-en"
#         self.deepgram = DeepgramClient(api_key=self.DG_API_KEY)

#     @staticmethod
#     def is_installed(lib_name: str) -> bool:
#         return shutil.which(lib_name) is not None

#     def speak(self, text):
#         if not self.is_installed("ffplay"):
#             print("Error: ffplay not found. Please install ffmpeg.")
#             return

#         output_file = "output.wav"
#         options = SpeakOptions(
#             model=self.MODEL_NAME,
#             encoding="linear16",
#             container="wav"
#         )

#         start_time = time.time()

#         try:
#             response = self.deepgram.speak.v("1").save(output_file, {"text": text}, options)
            
#             first_byte_time = time.time()
#             ttfb = int((first_byte_time - start_time) * 1000)
#             print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")

#             print(f"Audio saved to {output_file}")
#             print(response.to_json(indent=4))

#             # Play the audio file
#             subprocess.run(["ffplay", "-autoexit", "-nodisp", output_file],
#                            stdout=subprocess.DEVNULL,
#                            stderr=subprocess.DEVNULL,
#                            check=True)

#             print("Audio playback completed")

#         except Exception as e:
#             print(f"Error in Deepgram API request: {e}")

# class FetchAIAgent:
#     def __init__(self):
#         self.agent = Agent(name="emergency_response_agent")
#         self.conversation_context = []

#     def update_context(self, role, content):
#         self.conversation_context.append({"role": role, "content": content})

#     @staticmethod
#     async def handle_message(ctx: Context, message: Model):
#         # This method will be called when the agent receives a message
#         response = ctx.agent.storage.get("last_response", "No response yet.")
#         await ctx.send(message.sender, response)

#     def process(self, input_text):
#         self.update_context("user", input_text)
        
#         # Use the agent's storage to retain information
#         self.agent.storage.set("last_input", input_text)
        
#         # In a real-world scenario, you might want to implement more complex
#         # logic here, possibly interacting with other agents or services
        
#         return self.agent.storage.get("last_input", "No input received yet.")

# class ConversationManager:
#     def __init__(self):
#         self.llm = LanguageModelProcessor()
#         self.fetch_agent = FetchAIAgent()
#         try:
#             self.tts = TextToSpeech()
#         except ValueError as e:
#             print(f"Error initializing TextToSpeech: {e}")
#             self.tts = None

#     def process_input(self, input_text):
#         print(f"Civilian: {input_text}")
        
#         # Process with FetchAI agent
#         fetch_response = self.fetch_agent.process(input_text)
#         print(f"FetchAI Agent processed: {fetch_response}")
        
#         # Process with LLM
#         llm_response = self.llm.process(input_text)
        
#         # Update FetchAI agent context
#         self.fetch_agent.update_context("assistant", llm_response)
        
#         if self.tts:
#             try:
#                 self.tts.speak(llm_response)
#             except Exception as e:
#                 print(f"Error in text-to-speech: {e}")
#                 print("Continuing with text-only response.")
#         else:
#             print("Text-to-Speech is not available. Displaying text response only.")
        
#         return llm_response

#     def get_conversation_history(self):
#         return self.fetch_agent.conversation_context

# conversation_manager = None

# def initialize_conversation():
#     global conversation_manager
#     if conversation_manager is None:
#         print("Initializing ConversationManager...")
#         conversation_manager = ConversationManager()
        
#         print("Processing predefined inputs...")
#         predefined_inputs = [
#             "Help, active shooter!",
#             "The person is wearing a black tee and has black hair. He is on the 4th floor, he has a revolver, there are no injuries.",
#         ]
#         for input_text in predefined_inputs:
#             print(f"Processing: {input_text}")
#             conversation_manager.process_input(input_text)
#         print("Predefined inputs processed.")

# @app.before_request
# def before_request():
#     initialize_conversation()

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_input = request.json['message']
#     response = conversation_manager.process_input(user_input)
#     return jsonify({'response': response})

# @app.route('/history')
# def history():
#     return jsonify(conversation_manager.get_conversation_history())

# if __name__ == "__main__":
#     print("Starting the Emergency Response System...")
#     print("Starting Flask server...")
#     app.run(debug=True, use_reloader=False)
#     print("Flask server has shut down.")

# Version 2 # Speech-to-Speech
# import os
# import time
# import subprocess
# import shutil
# import base64
# import requests
# import asyncio
# import websockets
# import json
# import ssl
# import certifi
# import pyaudio
# import wave
# from io import BytesIO
# from PIL import Image
# from dotenv import load_dotenv
# from deepgram import DeepgramClient, SpeakOptions
# from flask import Flask, render_template, request, jsonify, Response
# from uagents import Agent, Model, Context
# load_dotenv()

# app = Flask(__name__)

# SYSTEM_PROMPT = """
# You are an AI simulating a highly trained police officer responding to emergency situations. Your primary goals are to ensure public safety, de-escalate dangerous situations, and provide clear, authoritative instructions. Respond as if you are directly communicating with someone in an emergency situation. Be concise, and ask followup questions such as description of person, gun, location, etc.
# """

# with open('system_prompt.txt', 'w') as file:
#     file.write(SYSTEM_PROMPT)

# class LanguageModelProcessor:
#     def __init__(self):
#         self.api_url = "https://api.hyperbolic.xyz/v1/chat/completions"
#         self.api_key = os.getenv("HYPERBOLIC_API_KEY")
#         if not self.api_key:
#             raise ValueError("HYPERBOLIC_API_KEY not found in environment variables")
#         self.headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {self.api_key}",
#         }
#         self.conversation_history = []

#     def load_system_prompt(self):
#         try:
#             with open('system_prompt.txt', 'r') as file:
#                 return file.read().strip()
#         except FileNotFoundError:
#             print("Warning: system_prompt.txt not found. Using default prompt.")
#             return SYSTEM_PROMPT

#     def process(self, text):
#         system_prompt = self.load_system_prompt()
#         self.conversation_history.append({"role": "system", "content": system_prompt})
#         self.conversation_history.append({"role": "user", "content": text})

#         payload = {
#             "messages": self.conversation_history,
#             "model": "meta-llama/Llama-3.2-90B-Vision-Instruct",
#             "max_tokens": 2048,
#             "temperature": 0.7,
#             "top_p": 0.9,
#         }

#         start_time = time.time()
#         response = requests.post(self.api_url, headers=self.headers, json=payload)
#         end_time = time.time()

#         if response.status_code == 200:
#             response_text = response.json()['choices'][0]['message']['content']
#             self.conversation_history.append({"role": "assistant", "content": response_text})
#         else:
#             response_text = f"Error: API request failed with status code {response.status_code}"

#         elapsed_time = int((end_time - start_time) * 1000)
#         print(f"Police Officer AI ({elapsed_time}ms): {response_text}")
#         return response_text

# class TextToSpeech:
#     def __init__(self):
#         self.DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
#         if not self.DG_API_KEY:
#             raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
#         self.MODEL_NAME = "aura-orion-en"
#         self.deepgram = DeepgramClient(api_key=self.DG_API_KEY)

#     @staticmethod
#     def is_installed(lib_name: str) -> bool:
#         return shutil.which(lib_name) is not None

#     def speak(self, text):
#         if not self.is_installed("ffplay"):
#             print("Error: ffplay not found. Please install ffmpeg.")
#             return

#         output_file = "output.wav"
#         options = SpeakOptions(
#             model=self.MODEL_NAME,
#             encoding="linear16",
#             container="wav"
#         )

#         start_time = time.time()

#         try:
#             response = self.deepgram.speak.v("1").save(output_file, {"text": text}, options)
            
#             first_byte_time = time.time()
#             ttfb = int((first_byte_time - start_time) * 1000)
#             print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")

#             print(f"Audio saved to {output_file}")
#             print(response.to_json(indent=4))

#             # Play the audio file
#             subprocess.run(["ffplay", "-autoexit", "-nodisp", output_file],
#                            stdout=subprocess.DEVNULL,
#                            stderr=subprocess.DEVNULL,
#                            check=True)

#             print("Audio playback completed")

#         except Exception as e:
#             print(f"Error in Deepgram API request: {e}")

# class FetchAIAgent:
#     def __init__(self):
#         self.agent = Agent(name="emergency_response_agent")
#         self.conversation_context = []

#     def update_context(self, role, content):
#         self.conversation_context.append({"role": role, "content": content})

#     @staticmethod
#     async def handle_message(ctx: Context, message: Model):
#         # This method will be called when the agent receives a message
#         response = ctx.agent.storage.get("last_response") or "No response yet."
#         await ctx.send(message.sender, response)

#     def process(self, input_text):
#         self.update_context("user", input_text)
        
#         # Use the agent's storage to retain information
#         self.agent.storage.set("last_input", input_text)
        
#         # In a real-world scenario, you might want to implement more complex
#         # logic here, possibly interacting with other agents or services
        
#         return self.agent.storage.get("last_input") or "No input received yet."

# class DeepgramVoiceAgent:
#     def __init__(self):
#         self.api_key = os.getenv("DEEPGRAM_API_KEY")
#         if not self.api_key:
#             raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
#         self.websocket_url = "wss://agent.deepgram.com/agent"

#     async def start_conversation(self):
#         ssl_context = ssl.create_default_context(cafile=certifi.where())
        
#         async with websockets.connect(
#             self.websocket_url,
#             extra_headers={"Authorization": f"Token {self.api_key}"},
#             ssl=ssl_context
#         ) as websocket:
#             # Send SettingsConfiguration message
#             settings = {
#                 "type": "SettingsConfiguration",
#                 "audio": {
#                     "input": {
#                         "encoding": "linear16",
#                         "sample_rate": 16000
#                     },
#                     "output": {
#                         "encoding": "mp3",
#                         "sample_rate": 24000
#                     }
#                 },
#                 "agent": {
#                     "listen": {
#                         "model": "nova-2"
#                     },
#                     "think": {
#                         "provider": {
#                             "type": "openai"
#                         },
#                         "model": "gpt-3.5-turbo",
#                         "instructions": SYSTEM_PROMPT
#                     },
#                     "speak": {
#                         "model": "aura-asteria-en"
#                     }
#                 }
#             }
#             await websocket.send(json.dumps(settings))

#             # Start audio streaming (you'll need to implement this)
#             await self.stream_audio(websocket)

#     async def stream_audio(self, websocket):
#         # This is a placeholder. You'll need to implement actual audio streaming.
#         # For example, you might use PyAudio to capture microphone input.
#         while True:
#             # Capture audio chunk
#             audio_chunk = self.capture_audio()
            
#             # Send audio chunk
#             await websocket.send(audio_chunk)
            
#             # Receive and process server messages
#             response = await websocket.recv()
#             await self.process_server_message(response)

#     def capture_audio(self):
#         # Placeholder for audio capture
#         # You'll need to implement this using a library like PyAudio
#         return b''  # Return captured audio chunk

#     async def process_server_message(self, message):
#         # Parse the message and handle different types
#         msg = json.loads(message)
#         if msg['type'] == 'Speech':
#             # Handle speech output
#             print(f"Agent: {msg['text']}")
#             # You might want to play this audio
#         elif msg['type'] == 'UserStartedSpeaking':
#             # Handle user started speaking event
#             print("User started speaking")
#         # Add more handlers for other message types as needed

# class ConversationManager:
#     def __init__(self):
#         self.llm = LanguageModelProcessor()
#         self.fetch_agent = FetchAIAgent()
#         self.voice_agent = DeepgramVoiceAgent()
#         try:
#             self.tts = TextToSpeech()
#         except ValueError as e:
#             print(f"Error initializing TextToSpeech: {e}")
#             self.tts = None

#     def process_input(self, input_text):
#         print(f"Civilian: {input_text}")
        
#         # Process with FetchAI agent
#         fetch_response = self.fetch_agent.process(input_text)
#         print(f"FetchAI Agent processed: {fetch_response}")
        
#         # Process with LLM
#         llm_response = self.llm.process(input_text)
        
#         # Update FetchAI agent context
#         self.fetch_agent.update_context("assistant", llm_response)
        
#         if self.tts:
#             try:
#                 self.tts.speak(llm_response)
#             except Exception as e:
#                 print(f"Error in text-to-speech: {e}")
#                 print("Continuing with text-only response.")
#         else:
#             print("Text-to-Speech is not available. Displaying text response only.")
        
#         return llm_response

#     def get_conversation_history(self):
#         return self.fetch_agent.conversation_context

#     async def start_voice_conversation(self):
#         await self.voice_agent.start_conversation()

# conversation_manager = None

# def initialize_conversation():
#     global conversation_manager
#     if conversation_manager is None:
#         print("Initializing ConversationManager...")
#         conversation_manager = ConversationManager()
        
#         print("Processing predefined inputs...")
#         predefined_inputs = [
#             "Help, active shooter!",
#             "The person is wearing a black tee and has black hair. He is on the 4th floor, he has a revolver, there are no injuries.",
#         ]
#         for input_text in predefined_inputs:
#             print(f"Processing: {input_text}")
#             conversation_manager.process_input(input_text)
#         print("Predefined inputs processed.")

# @app.before_request
# def before_request():
#     initialize_conversation()

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_input = request.json['message']
#     response = conversation_manager.process_input(user_input)
#     return jsonify({'response': response})

# @app.route('/voice_input', methods=['POST'])
# def voice_input():
#     # This function will handle voice input from the client
#     audio_data = request.files['audio'].read()
    
#     # Save the audio data to a temporary file
#     with wave.open("temp_audio.wav", "wb") as wf:
#         wf.setnchannels(1)
#         wf.setsampwidth(2)
#         wf.setframerate(16000)
#         wf.writeframes(audio_data)
    
#     # Process the audio (you'll need to implement this)
#     text = process_audio_to_text("temp_audio.wav")
    
#     # Use the existing process_input method
#     response = conversation_manager.process_input(text)
    
#     return jsonify({'response': response})

# @app.route('/start_voice_stream')
# def start_voice_stream():
#     def generate():
#         p = pyaudio.PyAudio()
#         stream = p.open(format=pyaudio.paInt16,
#                         channels=1,
#                         rate=16000,
#                         input=True,
#                         frames_per_buffer=1024)
        
#         while True:
#             data = stream.read(1024)
#             yield (b'--frame\r\n'
#                    b'Content-Type: audio/wav\r\n\r\n' + data + b'\r\n')
    
#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/history')
# def history():
#     return jsonify(conversation_manager.get_conversation_history())

# def process_audio_to_text(audio_file):
#     # Placeholder function for audio-to-text conversion
#     # You'll need to implement this using a speech recognition library
#     # or the Deepgram API for speech-to-text
#     return "Placeholder text from audio"

# if __name__ == "__main__":
#     print("Starting the Emergency Response System...")
#     initialize_conversation()  # Initialize conversation manager before starting threads
    
#     # Start the voice conversation in a separate thread
#     import threading
#     voice_thread = threading.Thread(target=asyncio.run, args=(conversation_manager.start_voice_conversation(),))
#     voice_thread.start()
    
#     print("Starting Flask server...")
#     app.run(debug=True, use_reloader=False)
#     print("Flask server has shut down.")

# Version 2 # Speech-to-Speech
import os
import time
import subprocess
import shutil
import base64
import requests
import asyncio
import websockets
import json
import ssl
import certifi
import pyaudio
import wave
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from deepgram import DeepgramClient, SpeakOptions
from flask import Flask, render_template, request, jsonify, Response
from uagents import Agent, Model, Context

load_dotenv()

app = Flask(__name__)

SYSTEM_PROMPT = """
You are an AI simulating a highly trained police officer responding to emergency situations. Your primary goals are to ensure public safety, de-escalate dangerous situations, and provide clear, authoritative instructions. Respond as if you are directly communicating with someone in an emergency situation. Be concise, and ask followup questions such as description of person, gun, location, etc.
"""

with open('system_prompt.txt', 'w') as file:
    file.write(SYSTEM_PROMPT)

class LanguageModelProcessor:
    def __init__(self):
        self.api_url = "https://api.hyperbolic.xyz/v1/chat/completions"
        self.api_key = os.getenv("HYPERBOLIC_API_KEY")
        if not self.api_key:
            raise ValueError("HYPERBOLIC_API_KEY not found in environment variables")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.conversation_history = []

    def load_system_prompt(self):
        try:
            with open('system_prompt.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Warning: system_prompt.txt not found. Using default prompt.")
            return SYSTEM_PROMPT

    def process(self, text):
        system_prompt = self.load_system_prompt()
        self.conversation_history.append({"role": "system", "content": system_prompt})
        self.conversation_history.append({"role": "user", "content": text})

        payload = {
            "messages": self.conversation_history,
            "model": "meta-llama/Llama-3.2-90B-Vision-Instruct",
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        start_time = time.time()
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        end_time = time.time()

        if response.status_code == 200:
            response_text = response.json()['choices'][0]['message']['content']
            self.conversation_history.append({"role": "assistant", "content": response_text})
        else:
            response_text = f"Error: API request failed with status code {response.status_code}"

        elapsed_time = int((end_time - start_time) * 1000)
        print(f"Police Officer AI ({elapsed_time}ms): {response_text}")
        return response_text

class TextToSpeech:
    def __init__(self):
        self.DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
        if not self.DG_API_KEY:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
        self.MODEL_NAME = "aura-orion-en"
        self.deepgram = DeepgramClient(api_key=self.DG_API_KEY)

    @staticmethod
    def is_installed(lib_name: str) -> bool:
        return shutil.which(lib_name) is not None

    def speak(self, text):
        if not self.is_installed("ffplay"):
            print("Error: ffplay not found. Please install ffmpeg.")
            return

        output_file = "output.wav"
        options = SpeakOptions(
            model=self.MODEL_NAME,
            encoding="linear16",
            container="wav"
        )

        start_time = time.time()

        try:
            response = self.deepgram.speak.v("1").save(output_file, {"text": text}, options)
            
            first_byte_time = time.time()
            ttfb = int((first_byte_time - start_time) * 1000)
            print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")

            print(f"Audio saved to {output_file}")
            print(response.to_json(indent=4))

            # Play the audio file
            subprocess.run(["ffplay", "-autoexit", "-nodisp", output_file],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           check=True)

            print("Audio playback completed")

        except Exception as e:
            print(f"Error in Deepgram API request: {e}")

class FetchAIAgent:
    def __init__(self):
        self.agent = Agent(name="emergency_response_agent")
        self.conversation_context = []

    def update_context(self, role, content):
        self.conversation_context.append({"role": role, "content": content})

    @staticmethod
    async def handle_message(ctx: Context, message: Model):
        # This method will be called when the agent receives a message
        response = ctx.agent.storage.get("last_response") or "No response yet."
        await ctx.send(message.sender, response)

    def process(self, input_text):
        self.update_context("user", input_text)
        
        # Use the agent's storage to retain information
        self.agent.storage.set("last_input", input_text)
        
        # In a real-world scenario, you might want to implement more complex
        # logic here, possibly interacting with other agents or services
        
        return self.agent.storage.get("last_input") or "No input received yet."

class SpeechToTextAgent:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in environment variables")
        self.deepgram = DeepgramClient(self.api_key)
        self.websocket_url = "wss://api.deepgram.com/v1/listen"
        self.conversation_manager = None

    def set_conversation_manager(self, manager):
        self.conversation_manager = manager

    async def start_listening(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with websockets.connect(
            self.websocket_url,
            extra_headers={"Authorization": f"Token {self.api_key}"},
            ssl=ssl_context
        ) as websocket:
            await self.stream_audio(websocket)

    async def stream_audio(self, websocket):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024)

        print("Listening... Speak into the microphone.")

        try:
            while True:
                data = stream.read(1024)
                await websocket.send(data)
                response = await websocket.recv()
                await self.process_server_message(response)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    async def process_server_message(self, message):
        msg = json.loads(message)
        if 'channel' in msg and 'alternatives' in msg['channel']:
            transcript = msg['channel']['alternatives'][0]['transcript']
            if transcript and not transcript.isspace():
                print(f"User: {transcript}")
                if self.conversation_manager:
                    response = self.conversation_manager.process_input(transcript)
                    print(f"AI: {response}")
                else:
                    print("ConversationManager not set. Unable to process input.")

    def start(self):
        asyncio.run(self.start_listening())

class ConversationManager:
    def __init__(self):
        self.llm = LanguageModelProcessor()
        self.fetch_agent = FetchAIAgent()
        self.speech_to_text = SpeechToTextAgent()
        self.speech_to_text.set_conversation_manager(self)
        try:
            self.tts = TextToSpeech()
        except ValueError as e:
            print(f"Error initializing TextToSpeech: {e}")
            self.tts = None

    def process_input(self, input_text):
        print(f"User: {input_text}")
        
        # Process with FetchAI agent
        fetch_response = self.fetch_agent.process(input_text)
        print(f"FetchAI Agent processed: {fetch_response}")
        
        # Process with LLM
        llm_response = self.llm.process(input_text)
        
        # Update FetchAI agent context
        self.fetch_agent.update_context("assistant", llm_response)
        
        if self.tts:
            try:
                self.tts.speak(llm_response)
            except Exception as e:
                print(f"Error in text-to-speech: {e}")
                print("Continuing with text-only response.")
        else:
            print("Text-to-Speech is not available. Displaying text response only.")
        
        return llm_response

    def get_conversation_history(self):
        return self.fetch_agent.conversation_context

    def start_voice_input(self):
        self.speech_to_text.start()

conversation_manager = None

def initialize_conversation():
    global conversation_manager
    if conversation_manager is None:
        print("Initializing ConversationManager...")
        conversation_manager = ConversationManager()
        
        print("Processing predefined inputs...")
        predefined_inputs = [
            "Help, active shooter!",
            "The person is wearing a black tee and has black hair. He is on the 4th floor, he has a revolver, there are no injuries.",
        ]
        for input_text in predefined_inputs:
            print(f"Processing: {input_text}")
            conversation_manager.process_input(input_text)
        print("Predefined inputs processed.")

@app.before_request
def before_request():
    initialize_conversation()

@app.route('/')
def home():
    return render_template('index.html')

# Update the chat route to properly handle JSON input
@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
    
    data = request.get_json()
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    response = conversation_manager.process_input(user_input)
    return jsonify({'response': response})

# Update the voice_input route to properly handle audio input
@app.route('/voice_input', methods=['POST'])
def voice_input():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Save the audio data to a temporary file
    temp_filename = "temp_audio.wav"
    audio_file.save(temp_filename)
    
    # Process the audio using Deepgram
    text = process_audio_to_text(temp_filename)
    
    # Use the existing process_input method
    response = conversation_manager.process_input(text)
    
    # Clean up the temporary file
    os.remove(temp_filename)
    
    return jsonify({'response': response})

@app.route('/start_voice_stream')
def start_voice_stream():
    def generate():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024)
        
        while True:
            data = stream.read(1024)
            yield (b'--frame\r\n'
                   b'Content-Type: audio/wav\r\n\r\n' + data + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/history')
def history():
    return jsonify(conversation_manager.get_conversation_history())

def process_audio_to_text(audio_file):
    deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
    
    with open(audio_file, "rb") as audio:
        source = {"buffer": audio, "mimetype": "audio/wav"}
        options = {"punctuate": True, "model": "nova-2", "language": "en-US"}
        
        response = deepgram.transcription.sync_prerecorded(source, options)
        
        if response and response.results and response.results.channels:
            return response.results.channels[0].alternatives[0].transcript
        else:
            return "Sorry, I couldn't understand the audio."

if __name__ == "__main__":
    print("Starting the Emergency Response System...")
    initialize_conversation()  # Initialize conversation manager before starting threads
    
    # Start the speech-to-text input in a separate thread
    import threading
    voice_thread = threading.Thread(target=conversation_manager.start_voice_input)
    voice_thread.start()
    
    print("Starting Flask server...")
    app.run(debug=True, use_reloader=False)
    print("Flask server has shut down.")