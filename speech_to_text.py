import speech_recognition as sr
from languages import languages_dict
from deep_translator import GoogleTranslator
import random

# Initializing the recognizer
r = sr.Recognizer()

def warm_up_microphone(warm_up_cycles=4):
    with sr.Microphone() as source:
        for _ in range(warm_up_cycles):
            r.adjust_for_ambient_noise(source, duration=0.5)  # Adjusting for ambient noise each time
            try:
                # Attempting a quick listen-and-ignore cycle
                r.listen(source, timeout=1, phrase_time_limit=1)
                print(f"Warming up microphone_{_}")
            except sr.WaitTimeoutError:
                continue

# Calling the warm-up function before entering the main loop
warm_up_microphone()

def is_wake_word_detected(audio_text, wake_word="hey red"):
    return wake_word in audio_text.lower()

def get_language_code(languages_dict, max_retries=5):
    retry_count = 0
    while retry_count < max_retries:
        with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=3, phrase_time_limit=3)
                try:
                    spoken_language = r.recognize_google(audio)
                    language_code = languages_dict.get(spoken_language.lower())
                    if language_code:
                        print(f"You said {spoken_language}: {language_code}")
                        return language_code
                    else:
                        print("Language not found, can you say that again?")
                        retry_count += 1
                except sr.UnknownValueError:
                    retry_count += 1
                    print("I didn't catch that, can you say that again?")
        
            
    return None

def recognize_speech(language_code, max_retries=5):
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
    
    for _ in range(max_retries):
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening for your command...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language=language_code)
                user_input_english = GoogleTranslator(source='auto', target='en').translate(text)  
                if user_input_english.lower() in stop_phrases:
                    print(random.choice(assistance_messages))
                    return "stop_phrase"
                elif any(phrase in user_input_english.lower() for phrase in change_language_phrases):
                    return "change_language"
                else:
                    print(f"You said: {text}")
                    print(random.choice(assistance_messages))
                    continue
            except sr.UnknownValueError:
                print("I don't understand, try again.")
    return None

# Main loop
while True:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening for wake word...")
        audio = r.listen(source, timeout=3, phrase_time_limit=3)
        try:
            spoken_text = r.recognize_google(audio)
            if is_wake_word_detected(spoken_text):
                retry_language_selection = 0
                while retry_language_selection < 5:
                    print("Please choose a language.")
                    language_code = get_language_code(languages_dict, max_retries=5)
                    
                    if language_code:
                        action = recognize_speech(language_code)
                        if action == "stop_phrase":
                            print("Stop phrase recognition")
                            break
                        elif action == "change_language":
                            print("Changing language. Please say the language you want to switch to.")
                            retry_language_selection = 0  # Resetting the counter to allow for language re-selection
                            continue
                        elif action is None:
                            print("Failed to recognize speech, returning to wake word detection.")
                            break
                    else:
                        retry_language_selection += 1
                        if retry_language_selection >= 5:
                            print("Failed to get language code after several attempts, returning to wake word detection.")
                            break
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")