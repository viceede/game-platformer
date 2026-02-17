import pygame
import sys

pygame.init()

# --- настройки окна ---
WIDTH, HEIGHT = 800, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Mario-like")

FPS = 60
CLOCK = pygame.time.Clock()

# --- цвета ---
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (240, 220, 50)
BLACK = (0, 0, 0)

# --- параметры игрока ---
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
PLAYER_SPEED = 5
JUMP_POWER = -12
GRAVITY = 0.6

# --- платформы, монеты, враги ---
GROUND_HEIGHT = 60

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0

    def handle_input(self, keys):
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15

    def update(self, platforms, enemies, coins):
        keys = pygame.key.get_pressed()
        self.handle_input(keys)
        self.apply_gravity()

        # движение по X
        self.rect.x += self.vel_x
        self.collide_x(platforms)

        # движение по Y
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_y(platforms)

        # столкновения с врагами
        enemy_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hit_list:
            # если сверху — убиваем врага
            if self.vel_y > 0 and self.rect.bottom <= enemy.rect.centery:
                enemy.kill()
                self.vel_y = JUMP_POWER / 1.5
            else:
                # иначе теряем жизнь и откатываемся
                self.lives -= 1
                self.rect.topleft = (100, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT)
                self.vel_y = 0

        # сбор монет
        coin_hit_list = pygame.sprite.spritecollide(self, coins, True)
        for _ in coin_hit_list:
            self.score += 1

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


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_bound, right_bound, speed=2):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.speed *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))


def main():
    player = Player(100, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT)

    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    # земля
    ground = Platform(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT, color=BLACK)
    platforms.add(ground)
    all_sprites.add(ground)

    # несколько платформ
    level_platforms = [
        Platform(200, 360, 120, 20),
        Platform(380, 300, 120, 20),
        Platform(560, 260, 120, 20),
        Platform(350, 420, 80, 20),
    ]
    for p in level_platforms:
        platforms.add(p)
        all_sprites.add(p)

    # враг
    enemy = Enemy(420, HEIGHT - GROUND_HEIGHT - 40, 380, 560)
    enemies.add(enemy)
    all_sprites.add(enemy)

    # монеты
    coin_positions = [(230, 330), (410, 270), (590, 230), (380, 390)]
    for cx, cy in coin_positions:
        c = Coin(cx, cy)
        coins.add(c)
        all_sprites.add(c)

    all_sprites.add(player)

    font = pygame.font.SysFont(None, 28)

    running = True
    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if player.lives <= 0:
            WIN.fill(BLACK)
            text = font.render("GAME OVER (Esc - выйти)", True, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
            continue

        # обновление
        enemies.update()
        player.update(platforms, enemies, coins)

        # отрисовка
        WIN.fill((135, 206, 235))  # небо
        all_sprites.draw(WIN)

        # HUD
        score_text = font.render(f"Монеты: {player.score}", True, BLACK)
        lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
        WIN.blit(score_text, (10, 10))
        WIN.blit(lives_text, (10, 35))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
