import os
import pygame
from settings import *


class ResourceLoader:
    """Класс для загрузки и хранения всех ресурсов (спрайты, фоны и текстуры)"""

    _instance = None
    _sprites = {}
    _backgrounds = {}
    _textures = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_resources()
        return cls._instance

    def _load_all_resources(self):
        """Загружает все ресурсы из папки assets"""
        self._load_all_sprites()
        self._load_all_backgrounds()
        self._load_all_textures()

    def _load_all_sprites(self):
        """Загружает все спрайты персонажей"""
        # Загрузка спрайтов игрока
        player_path = os.path.join(SPRITES_PATH, 'player')
        self._sprites['player'] = {
            'idle': self._load_animation(player_path, 'player_idle', 2, (PLAYER_WIDTH, PLAYER_HEIGHT)),
            'walk': self._load_animation(player_path, 'player_walk', 4, (PLAYER_WIDTH, PLAYER_HEIGHT)),
            'jump': self._load_image(os.path.join(player_path, 'player_jump.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)),
            'fall': self._load_image(os.path.join(player_path, 'player_fall.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))
        }

        # Загрузка спрайтов врага
        enemy_path = os.path.join(SPRITES_PATH, 'enemy')
        self._sprites['enemy'] = {
            'idle': self._load_animation(enemy_path, 'enemy_idle', 2, (40, 40)),
            'walk': self._load_animation(enemy_path, 'enemy_walk', 2, (40, 40))
        }

        # Загрузка спрайтов монет
        coin_path = os.path.join(SPRITES_PATH, 'coin')
        self._sprites['coin'] = self._load_animation(coin_path, 'coin', 4, (20, 20))

    def _load_all_backgrounds(self):
        """Загружает все фоновые изображения"""
        self._backgrounds['game'] = self._load_image(GAME_BACKGROUND, (WIDTH, HEIGHT))

        if os.path.exists(MENU_BACKGROUND):
            self._backgrounds['menu'] = self._load_image(MENU_BACKGROUND, (WIDTH, HEIGHT))
        else:
            self._backgrounds['menu'] = self._backgrounds['game']

    def _load_all_textures(self):
        """Загружает все текстуры для платформ и земли"""
        platforms_path = os.path.join(SPRITES_PATH, 'platforms')

        # Текстуры земли
        self._textures['ground'] = self._load_image(os.path.join(platforms_path, 'ground.png'))
        self._textures['ground_top'] = self._load_image(os.path.join(platforms_path, 'ground_top.png'))

        # Текстуры платформ
        self._textures['platform'] = self._load_image(os.path.join(platforms_path, 'platform.png'))
        self._textures['platform_left'] = self._load_image(os.path.join(platforms_path, 'platform_left.png'))
        self._textures['platform_mid'] = self._load_image(os.path.join(platforms_path, 'platform_mid.png'))
        self._textures['platform_right'] = self._load_image(os.path.join(platforms_path, 'platform_right.png'))

    def _load_image(self, path, scale=None):
        """Загружает одно изображение"""
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
            else:
                print(f"Предупреждение: Не удалось загрузить {path}")
                # Создаем цветную заглушку
                if 'ground' in path:
                    image = pygame.Surface((40, 40))
                    image.fill(BLACK)
                elif 'platform' in path:
                    image = pygame.Surface((40, 20))
                    image.fill(GREEN)
                else:
                    image = pygame.Surface((40, 40))
                    image.fill(RED)
                return image
        except pygame.error:
            print(f"Предупреждение: Ошибка загрузки {path}")
            image = pygame.Surface((40, 40))
            image.fill(RED)
            return image

        if scale:
            image = pygame.transform.scale(image, scale)
        return image

    def _load_animation(self, folder, base_name, count, scale=None):
        """Загружает анимацию из нескольких файлов"""
        frames = []
        for i in range(1, count + 1):
            path = os.path.join(folder, f"{base_name}_{i}.png")
            frame = self._load_image(path, scale)
            frames.append(frame)

        if not frames:
            surf = pygame.Surface((40, 40))
            surf.fill(RED)
            frames = [surf]

        return frames

    def get_player_animation(self, state):
        """Возвращает анимацию игрока"""
        return self._sprites['player'].get(state, [self._sprites['player']['idle'][0]])

    def get_enemy_animation(self, state):
        """Возвращает анимацию врага"""
        return self._sprites['enemy'].get(state, [self._sprites['enemy']['idle'][0]])

    def get_coin_animation(self):
        """Возвращает анимацию монеты"""
        return self._sprites['coin']

    def get_background(self, name='game'):
        """Возвращает фоновое изображение"""
        return self._backgrounds.get(name, self._backgrounds['game'])

    def get_texture(self, name):
        """Возвращает текстуру по имени"""
        return self._textures.get(name)