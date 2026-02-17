import pygame
from settings import *
from utils.sprite_sheet import SpriteLoader


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprites = SpriteLoader()
        self.frames = self.sprites.get_coin_animation()
        self.current_frame = 0
        self.animation_timer = 0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Анимация вращения монеты"""
        self.animation_timer += 1
        if self.animation_timer >= 8:  # Меняем кадр каждые 8 тиков
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]