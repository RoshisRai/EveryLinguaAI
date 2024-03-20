import pygame

def play_audio(file_path):
    """
    This function plays an audio file at the given file path using pygame's mixer module.

    Args:
        file_path (str): The path to the audio file to be played.

    The function initializes the pygame mixer, loads the audio file, and plays it.
    It then waits for the audio to finish playing before stopping the mixer and quitting pygame.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.quit()