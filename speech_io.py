import os
from typing import Any, Optional, Tuple
import speech_recognition as sr

from assistant_logger import AssistantLogger
from config import AssistantConfig


class SpeechIO:
    """Microphone and speech-recognition operations."""

    def __init__(self, config: AssistantConfig, logger: AssistantLogger):
        self.config = config
        self.logger = logger

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = config.energy_threshold
        self.recognizer.pause_threshold = config.pause_threshold
        self.recognizer.non_speaking_duration = config.non_speaking_duration

        self.available_mics = sr.Microphone.list_microphone_names()
        self.current_mic_index: Optional[int] = None
        self.microphone = self.create_microphone()

    def create_microphone(self) -> sr.Microphone:
        """Choose microphone from env override or automatic device selection."""
        mic_index_raw = os.environ.get("VOICE_MIC_INDEX")
        if mic_index_raw:
            try:
                mic_index = int(mic_index_raw)
                mic_name = self.available_mics[mic_index] if 0 <= mic_index < len(self.available_mics) else "Unknown"
                self.logger.info(f"Using microphone index {mic_index}: {mic_name}")
                self.current_mic_index = mic_index
                return sr.Microphone(device_index=mic_index)
            except (ValueError, OSError):
                self.logger.info("Invalid VOICE_MIC_INDEX. Falling back to default selection.")

        auto_index = self.find_likely_input_microphone_index()
        if auto_index is not None:
            self.current_mic_index = auto_index
            self.logger.info(f"Auto-selected microphone index {auto_index}: {self.available_mics[auto_index]}")
            return sr.Microphone(device_index=auto_index)

        self.logger.info("Using default microphone. Set VOICE_MIC_INDEX in .env to override.")
        self.current_mic_index = None
        return sr.Microphone()

    def find_likely_input_microphone_index(self) -> Optional[int]:
        """Pick the most likely input microphone based on device-name heuristics."""
        preferred_keywords = ["microphone", "mic", "input", "array", "headset", "usb"]
        avoid_keywords = ["stereo mix", "output", "speaker", "monitor", "virtual", "wave out"]

        best_index: Optional[int] = None
        best_score = -999
        for idx, name in enumerate(self.available_mics):
            lowered = name.lower()
            score = 0
            for token in preferred_keywords:
                if token in lowered:
                    score += 2
            for token in avoid_keywords:
                if token in lowered:
                    score -= 3

            if score > best_score:
                best_score = score
                best_index = idx

        if best_index is not None and best_score > 0:
            return best_index
        return None

    def switch_to_next_microphone(self) -> bool:
        """Rotate to the next available microphone when repeated timeouts occur."""
        if not self.available_mics:
            return False

        start_index = self.current_mic_index if self.current_mic_index is not None else -1
        total = len(self.available_mics)
        for offset in range(1, total + 1):
            candidate = (start_index + offset) % total
            mic_name = self.available_mics[candidate]
            try:
                self.logger.info(f"Trying next microphone [{candidate}]: {mic_name}")
                self.microphone = sr.Microphone(device_index=candidate)
                self.current_mic_index = candidate
                self.calibrate_microphone(duration=1)
                self.logger.info("Switched microphone successfully.")
                return True
            except OSError:
                continue
        return False

    def calibrate_microphone(self, duration: int = 2) -> None:
        """Calibrate ambient noise and clamp energy threshold to configured limits."""
        with self.microphone as source:
            self.logger.mic_state("MIC ON calibrate")
            self.logger.info("Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.recognizer.energy_threshold = min(
                max(self.recognizer.energy_threshold, self.config.min_energy_threshold),
                self.config.max_energy_threshold,
            )
            self.logger.info(f"Energy threshold set to {int(self.recognizer.energy_threshold)}")
        self.logger.mic_state("MIC OFF calibrate")

    def capture_audio(self, timeout: int, phrase_time_limit: int, capture_label: str) -> sr.AudioData:
        """Capture one speech segment while emitting optional mic state debug logs."""
        with self.microphone as source:
            self.logger.mic_state(f"MIC ON {capture_label}")
            try:
                return self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            finally:
                self.logger.mic_state(f"MIC OFF {capture_label}")

    def recognize_google(self, audio: sr.AudioData, language: Optional[str] = None) -> str:
        """Recognize speech text using Google Web Speech API."""
        recognizer_any: Any = self.recognizer
        if language:
            return recognizer_any.recognize_google(audio, language=language)
        return recognizer_any.recognize_google(audio)

    def recognize_google_with_alternatives(self, audio: sr.AudioData) -> Tuple[str, list[str]]:
        """Return primary transcript and alternatives from Google STT response."""
        recognizer_any: Any = self.recognizer
        response = recognizer_any.recognize_google(audio, show_all=True)

        alternatives: list[str] = []
        if isinstance(response, dict):
            for alt in response.get("alternative", []):
                transcript = alt.get("transcript")
                if isinstance(transcript, str) and transcript.strip():
                    alternatives.append(transcript)

        if alternatives:
            return alternatives[0], alternatives

        return self.recognize_google(audio), []
