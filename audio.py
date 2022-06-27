import os
import pygame


class AudioManager:
    def __init__(self):

        # Music
        self.musics = None
        self.music_index = -1

        # Get sounds
        self.sounds = {}
        self.can_play_sound = True
        for file in os.scandir('sfx'):
            self.sounds[file.name.split(
                '.')[0]] = pygame.mixer.Sound(file.path)

        self.sounds['jump'].set_volume(0.4)

        self.last_time = pygame.time.get_ticks()
        self.cooldowns = 100

    def set_volume(self, int):
        pygame.mixer.music.set_volume(int)

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            print("No music")
            self.music_index += 1

            print(len([name for name in os.listdir('musics')]))
            print(self.music_index)
            if self.music_index >= len([name for name in os.listdir('musics')]):
                print()
                self.music_index = 0

            for file_index, file in enumerate(os.scandir('musics')):
                if file_index == self.music_index:
                    pygame.mixer.music.load(file.path)

            pygame.mixer.music.play(1, 0)

    def play_sound(self, name):
        current_time = pygame.time.get_ticks()

        if self.can_play_sound:
            for sound_name, sound in self.sounds.items():
                if name == sound_name:
                    sound.play()
                    self.can_play_sound = False

        if current_time - self.last_time >= self.cooldowns:
            self.can_play_sound = True


global audio_manager
audio_manager = AudioManager()
