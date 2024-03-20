from dotenv import load_dotenv
from voice_assistant import VoiceAssistant

load_dotenv()

# Entry point for the EveryLinguaAI Voice Assistant application
def main():
    #Initialize and run the Voice Assistant
    voice_assistant = VoiceAssistant()
    voice_assistant.run()

if __name__ == "__main__":
    main()