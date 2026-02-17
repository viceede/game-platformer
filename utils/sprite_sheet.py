import os
import pygame
from settings import *


class SpriteLoader:
    """Класс для загрузки и хранения спрайтов"""

    _instance = None
    _sprites = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_sprites()
        return cls._instance

    def _load_all_sprites(self):
        """Загружает все спрайты из папки assets"""
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sprites')

        # Загрузка спрайтов игрока
        player_path = os.path.join(base_path, 'player')
        self._sprites['player'] = {
            'idle': self._load_animation(player_path, 'player_idle', 2),
            'walk': self._load_animation(player_path, 'player_walk', 4),
            'jump': self._load_image(os.path.join(player_path, 'player_jump.png')),
            'fall': self._load_image(os.path.join(player_path, 'player_fall.png'))
        }

        # Загрузка спрайтов врага
        enemy_path = os.path.join(base_path, 'enemy')
        self._sprites['enemy'] = {
            'idle': self._load_animation(enemy_path, 'enemy_idle', 2),
            'walk': self._load_animation(enemy_path, 'enemy_walk', 2)
        }

        # Загрузка спрайтов монет
        coin_path = os.path.join(base_path, 'coin')
        self._sprites['coin'] = self._load_animation(coin_path, 'coin', 4)

    def _load_image(self, path, scale=None):
        """Загружает одно изображение"""
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
        except pygame.error:
            print(f"Предупреждение: Не удалось загрузить {path}")
            # Возвращаем заглушку
            surf = pygame.Surface((40, 40))
            surf.fill(RED)
            return surf

    def _load_animation(self, folder, base_name, count, scale=None):
        """Загружает анимацию из нескольких файлов"""
        frames = []
        for i in range(1, count + 1):
            path = os.path.join(folder, f"{base_name}_{i}.png")
            frame = self._load_image(path, scale)
            frames.append(frame)
        return frames

    def get_player_animation(self, state):
        """Возвращает анимацию игрока для указанного состояния"""
        return self._sprites['player'].get(state, [self._sprites['player']['idle'][0]])

    def get_enemy_animation(self, state):
        """Возвращает анимацию врага для указанного состояния"""
        return self._sprites['enemy'].get(state, [self._sprites['enemy']['idle'][0]])

    def get_coin_animation(self):
        """Возвращает анимацию монеты"""
        return self._sprites['coin']