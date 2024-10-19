import asyncio
import os
import time
import subprocess
import shutil
from dotenv import load_dotenv
from deepgram import DeepgramClient, SpeakOptions

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

load_dotenv()

# Create the system_prompt.txt file
SYSTEM_PROMPT = """
You are an AI simulating a highly trained police officer responding to emergency situations. Your primary goals are to ensure public safety, de-escalate dangerous situations, and provide clear, authoritative instructions. Respond as if you are directly communicating with someone in an emergency situation. Be concise, and ask followup questions such as description of person, gun, location, etc.
"""

with open('system_prompt.txt', 'w') as file:
    file.write(SYSTEM_PROMPT)

class LanguageModelProcessor:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key=os.getenv("GROQ_API_KEY"))
        self.memory = ConversationBufferMemory(return_messages=True)
        system_prompt = self.load_system_prompt()
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    def load_system_prompt(self):
        try:
            with open('system_prompt.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Warning: system_prompt.txt not found. Using default prompt.")
            return SYSTEM_PROMPT

    def process(self, text):
        self.memory.chat_memory.add_user_message(text)

        start_time = time.time()
        response = self.conversation.invoke({"text": text})
        end_time = time.time()

        self.memory.chat_memory.add_ai_message(response['text'])

        elapsed_time = int((end_time - start_time) * 1000)
        print(f"Police Officer AI ({elapsed_time}ms): {response['text']}")
        return response['text']

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

class ConversationManager:
    def __init__(self):
        self.llm = LanguageModelProcessor()
        try:
            self.tts = TextToSpeech()
        except ValueError as e:
            print(f"Error initializing TextToSpeech: {e}")
            self.tts = None

    async def process_input(self, input_text):
        print(f"Civilian: {input_text}")
        llm_response = self.llm.process(input_text)
        if self.tts:
            try:
                self.tts.speak(llm_response)
            except Exception as e:
                print(f"Error in text-to-speech: {e}")
                print("Continuing with text-only response.")
        else:
            print("Text-to-Speech is not available. Displaying text response only.")
        # Add a short pause between responses
        await asyncio.sleep(1)

    async def main(self):
        inputs = [
            "Help, active shooter!",
            "The person is wearing a black tee and has black hair. He is on the 4th floor, he has a revolver, there are no injuries.",
            # Add more follow-up inputs here as needed
        ]

        for input_text in inputs:
            await self.process_input(input_text)
        #     # Wait for user input before continuing to the next message
        #     input("Press Enter to continue...")
        # Allow user to continue the conversation
        while True:
            user_input = input("\nEnter your message (or type 'exit' to end the conversation): ").strip()
            if user_input.lower() == 'exit':
                print("Ending the conversation. Stay safe!")
                break
            await self.process_input(user_input)

if __name__ == "__main__":
    manager = ConversationManager()
    asyncio.run(manager.main())