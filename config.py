from dataclasses import dataclass
import os


@dataclass
class AssistantConfig:
    """Configuration values loaded from environment variables."""

    energy_threshold: int = 300
    min_energy_threshold: int = 120
    max_energy_threshold: int = 700
    pause_threshold: float = 0.8
    non_speaking_duration: float = 0.4

    wake_timeout: int = 15
    wake_phrase_time_limit: int = 8
    query_timeout: int = 15
    query_phrase_time_limit: int = 12
    language_timeout: int = 12
    language_phrase_time_limit: int = 8

    auto_switch_mic: bool = True
    debug: bool = False

    @classmethod
    def from_env(cls) -> "AssistantConfig":
        """Build config from environment variables with sensible defaults."""
        return cls(
            energy_threshold=int(os.environ.get("VOICE_ENERGY_THRESHOLD", "300")),
            min_energy_threshold=int(os.environ.get("VOICE_MIN_ENERGY_THRESHOLD", "120")),
            max_energy_threshold=int(os.environ.get("VOICE_MAX_ENERGY_THRESHOLD", "700")),
            wake_timeout=int(os.environ.get("VOICE_WAKE_TIMEOUT", "15")),
            wake_phrase_time_limit=int(os.environ.get("VOICE_WAKE_PHRASE_LIMIT", "8")),
            query_timeout=int(os.environ.get("VOICE_QUERY_TIMEOUT", "15")),
            query_phrase_time_limit=int(os.environ.get("VOICE_QUERY_PHRASE_LIMIT", "12")),
            language_timeout=int(os.environ.get("VOICE_LANGUAGE_TIMEOUT", "12")),
            language_phrase_time_limit=int(os.environ.get("VOICE_LANGUAGE_PHRASE_LIMIT", "8")),
            auto_switch_mic=os.environ.get("VOICE_AUTO_SWITCH_MIC", "1") == "1",
            debug=os.environ.get("VOICE_DEBUG", "0") == "1",
        )
