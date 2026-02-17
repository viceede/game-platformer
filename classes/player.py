import pygame
from settings import *
from utils.sprite_sheet import SpriteLoader


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprites = SpriteLoader()
        self.animation_state = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing_right = True  # Для отражения спрайта

        # Загружаем анимации
        self.animations = {
            'idle': self.sprites.get_player_animation('idle'),
            'walk': self.sprites.get_player_animation('walk'),
            'jump': self.sprites.get_player_animation('jump'),
            'fall': self.sprites.get_player_animation('fall')
        }

        # Устанавливаем начальное изображение
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.coins_collected = 0
        self.bonus_points = 0
        self.start_x = x
        self.start_y = y

    @property
    def total_score(self):
        return self.coins_collected + self.bonus_points

    def handle_input(self, keys):
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15

    def update_animation(self):
        """Обновляет анимацию игрока"""
        self.animation_timer += 1

        # Определяем состояние анимации
        if not self.on_ground:
            if self.vel_y < 0:
                self.animation_state = 'jump'
            else:
                self.animation_state = 'fall'
        elif self.vel_x != 0:
            self.animation_state = 'walk'
        else:
            self.animation_state = 'idle'

        # Обновляем кадр анимации (каждые 10 тиков)
        if self.animation_timer >= 10:
            self.animation_timer = 0
            frames = self.animations[self.animation_state]
            if isinstance(frames, list):
                self.animation_frame = (self.animation_frame + 1) % len(frames)
                self.image = frames[self.animation_frame]
            else:
                self.image = frames

            # Отражение спрайта если нужно
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

    def update(self, platforms, enemies, coins):
        keys = pygame.key.get_pressed()
        self.handle_input(keys)
        self.apply_gravity()

        # движение по X
        self.rect.x += self.vel_x
        self.collide_x(platforms)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # движение по Y
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_y(platforms)

        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        # столкновения с врагами
        enemy_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hit_list:
            if self.vel_y > 0 and self.rect.bottom <= enemy.rect.centery + 10:
                enemy.kill()
                self.vel_y = JUMP_POWER / 1.5
                self.bonus_points += 5
            else:
                self.lives -= 1
                self.rect.topleft = (self.start_x, self.start_y)
                self.vel_y = 0

        # сбор монет
        coin_hit_list = pygame.sprite.spritecollide(self, coins, True)
        for _ in coin_hit_list:
            self.coins_collected += 1

        # Обновляем анимацию
        self.update_animation()

    def collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

    def collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0