import os
import speech_recognition as sr

from openai_client import OpenAIClient
from assistant_logger import AssistantLogger
from config import AssistantConfig
from wakeword import WakeWordDetector
from speech_io import SpeechIO
from conversation import ConversationManager


class VoiceAssistant:
    """Voice assistant for wake-word activation and multilingual conversation."""

    def __init__(self):
        """Initialize dependencies and shared runtime state."""
        self.config = AssistantConfig.from_env()
        self.logger = AssistantLogger(debug=self.config.debug)
        self.wake_detector = WakeWordDetector()
        self.speech_io = SpeechIO(config=self.config, logger=self.logger)
        self.missed_listens = 0
        self.printed_mic_help = False
        self.openai_client = OpenAIClient(api_key=os.environ.get("OPENAI_API_KEY"))
        self.conversation_manager = ConversationManager(
            config=self.config,
            logger=self.logger,
            speech_io=self.speech_io,
            openai_client=self.openai_client,
        )
        self.speech_io.calibrate_microphone()

    def run(self):
        """Run the wake-word loop and start conversation after activation."""
        self.logger.info("Voice Assistant activated. Say 'Hey Red' to begin.")
        while True:
            try:
                audio = self.speech_io.capture_audio(
                    timeout=self.config.wake_timeout,
                    phrase_time_limit=self.config.wake_phrase_time_limit,
                    capture_label="wake",
                )
                self.missed_listens = 0
                spoken_text, alternatives = self.speech_io.recognize_google_with_alternatives(audio)
                self.logger.debug(f"Wake transcript: {spoken_text!r}")
                if alternatives and self.config.debug:
                    self.logger.debug(f"Wake alternatives: {alternatives}")

                if self.wake_detector.is_wake_word_detected([spoken_text, *alternatives]):
                    self.logger.info("Wake word detected. Switching to language selection.")
                    language_code = self.conversation_manager.get_language_code()
                    if language_code:
                        self.conversation_manager.conduct_conversation(language_code)
            except sr.UnknownValueError:
                self.logger.debug("Wake transcript could not be recognized.")
            except sr.WaitTimeoutError:
                self.missed_listens += 1
                self.logger.debug("No speech detected before timeout.")
                if self.missed_listens % 3 == 0:
                    new_threshold = max(
                        self.config.min_energy_threshold,
                        int(self.speech_io.recognizer.energy_threshold * 0.8)
                    )
                    self.speech_io.recognizer.energy_threshold = new_threshold
                    self.logger.info(f"Adjusted energy threshold to {self.speech_io.recognizer.energy_threshold}.")

                if self.missed_listens >= 5 and not self.printed_mic_help:
                    self.printed_mic_help = True
                    self.logger.info("Microphone may be incorrect. Available devices:")
                    for index, name in enumerate(self.speech_io.available_mics):
                        self.logger.info(f"  [{index}] {name}")
                    self.logger.info("Set VOICE_MIC_INDEX in .env to select a device.")

                if self.missed_listens >= 6 and self.config.auto_switch_mic:
                    if self.speech_io.switch_to_next_microphone():
                        self.missed_listens = 0
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition request failed: {e}")
            except OSError as e:
                self.logger.error(f"Microphone error: {e}")
                self.logger.info("Tip: check default input device or set VOICE_MIC_INDEX.")
            except Exception as e:
                self.logger.error(f"Unexpected wake-listen error: {type(e).__name__}: {e}")
