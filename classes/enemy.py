import pygame
from settings import *
from utils.sprite_sheet import SpriteLoader


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_bound, right_bound, speed=2):
        super().__init__()
        self.sprites = SpriteLoader()
        self.animation_state = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing_right = True

        # Загружаем анимации
        self.animations = {
            'idle': self.sprites.get_enemy_animation('idle'),
            'walk': self.sprites.get_enemy_animation('walk')
        }

        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.speed = speed

    def update_animation(self):
        """Обновляет анимацию врага"""
        self.animation_timer += 1

        # Определяем состояние
        if self.speed != 0:
            self.animation_state = 'walk'
            self.facing_right = self.speed > 0
        else:
            self.animation_state = 'idle'

        # Обновляем кадр
        if self.animation_timer >= 15:  # Медленнее чем игрок
            self.animation_timer = 0
            frames = self.animations[self.animation_state]
            self.animation_frame = (self.animation_frame + 1) % len(frames)
            self.image = frames[self.animation_frame]

            # Отражение спрайта
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.speed *= -1

        self.update_animation()