import pygame
from settings import *
from utils.sprite_sheet import ResourceLoader


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="platform"):
        """
        platform_type: "ground" - земля, "platform" - обычная платформа
        """
        super().__init__()
        self.resources = ResourceLoader()
        self.platform_type = platform_type

        if platform_type == "ground":
            self._create_ground_texture(x, y, width, height)
        else:
            self._create_platform_texture(x, y, width, height)

        self.rect = self.image.get_rect(topleft=(x, y))

    def _create_ground_texture(self, x, y, width, height):
        """Создает текстуру земли (пола) с поддержкой прозрачности"""
        ground_texture = self.resources.get_texture('ground')
        ground_top = self.resources.get_texture('ground_top')

        if ground_texture and ground_top:
            # Создаем поверхность с поддержкой прозрачности
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)

            # Заполняем основную часть земли
            texture_height = ground_texture.get_height()
            texture_width = ground_texture.get_width()

            for ty in range(0, height, texture_height):
                for tx in range(0, width, texture_width):
                    self.image.blit(ground_texture, (tx, ty))

            # Добавляем верхний слой (траву) с проверкой на прозрачность
            if ground_top:
                top_width = ground_top.get_width()
                for tx in range(0, width, top_width):
                    self.image.blit(ground_top, (tx, 0))
        else:
            # Если текстуры нет, используем цвет с альфа-каналом
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 255))  # Черный с полной непрозрачностью
            # Добавляем полоску сверху для имитации травы
            grass_strip = pygame.Surface((width, 5), pygame.SRCALPHA)
            grass_strip.fill((0, 255, 0, 255))
            self.image.blit(grass_strip, (0, 0))

    def _create_platform_texture(self, x, y, width, height):
        """Создает текстуру платформы с краями и прозрачностью"""
        left_texture = self.resources.get_texture('platform_left')
        mid_texture = self.resources.get_texture('platform_mid')
        right_texture = self.resources.get_texture('platform_right')

        if left_texture and mid_texture and right_texture:
            # Определяем высоту платформы по высоте текстуры
            platform_height = left_texture.get_height()

            # Создаем поверхность с поддержкой прозрачности
            self.image = pygame.Surface((width, platform_height), pygame.SRCALPHA)

            # Левый край
            self.image.blit(left_texture, (0, 0))

            # Середина - повторяем текстуру mid_texture
            mid_width = mid_texture.get_width()
            current_x = left_texture.get_width()

            while current_x < width - right_texture.get_width():
                self.image.blit(mid_texture, (current_x, 0))
                current_x += mid_width

            # Правый край
            self.image.blit(right_texture, (width - right_texture.get_width(), 0))
        else:
            # Если текстур нет, используем цвет с альфа-каналом
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((0, 255, 0, 255))  # Зеленый с полной непрозрачностью
            # Добавляем рамку для имитации текстуры
            pygame.draw.rect(self.image, (0, 100, 0, 255), (0, 0, width, height), 2)