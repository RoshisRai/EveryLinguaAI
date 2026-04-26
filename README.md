# EveryLinguaAI 🌟
### Get assistance in languages spoken all over the world 🌍

EveryLinguaAI is a voice assistant application capable of recognizing and responding to spoken commands in multiple languages. It utilizes the Google Speech Recognition API for speech-to-text conversion, Deep Translator for seamless language translation, and leverages OpenAI's GPT models to generate human-like conversational responses.

## Project Structure

The codebase is now split into focused modules for easier maintenance:

- `main.py`: Application entrypoint.
- `voice_assistant.py`: High-level orchestration (wake loop + handoff to conversation).
- `config.py`: Environment-based runtime configuration.
- `assistant_logger.py`: Info/error/debug logging helpers.
- `wakeword.py`: Wake-word normalization and fuzzy matching.
- `speech_io.py`: Microphone selection, calibration, capture, and STT utilities.
- `conversation.py`: Language selection and conversation flow.
- `openai_client.py`: OpenAI chat + text-to-speech API integration.
- `languages.py`: Supported language mapping.
- `audio.py`: Audio playback helpers.

## Features

- **Wake Word Detection**: Activates the assistant using a specific wake word.
- **Multi-Language Support**: Capable of understanding and responding in numerous languages.
- **Conversational AI**: Employs OpenAI's GPT models for generating intelligent responses.
- **Language Switching**: Allows users to switch the assistant's language dynamically.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following requirements:

- Python 3.6 or higher
- Pip for Python package management

### Installation

Follow these steps to get your voice assistant up and running:

1. **Clone the repository**:

```bash
git clone https://github.com/RoshisRai/EveryLinguaAI.git
```


2. **Navigate to the project directory**:
```bash
cd EveryLinguaAI
```

3. **Install the required Python packages**:
```bash
pip install -r requirements.txt
```

### Configuration

- Obtain an API key from OpenAI.
- Create a `.env` file in the project root directory.
- Add the required key and any optional settings below.

Required:

```plaintext
OPENAI_API_KEY=YourOpenAIApiKeyHere
```

Optional voice settings:

```plaintext
# OpenAI response cost control
OPENAI_MAX_OUTPUT_TOKENS=120
OPENAI_SYSTEM_PROMPT=You are a concise multilingual voice assistant. Keep answers brief and practical.

# Microphone selection
VOICE_MIC_INDEX=2

# Recognition sensitivity
VOICE_ENERGY_THRESHOLD=300
VOICE_MIN_ENERGY_THRESHOLD=120
VOICE_MAX_ENERGY_THRESHOLD=700

# Timing (seconds)
VOICE_WAKE_TIMEOUT=15
VOICE_WAKE_PHRASE_LIMIT=8
VOICE_LANGUAGE_TIMEOUT=12
VOICE_LANGUAGE_PHRASE_LIMIT=8
VOICE_QUERY_TIMEOUT=15
VOICE_QUERY_PHRASE_LIMIT=12

# Behavior toggles
VOICE_AUTO_SWITCH_MIC=1
VOICE_DEBUG=0
```

Notes:

- `OPENAI_MAX_OUTPUT_TOKENS` sets a hard cap for assistant response size and helps control API costs.
- `OPENAI_SYSTEM_PROMPT` lets you override the default concise system instruction used by the OpenAI client.
- `VOICE_MIC_INDEX` lets you lock to a specific input device. If omitted, the app auto-selects a likely microphone.
- Set `VOICE_DEBUG=1` to show debug logs (including mic state transitions and wake transcripts).
- `VOICE_AUTO_SWITCH_MIC=1` enables automatic fallback to the next microphone after repeated timeouts.

### Response Cost Control

The OpenAI client uses two settings to reduce usage costs:

- `OPENAI_MAX_OUTPUT_TOKENS`: Hard upper bound for generated output tokens per response.
- `OPENAI_SYSTEM_PROMPT`: System instruction used to keep replies concise.

If these are not set, the app uses safe defaults from the client implementation.

### Running EveryLinguaAI

To start EveryLinguaAI voice assistant, execute:

```bash
python main.py
```

### Usage

To begin interacting with EveryLinguaAI, activate it by saying the wake word "Hey Red" or any other wake word you've configured. Once activated, follow these steps to engage in conversation:

1. **Language Selection:** After activating the voice assistant, specify the language you want to use for the conversation. Simply say the name of the desired language in the language you are currently interacting with. For example, if you want to converse in Spanish, say "español" or "Spanish." You can also switch languages at any time during the conversation by saying commands like "change language," "another language," or "different language" in either the current language or English.

2. **Asking Questions:** After selecting the language, you can proceed to ask questions or give commands. Here are some examples of commands:
   - "What is the tallest mountain in the world?"
   - "Can you tell me some facts about pyramids?"
   - "Do aliens exist?"
   - "Is AI going to take over?"

3. **Language Switching:** If you wish to switch languages during the conversation, simply utter one of the predefined language-switching commands in the language you are currently using or in English. The voice assistant will prompt you to specify the new language, allowing you to seamlessly transition between languages as needed.

4. **Ending Interaction:** To stop asking questions and deactivate the voice assistant, say commands like "stop listening," "no more," "that's all," or "nothing else." You can reactivate the voice assistant at any time by saying the wake word again.

Current stop phrases used in code:

- "stop listening"
- "no"
- "that's all"
- "nothing else"

Feel free to explore the capabilities of the EveryLinguaAI by asking questions, switching languages, and interacting in various scenarios. Enjoy the convenience of a versatile and multilingual conversational experience with EveryLinguaAI Voice Assistant!


### Contributing

We welcome contributions to this project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`.
4. Push to your branch: `git push origin <branch_name>`.
5. Create the pull request.

Alternatively, see the GitHub documentation on [creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

### License

This project is licensed under the MIT License - see the `LICENSE` file for details.

### Contact

If you have any questions or feedback, please contact me at 📧 roshis.awai@gmail.com.
