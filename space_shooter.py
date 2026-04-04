"""
Space Shooter - Космический шутер
Игра с графикой, сохранением рекорда и работой с реестром Windows
"""

import pygame
import random
import math
import sys
import os

# Инициализация pygame
pygame.init()
pygame.mixer.init()

# Константы экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
CYAN = (50, 255, 255)
MAGENTA = (255, 50, 255)
ORANGE = (255, 150, 50)
PURPLE = (150, 50, 255)
DARK_BLUE = (10, 10, 40)
GRAY = (100, 100, 100)

# Работа с реестром Windows
def create_registry_entries():
    """Создает записи в реестре Windows"""
    try:
        import winreg
        # Создаем ключ реестра для игры
        key_path = r"Software\SpaceShooterGame"
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            
            # 10 различных значений для реестра
            values = {
                "GameName": "Space Shooter Deluxe",
                "Version": "1.0.0",
                "Author": "Game Developer",
                "MaxScore": get_high_score_from_file(),
                "TotalGamesPlayed": load_stat("total_games", 0),
                "TotalEnemiesDestroyed": load_stat("total_enemies", 0),
                "PlayerName": "Hero",
                "Difficulty": "Normal",
                "SoundEnabled": "True",
                "FullScreen": "False"
            }
            
            for name, value in values.items():
                if isinstance(value, int):
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                else:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Registry error: {e}")
            return False
    except ImportError:
        print("winreg not available (not on Windows)")
        return False

def get_high_score_from_file():
    """Получает максимальный счет из файла"""
    try:
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def save_high_score(score):
    """Сохраняет максимальный счет в файл"""
    current_high = get_high_score_from_file()
    if score > current_high:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
        return True
    return False

def load_stat(stat_name, default=0):
    """Загружает статистику из файла"""
    try:
        filename = f"{stat_name}.txt"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return int(f.read().strip())
    except:
        pass
    return default

def save_stat(stat_name, value):
    """Сохраняет статистику в файл"""
    with open(f"{stat_name}.txt", "w") as f:
        f.write(str(value))


