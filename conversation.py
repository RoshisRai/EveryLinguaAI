import random
from typing import Optional, Tuple

import speech_recognition as sr
from deep_translator import GoogleTranslator

from assistant_logger import AssistantLogger
from config import AssistantConfig
from speech_io import SpeechIO
from openai_client import OpenAIClient
from audio import play_audio
from languages import languages_dict


LanguageCode = Tuple[str, str]


class ConversationManager:
    """Language selection and active conversation flow."""

    def __init__(
        self,
        config: AssistantConfig,
        logger: AssistantLogger,
        speech_io: SpeechIO,
        openai_client: OpenAIClient,
    ):
        self.config = config
        self.logger = logger
        self.speech_io = speech_io
        self.openai_client = openai_client

    def get_language_code(self) -> Optional[LanguageCode]:
        """Prompt for language name and return a `(speech_locale, translation_code)` tuple."""
        self.logger.info("Please choose a language.")
        for _ in range(3):
            try:
                audio = self.speech_io.capture_audio(
                    timeout=self.config.language_timeout,
                    phrase_time_limit=self.config.language_phrase_time_limit,
                    capture_label="language",
                )
                spoken_language = self.speech_io.recognize_google(audio)
                language_data = languages_dict.get(spoken_language.lower())
                if language_data and len(language_data) >= 2:
                    language_code: LanguageCode = (language_data[0], language_data[1])
                    self.logger.info(f"Language selected: {spoken_language}")
                    return language_code
                self.logger.info("Language not found. Please try again.")
            except sr.UnknownValueError:
                self.logger.info("Could not understand language. Please try again.")
            except sr.WaitTimeoutError:
                self.logger.info("Language selection timed out. Please speak again.")
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition request failed: {e}")
        return None

    def conduct_conversation(self, language_code: LanguageCode) -> None:
        """Run conversational loop in selected language until stop phrase is spoken."""
        self.logger.info(f"Conversation started in {language_code[1]}. Speak your query.")
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
            "Need help with anything else?",
        ]

        stop_phrases = ["stop listening", "no", "that's all", "nothing else"]
        change_language_phrases = ["change language", "another language", "different language"]

        while True:
            try:
                audio = self.speech_io.capture_audio(
                    timeout=self.config.query_timeout,
                    phrase_time_limit=self.config.query_phrase_time_limit,
                    capture_label="query",
                )
                text = self.speech_io.recognize_google(audio, language=language_code[0])
                user_input_english = GoogleTranslator(source="auto", target="en").translate(text)

                if user_input_english.lower() in stop_phrases:
                    self.logger.info("Thank you. Have a great day!")
                    break

                if any(phrase in user_input_english.lower() for phrase in change_language_phrases):
                    self.logger.info("Changing language. Please say the language you want to switch to.")
                    new_language_code = self.get_language_code()
                    if new_language_code:
                        language_code = new_language_code
                        self.logger.info(f"Language changed to {language_code[1]}. Speak your query.")
                        continue
                    self.logger.info("Failed to change language after several attempts.")
                    break

                response = self.openai_client.chat_with_gpt(user_input_english)
                translated_response = GoogleTranslator(source="en", target=language_code[1]).translate(response)
                self.logger.info(f"Response: {translated_response}")
                audio_filepath = self.openai_client.text_to_speech(translated_response)
                play_audio(audio_filepath)
                self.logger.info(random.choice(assistance_messages))
            except sr.UnknownValueError:
                self.logger.info("Could not understand audio. Please try again.")
            except sr.WaitTimeoutError:
                self.logger.info("I didn't hear anything. Please try again.")
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition request failed: {e}")
