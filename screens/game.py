import pygame
from settings import *
from classes import Player, Platform, Enemy, Coin
from utils import show_message


def create_game_objects():
    """Создает все игровые объекты для нового запуска"""
    player = Player(100, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT)
    player.coins_collected = 0
    player.bonus_points = 0
    player.lives = 3

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

    return player, platforms, enemies, coins, all_sprites


def game_loop():
    """Основной игровой цикл"""
    from main import WIN, CLOCK

    player, platforms, enemies, coins, all_sprites = create_game_objects()

    font = pygame.font.SysFont(None, 28)
    victory_font = pygame.font.SysFont(None, 72)

    victory = False
    game_over = False

    running = True
    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_r and (game_over or victory):
                    return "restart"

        # Обновление анимаций монет
        coins.update()

        # Проверка условий победы
        if len(enemies) == 0 and not victory and player.lives > 0:
            victory = True

        if player.lives <= 0:
            game_over = True

        if game_over:
            WIN.fill(BLACK)
            show_message(WIN, "GAME OVER", RED, 72, -30)
            show_message(WIN, "Нажмите R для рестарта или Esc для меню", WHITE, 28, 30)
            pygame.display.flip()
            continue

        if victory:
            WIN.fill(SKY_BLUE)
            all_sprites.draw(WIN)
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            WIN.blit(s, (0, 0))

            victory_text = victory_font.render("ПОБЕДА!", True, YELLOW)
            victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            WIN.blit(victory_text, victory_rect)

            show_message(WIN, f"Монет собрано: {player.coins_collected}", WHITE, 36, 20)
            show_message(WIN, "Нажмите R для рестарта или Esc для меню", WHITE, 24, 60)

            pygame.display.flip()
            continue

        # обновление
        enemies.update()
        player.update(platforms, enemies, coins)

        # отрисовка
        WIN.fill(SKY_BLUE)
        all_sprites.draw(WIN)

        # HUD
        coins_text = font.render(f"Монеты: {player.coins_collected}", True, BLACK)
        lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
        coins_left_text = font.render(f"Осталось монет: {len(coins)}", True, BLACK)
        enemies_left_text = font.render(f"Врагов: {len(enemies)}", True, BLACK)
        total_text = font.render(f"Всего очков: {player.total_score}", True, BLACK)
        menu_hint = font.render("ESC - меню", True, BLACK)

        WIN.blit(coins_text, (10, 10))
        WIN.blit(lives_text, (10, 35))
        WIN.blit(coins_left_text, (10, 60))
        WIN.blit(enemies_left_text, (10, 85))
        WIN.blit(total_text, (10, 110))

        menu_hint_rect = menu_hint.get_rect(topright=(WIDTH - 10, 10))
        WIN.blit(menu_hint, menu_hint_rect)

        pygame.display.flip()

    return "quit"