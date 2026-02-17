import pygame
import sys

pygame.init()

# --- настройки окна ---
WIDTH, HEIGHT = 800, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gabeitch")

FPS = 60
CLOCK = pygame.time.Clock()

# --- цвета ---
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (240, 220, 50)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)

# --- параметры игрока ---
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
PLAYER_SPEED = 5
JUMP_POWER = -12
GRAVITY = 0.6

# --- платформы, монеты, враги ---
GROUND_HEIGHT = 60


class Button:
    """Класс для создания интерактивных кнопок"""

    def __init__(self, x, y, width, height, text, color=GRAY, hover_color=DARK_GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen, font):
        # Изменяем цвет при наведении
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # Рамка

        # Рисуем текст
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click[0]


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
        self.start_x = x
        self.start_y = y

    def handle_input(self, keys):
        self.vel_x = 0
        # Управление на WASD
        if keys[pygame.K_a]:  # Влево
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_d]:  # Вправо
            self.vel_x = PLAYER_SPEED
        # Прыжок на пробел (можно также добавить W для прыжка)
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
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

        # проверка выхода за левую и правую границы карты
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # движение по Y
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_y(platforms)

        # проверка выхода за верхнюю границу
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        # столкновения с врагами
        enemy_hit_list = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hit_list:
            # если сверху — убиваем врага
            if self.vel_y > 0 and self.rect.bottom <= enemy.rect.centery + 10:
                enemy.kill()
                self.vel_y = JUMP_POWER / 1.5
                self.score += 5  # бонус за убийство врага
            else:
                # иначе теряем жизнь и откатываемся
                self.lives -= 1
                self.rect.topleft = (self.start_x, self.start_y)
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


def show_message(screen, message, color, size=48, y_offset=0):
    """Отображает сообщение в центре экрана"""
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)


def show_rules(screen, font, start_y=150):
    """Отображает правила игры"""
    rules = [
        "ПРАВИЛА ИГРЫ:",
        "1. Убейте врага, прыгнув ему на голову - это главная цель!",
        "2. Собирайте монеты для получения дополнительных очков",
        "3. У вас 3 жизни",
        "4. При касании врага сбоку или снизу - теряете жизнь",
        "",
        "ЦЕЛЬ: Убить врага (монеты - для счета)"
    ]
    for i, text in enumerate(rules):
        if i == 0:  # Заголовок
            rule_text = font.render(text, True, ORANGE)
            screen.blit(rule_text, (WIDTH // 2 - 250, start_y + i * 30))
        else:
            rule_text = font.render(text, True, BLACK)
            screen.blit(rule_text, (WIDTH // 2 - 250, start_y + i * 30))


def main_menu():
    """Главное меню игры"""
    menu_font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 28)
    title_font = pygame.font.SysFont(None, 72)

    # Создание кнопок
    start_button = Button(WIDTH // 2 - 100, 250, 200, 50, "Начать игру")
    rules_button = Button(WIDTH // 2 - 100, 320, 200, 50, "Правила")
    quit_button = Button(WIDTH // 2 - 100, 390, 200, 50, "Выйти")

    show_rules_screen = False
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_rules_screen:
                        show_rules_screen = False
                    else:
                        running = False

        # Проверка наведения на кнопки
        if not show_rules_screen:
            start_button.check_hover(mouse_pos)
            rules_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)

            # Обработка нажатий на кнопки
            if start_button.is_clicked(mouse_pos, mouse_click):
                return "start"  # Начать игру
            if rules_button.is_clicked(mouse_pos, mouse_click):
                show_rules_screen = True
            if quit_button.is_clicked(mouse_pos, mouse_click):
                pygame.quit()
                sys.exit()

        # Отрисовка
        WIN.fill(SKY_BLUE)

        # Заголовок игры
        title_text = title_font.render("Gabeitch", True, BLUE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
        WIN.blit(title_text, title_rect)

        if show_rules_screen:
            # Экран с правилами
            show_rules(WIN, small_font, 150)

            # Подсказка для возврата
            back_text = small_font.render("Нажмите ESC для возврата в меню", True, DARK_GRAY)
            back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            WIN.blit(back_text, back_rect)
        else:
            # Краткое описание под заголовком
            subtitle_text = small_font.render("Платформер с монетами и врагами", True, BLACK)
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, 140))
            WIN.blit(subtitle_text, subtitle_rect)

            # Отрисовка кнопок главного меню
            start_button.draw(WIN, menu_font)
            rules_button.draw(WIN, menu_font)
            quit_button.draw(WIN, menu_font)

            # Краткие правила под кнопками
            quick_rules = [
                "• Главная цель: Убить врага (прыжком сверху)",
                "• Монеты - дополнительные очки",
                "• У вас 3 жизни"
            ]
            for i, rule in enumerate(quick_rules):
                rule_text = small_font.render(rule, True, BLACK)
                WIN.blit(rule_text, (WIDTH // 2 - 150, 460 + i * 25))

        pygame.display.flip()
        CLOCK.tick(FPS)

    return "quit"


def game_loop():
    """Основной игровой цикл"""
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
                    return "menu"  # ESC всегда возвращает в меню
                if event.key == pygame.K_r and (game_over or victory):
                    # Перезапуск игры
                    return "restart"

        # Проверка условий победы (главное условие - убийство врага)
        if len(enemies) == 0 and not victory and player.lives > 0:
            victory = True

        # Проверка поражения
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
            # Затемняющий overlay
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            WIN.blit(s, (0, 0))

            victory_text = victory_font.render("ПОБЕДА!", True, YELLOW)
            victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            WIN.blit(victory_text, victory_rect)

            show_message(WIN, f"Монет собрано: {player.score}", WHITE, 36, 20)
            show_message(WIN, "Нажмите R для рестарта или Esc для меню", WHITE, 24, 60)

            pygame.display.flip()
            continue

        # обновление
        enemies.update()
        player.update(platforms, enemies, coins)

        # отрисовка
        WIN.fill(SKY_BLUE)  # небо
        all_sprites.draw(WIN)

        # HUD - расположение как на скриншоте
        score_text = font.render(f"Монеты: {player.score}", True, BLACK)
        lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
        coins_left_text = font.render(f"Осталось монет: {len(coins)}", True, BLACK)
        enemies_left_text = font.render(f"Врагов: {len(enemies)}", True, BLACK)
        menu_hint = font.render("ESC - меню", True, BLACK)

        # Размещаем текст слева сверху
        WIN.blit(score_text, (10, 10))
        WIN.blit(lives_text, (10, 35))
        WIN.blit(coins_left_text, (10, 60))
        WIN.blit(enemies_left_text, (10, 85))

        # ESC - меню в правом верхнем углу
        menu_hint_rect = menu_hint.get_rect(topright=(WIDTH - 10, 10))
        WIN.blit(menu_hint, menu_hint_rect)

        pygame.display.flip()

    return "quit"


def main():
    """Главная функция программы"""
    while True:
        menu_result = main_menu()

        if menu_result == "quit":
            break
        elif menu_result == "start":
            game_result = game_loop()

            while game_result == "restart":
                game_result = game_loop()

            if game_result == "quit":
                break
            # Если "menu" - возвращаемся в главное меню

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()