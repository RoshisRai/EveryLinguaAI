import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
from openai_client import OpenAIClient
from audio import play_audio
from languages import languages_dict
import random 


class VoiceAssistant:
    """
    A class to represent the voice assistant which handles speech recognition,
    language translation, and conversation management.
    """
    def __init__(self):
        """
        Initializes the voice assistant with necessary components.
        """
        self.recognizer = sr.Recognizer()
        self.openai_client = OpenAIClient(api_key=os.environ.get('OPENAI_API_KEY'))
        self.warm_up_microphone()

    def run(self):
        print("Voice Assistant activated. Say 'Hey Red' to begin.")
        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                
                try:
                    spoken_text = self.recognizer.recognize_google(audio)
                    if self.is_wake_word_detected(spoken_text):
                        language_code = self.get_language_code()
                        if language_code:
                            self.conduct_conversation(language_code)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.WaitTimeoutError:
                    print("Waiting for the audio...")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")

    def is_wake_word_detected(self, audio_text, wake_word="hey red"):
        return wake_word in audio_text.lower()
    
    def warm_up_microphone(self, warm_up_cycles=4):
        with sr.Microphone() as source:
            for _ in range(warm_up_cycles):
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjusting for ambient noise each time
                try:
                    # Attempting a quick listen-and-ignore cycle
                    self.recognizer.listen(source, timeout=1, phrase_time_limit=1)
                    print(f"Warming up microphone_{_}")
                except sr.WaitTimeoutError:
                    continue

    def get_language_code(self):
        print("Please choose a language.")
        for _ in range(3):  # Maximum 3 retries
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                
                try:
                    spoken_language = self.recognizer.recognize_google(audio)
                    language_code = languages_dict.get(spoken_language.lower())
                    if language_code:
                        print(f"You selected {spoken_language}: {language_code}")
                        return language_code
                    else:
                        print("Language not found. Please try again.")
                except sr.UnknownValueError:
                    print("Could not understand audio. Please try again.")
                except sr.WaitTimeoutError:
                    print("Waiting for the audio...")
        return None

    def conduct_conversation(self, language_code):
        print(f"Conversation started in {language_code}. Speak your query.")
        assistance_messages = [
            "Let me know if you need anything else.",
            "Is there anything else I can assist you with?",
            "Do you have any other questions?",
            "Anything more I can do for you?",
            "How else may I assist you today?",
            "Would you like help with anything else?",
            "Can I assist with another query?",
            "Any more assistance needed?",
            "What else can I do for you?",
            "Need help with anything else?"
        ]
        
        stop_phrases = ["stop listening", "no", "that's all", "nothing else"]
        change_language_phrases = ["change language", "another language", "different language"]
        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening for query...")
                audio = self.recognizer.listen(source, timeout=3)
                
                try:
                    print("Before translating")
                    text = self.recognizer.recognize_google(audio, language=language_code[0])
                    user_input_english = GoogleTranslator(source='auto', target='en').translate(text)
                    print("after transating")
                    if user_input_english.lower() in stop_phrases:
                        print("Thank you. Have a great day!")
                        break
                    elif any(phrase in user_input_english.lower() for phrase in change_language_phrases):
                        print("Changing language. Please say the language you want to switch to.")
                        language_code = self.get_language_code()
                        if language_code:
                            print(f"Language changed to {language_code}. Speak your query.")
                            continue
                        else:
                            print("Failed to change language after several attempts.")
                            break
                    else:
                        print(f"You said: {text}")
                        response = self.openai_client.chat_with_gpt(user_input_english)
                        translated_response = GoogleTranslator(source='en', target=language_code[1]).translate(response)
                        print(f"Response: {translated_response}")
                        audio_filepath = self.openai_client.text_to_speech(translated_response)
                        play_audio(audio_filepath)
                        print(random.choice(assistance_messages))
                except sr.UnknownValueError:
                    print("Could not understand audio. Please try again.")
                except sr.WaitTimeoutError:
                    print("Waiting for the audio...")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
