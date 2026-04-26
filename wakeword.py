import re
from difflib import SequenceMatcher
from typing import Sequence


WAKE_WORD_VARIANTS = [
    "hey red",
    "hey read",
    "hey rad",
    "hey raid",
    "hi red",
    "hi read",
    "hi rad",
    "high red",
    "high read",
    "hello red",
    "hello read",
    "a red",
]

WAKE_GREETINGS = {"hey", "hi", "hello", "hay", "he", "yo"}
WAKE_NAMES = {"red", "read", "rad", "reed", "raid", "rid", "rhett", "redd"}


class WakeWordDetector:
    """Wake-word matching with direct, variant, and fuzzy token strategies."""

    def normalize_text(self, text: str) -> str:
        """Normalize recognized text for consistent wake-word matching."""
        normalized = re.sub(r"[^a-zA-Z\\s]", " ", text).lower()
        return " ".join(normalized.split())

    def matches_wake_tokens(self, normalized_text: str) -> bool:
        """Fuzzy-match two-word patterns like 'hi red' and close phonetic variants."""
        words = normalized_text.split()
        if len(words) < 2:
            return False

        for i in range(len(words) - 1):
            first = words[i]
            second = words[i + 1]
            greeting_match = any(SequenceMatcher(None, first, g).ratio() >= 0.75 for g in WAKE_GREETINGS)
            name_match = any(SequenceMatcher(None, second, n).ratio() >= 0.7 for n in WAKE_NAMES)
            if greeting_match and name_match:
                return True

        return False

    def is_wake_word_detected(self, candidates: Sequence[str], wake_word: str = "hey red") -> bool:
        """Return True when wake word is detected from one or more transcripts."""
        normalized_wake = self.normalize_text(wake_word)

        for candidate in [c for c in candidates if isinstance(c, str)]:
            normalized_text = self.normalize_text(candidate)
            if not normalized_text:
                continue

            if normalized_wake in normalized_text:
                return True

            for variant in WAKE_WORD_VARIANTS:
                normalized_variant = self.normalize_text(variant)
                if normalized_variant in normalized_text:
                    return True
                if SequenceMatcher(None, normalized_text, normalized_variant).ratio() >= 0.8:
                    return True

            if self.matches_wake_tokens(normalized_text):
                return True

        return False
