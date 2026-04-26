import os
from pathlib import Path
from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = (
    "You are a concise multilingual voice assistant. "
    "Keep answers brief, practical, and under 3 short sentences unless explicitly asked for detail. "
    "Avoid long lists, long explanations, and unnecessary filler."
)

class OpenAIClient:
    """
    A client for interacting with OpenAI's API for conversational AI and text-to-speech functionalities.
    """
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = os.environ.get("OPENAI_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
        self.max_output_tokens = int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "120"))

    def chat_with_gpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=self.max_output_tokens,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        if isinstance(content, str):
            return content.strip()
        return ""
    
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