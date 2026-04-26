class AssistantLogger:
    """Simple logger with optional debug output."""

    def __init__(self, debug: bool = False):
        self.debug_enabled = debug

    def info(self, message: str) -> None:
        print(message, flush=True)

    def error(self, message: str) -> None:
        print(message, flush=True)

    def debug(self, message: str) -> None:
        if self.debug_enabled:
            print(message, flush=True)

    def mic_state(self, state: str) -> None:
        self.debug(state)