class Particle:
    """Класс для частиц эффектов"""
    def __init__(self, x, y, color, speed=None, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        if speed is None:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            self.vx, self.vy = speed
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = tuple(min(255, c * alpha // 255) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Star:
    """Класс для звезд на фоне"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Player(pygame.sprite.Sprite):
    """Класс игрока"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
        self.draw_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 7
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.health = 100
        self.invincible = False
        self.invincible_timer = 0
    
    def draw_ship(self):
        """Рисует корабль игрока"""
        points = [(25, 0), (0, 50), (15, 40), (25, 55), (35, 40), (50, 50)]
        pygame.draw.polygon(self.image, CYAN, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)
        # Двигатель
        pygame.draw.ellipse(self.image, ORANGE, (18, 50, 14, 15))
        pygame.draw.ellipse(self.image, YELLOW, (20, 52, 10, 10))
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        # Ограничение по экрану
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Невидимость после попадания
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > 2000:
                self.invincible = False
            else:
                self.image.set_alpha(128 if (pygame.time.get_ticks() // 100) % 2 == 0 else 255)
        else:
            self.image.set_alpha(255)
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx, self.rect.top)
        return None
    
    def hit(self):
        if not self.invincible:
            self.health -= 25
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            return True
        return False


class Enemy(pygame.sprite.Sprite):
    """Класс врага"""
    def __init__(self, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.draw_enemy(enemy_type)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 40)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.uniform(2, 5) + enemy_type * 0.5
        self.speed_x = random.uniform(-1, 1)
        self.health = 1 + enemy_type
        self.score_value = 10 + enemy_type * 10
    
    def draw_enemy(self, enemy_type):
        """Рисует разные типы врагов"""
        colors = [RED, MAGENTA, PURPLE, ORANGE]
        color = colors[enemy_type % len(colors)]
        
        if enemy_type % 4 == 0:
            # Треугольник
            points = [(20, 0), (0, 40), (40, 40)]
            pygame.draw.polygon(self.image, color, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
        elif enemy_type % 4 == 1:
            # Квадрат
            pygame.draw.rect(self.image, color, (5, 5, 30, 30))
            pygame.draw.rect(self.image, WHITE, (5, 5, 30, 30), 2)
        elif enemy_type % 4 == 2:
            # Круг
            pygame.draw.circle(self.image, color, (20, 20), 18)
            pygame.draw.circle(self.image, WHITE, (20, 20), 18, 2)
        else:
            # Ромб
            points = [(20, 0), (40, 20), (20, 40), (0, 20)]
            pygame.draw.polygon(self.image, color, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
        
        # Глаза
        pygame.draw.circle(self.image, WHITE, (12, 15), 5)
        pygame.draw.circle(self.image, WHITE, (28, 15), 5)
        pygame.draw.circle(self.image, BLACK, (12, 15), 2)
        pygame.draw.circle(self.image, BLACK, (28, 15), 2)
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    """Класс пули"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 20))
        pygame.draw.rect(self.image, WHITE, (2, 0, 2, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    """Класс бонусов"""
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(["health", "speed", "multishot"])
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.draw_powerup()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 3
    
    def draw_powerup(self):
        colors = {"health": GREEN, "speed": BLUE, "multishot": MAGENTA}
        symbols = {"health": "+", "speed": ">>", "multishot": "*"}
        color = colors.get(self.type, WHITE)
        
        pygame.draw.circle(self.image, color, (15, 15), 14)
        pygame.draw.circle(self.image, WHITE, (15, 15), 14, 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render(symbols.get(self.type, "?"), True, WHITE)
        text_rect = text.get_rect(center=(15, 15))
        self.image.blit(text, text_rect)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Game:
    """Основной класс игры"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter - Космический Шутер")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Создание звездного фона
        self.stars = [Star() for _ in range(100)]
        
        self.reset_game()
        
        # Попытка создать записи в реестре
        self.registry_created = create_registry_entries()
        
        # Загрузка рекорда
        self.high_score = get_high_score_from_file()
    
    def reset_game(self):
        """Сброс игры"""
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = []
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1500
        
        # Обновление статистики
        total_games = load_stat("total_games", 0) + 1
        save_stat("total_games", total_games)
    
    def spawn_enemy(self):
        """Создание врага"""
        enemy_type = min(self.level - 1, 3)
        if random.random() < 0.3:
            enemy_type = random.randint(0, min(self.level, 4))
        
        enemy = Enemy(enemy_type)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
    
    def create_explosion(self, x, y, color, count=15):
        """Создание взрыва"""
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        return False
                    self.paused = not self.paused
                
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                    bullet = self.player.shoot()
                    if bullet:
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)
        
        return True
    
    def update(self):
        """Обновление игры"""
        if self.game_over or self.paused:
            return
        
        # Обновление звезд
        for star in self.stars:
            star.update()
        
        # Обновление спрайтов
        self.all_sprites.update()
        
        # Обновление частиц
        self.particles = [p for p in self.particles if p.update()]
        
        # Спавн врагов
        self.enemy_spawn_timer += self.clock.get_time()
        if self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()
            # Усложнение со временем
            self.enemy_spawn_delay = max(500, 1500 - self.level * 100)
        
        # Проверка попаданий пуль во врагов
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= len(bullets)
            if enemy.health <= 0:
                self.create_explosion(enemy.rect.centerx, enemy.rect.centery, 
                                    RED if enemy.enemy_type == 0 else MAGENTA)
                self.score += enemy.score_value
                
                # Обновление статистики
                total_enemies = load_stat("total_enemies", 0) + 1
                save_stat("total_enemies", total_enemies)
                
                # Шанс выпадения бонуса
                if random.random() < 0.1:
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
                
                enemy.kill()
                
                # Повышение уровня
                if self.score >= self.level * 100:
                    self.level += 1
        
        # Проверка столкновений игрока с врагами
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for enemy in hits:
            if self.player.hit():
                self.create_explosion(self.player.rect.centerx, self.player.rect.centery, RED, 20)
            self.create_explosion(enemy.rect.centerx, enemy.rect.centery, RED)
            self.score += enemy.score_value
        
        # Проверка получения бонусов
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            if powerup.type == "health":
                self.player.health = min(100, self.player.health + 25)
            elif powerup.type == "speed":
                self.player.speed = min(12, self.player.speed + 1)
            elif powerup.type == "multishot":
                self.player.shoot_delay = max(100, self.player.shoot_delay - 50)
            self.score += 50
        
        # Проверка конца игры
        if self.player.health <= 0:
            self.game_over = True
            self.create_explosion(self.player.rect.centerx, self.player.rect.centery, CYAN, 30)
            
            # Сохранение рекорда (только если новый рекорд!)
            save_high_score(self.score)
            
            # Обновление реестра с новым рекордом
            create_registry_entries()
    
    def draw(self):
        """Отрисовка"""
        self.screen.fill(DARK_BLUE)
        
        # Рисуем звезды
        for star in self.stars:
            star.draw(self.screen)
        
        # Рисуем спрайты
        self.all_sprites.draw(self.screen)
        
        # Рисуем частицы
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Интерфейс
        self.draw_ui()
        
        if self.paused:
            self.draw_paused()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Отрисовка интерфейса"""
        # Счет
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Уровень
        level_text = self.font.render(f"Уровень: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 45))
        
        # Здоровье
        health_text = self.font.render(f"Здоровье: {self.player.health}%", True, 
                                       GREEN if self.player.health > 50 else RED)
        self.screen.blit(health_text, (10, 80))
        
        # Полоска здоровья
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 110
        fill = (self.player.health / 100) * bar_width
        
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN if self.player.health > 50 else RED, 
                        (bar_x, bar_y, fill, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Рекорд
        high_score_text = self.font.render(f"Рекорд: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 200, 10))
        
        # Информация о реестре
        if self.registry_created:
            reg_text = pygame.font.Font(None, 20).render("Реестр: OK", True, GREEN)
            self.screen.blit(reg_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 25))
    
    def draw_paused(self):
        """Отрисовка паузы"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.big_font.render("ПАУЗА", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        resume_text = self.font.render("Нажмите ESC для продолжения", True, WHITE)
        text_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, text_rect)
    
    def draw_game_over(self):
        """Отрисовка конца игры"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        final_score_text = self.font.render(f"Ваш счет: {self.score}", True, WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(final_score_text, text_rect)
        
        # Проверка нового рекорда
        if self.score >= self.high_score and self.score > 0:
            record_text = self.font.render("НОВЫЙ РЕКОРД!", True, YELLOW)
            text_rect = record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(record_text, text_rect)
        
        restart_text = self.font.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)
        text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, text_rect)
    
    def run(self):
        """Запуск игрового цикла"""
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("=" * 50)
    print("SPACE SHOOTER - КОСМИЧЕСКИЙ ШУТЕР")
    print("=" * 50)
    print("\nУправление:")
    print("  Стрелки / WASD - движение")
    print("  Пробел - стрельба")
    print("  ESC - пауза/выход")
    print("  R - рестарт (после проигрыша)")
    print("\nОсобенности:")
    print("  ✓ Красивая графика с эффектами частиц")
    print("  ✓ Звездный фон с параллаксом")
    print("  ✓ Разные типы врагов")
    print("  ✓ Бонусы (здоровье, скорость, мульти-выстрел)")
    print("  ✓ Система уровней сложности")
    print("  ✓ Сохранение рекорда (не перезаписывается!)")
    print("  ✓ Создание записей в реестре Windows (10 значений)")
    print("=" * 50)
    
    game = Game()
    game.run()
