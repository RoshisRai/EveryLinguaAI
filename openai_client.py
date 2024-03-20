from pathlib import Path
from openai import OpenAI

class OpenAIClient:
    """
    A client for interacting with OpenAI's API for conversational AI and text-to-speech functionalities.
    """
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def chat_with_gpt(self, promt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": promt}
            ]
        )
        return response.choices[0].message.content.strip()
    
    def text_to_speech(self, text):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        filename = Path(__file__).parent / "output_speech.mp3"
        with open(str(filename), "wb") as f:
            f.write(response.content)
        return str(filename)