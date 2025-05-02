# 📁 file: sounds.py

import os
import pygame

pygame.init()

def play_sound(name):
    try:
        sound_path = f"assets/{name}.wav"
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sound.play(maxtime=1000)  # plays for 1000 ms = 1 second
    except Exception as e:
        print("Sound error:", e)
