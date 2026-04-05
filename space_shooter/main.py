#!/usr/bin/env python3
"""
Космический шутер "Крестики в космосе"
Игрок управляет кораблем-крестиком, стреляет по врагам
Сохранение рекорда в ~/.space_shooter/settings.json
"""

import pygame
import json
import os
import random
import math
from pathlib import Path

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (150, 0, 255)

# Пути
SETTINGS_DIR = Path.home() / ".space_shooter"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# Создание папки настроек
SETTINGS_DIR.mkdir(exist_ok=True)

# Загрузка/сохранение настроек
def load_settings():
    default_settings = {
        "high_score": 0,
        "volume": 70,
        "difficulty": "normal",
        "player_speed": 5,
        "bullet_speed": 7,
        "enemy_speed": 2,
        "spawn_rate": 60,
        "player_color": [0, 255, 255],
        "bullet_color": [255, 255, 0],
        "bg_color": [0, 0, 30],
        "show_fps": False,
        "sound_enabled": True
    }
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Обновляем только существующие ключи, сохраняя структуру
                for key in default_settings:
                    if key not in settings:
                        settings[key] = default_settings[key]
                return settings
        except:
            pass
    
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

# Генерация звуков программно (без внешних файлов)
def generate_sound(frequency, duration, wave_type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    buf = bytearray(n_samples * 2)
    
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'sine':
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * t))
        elif wave_type == 'square':
            value = int(32767 * 0.3 * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1))
        elif wave_type == 'noise':
            value = int(32767 * 0.3 * (random.random() * 2 - 1))
        else:
            value = 0
        
        # Затухание
        decay = 1.0 - (i / n_samples)
        value = int(value * decay)
        
        buf[i * 2] = value & 0xFF
        buf[i * 2 + 1] = (value >> 8) & 0xFF
    
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    return sound

# Создание звуков
shoot_sound = None
explosion_sound = None
hit_sound = None
game_over_sound = None

try:
    shoot_sound = generate_sound(800, 0.1, 'square')
    explosion_sound = generate_sound(150, 0.3, 'noise')
    hit_sound = generate_sound(600, 0.15, 'sine')
    game_over_sound = generate_sound(200, 0.5, 'sine')
except Exception as e:
    print(f"Звуки не доступны: {e}")

class Player(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.color = tuple(settings.get("player_color", [0, 255, 255]))
        self.draw_player()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = settings.get("player_speed", 5)
        self.lives = 3
        
    def draw_player(self):
        """Рисуем игрока как большой заметный крестик с деталями"""
        self.image.fill((0, 0, 0, 0))
        color = self.color
        
        # Основной корпус (крест)
        thickness = 8
        # Вертикальная линия
        pygame.draw.line(self.image, color, (20, 5), (20, 35), thickness)
        # Горизонтальная линия
        pygame.draw.line(self.image, color, (5, 20), (35, 20), thickness)
        
        # Центр (яркое ядро)
        pygame.draw.circle(self.image, YELLOW, (20, 20), 6)
        pygame.draw.circle(self.image, WHITE, (20, 20), 3)
        
        # Двигатели (свечение сзади)
        pygame.draw.circle(self.image, RED, (15, 35), 4)
        pygame.draw.circle(self.image, RED, (25, 35), 4)
        
        # Крылья
        pygame.draw.polygon(self.image, color, [(5, 15), (5, 25), (15, 20)])
        pygame.draw.polygon(self.image, color, [(35, 15), (35, 25), (25, 20)])
        
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
            
        # Ограничение экраном
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, settings):
        super().__init__()
        self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
        color = tuple(settings.get("bullet_color", [255, 255, 0]))
        pygame.draw.rect(self.image, color, (0, 0, 6, 15))
        pygame.draw.rect(self.image, WHITE, (2, 0, 2, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = settings.get("bullet_speed", 7)
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        colors = [RED, PURPLE, GREEN, ORANGE if 'ORANGE' in globals() else (255, 165, 0)]
        self.color = random.choice(colors)
        self.draw_enemy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-50, -20)
        self.speed = settings.get("enemy_speed", 2) + random.random()
        
    def draw_enemy(self):
        """Рисуем врага как зловещий крестик"""
        self.image.fill((0, 0, 0, 0))
        
        # Злой крест
        pygame.draw.line(self.image, self.color, (5, 5), (30, 30), 6)
        pygame.draw.line(self.image, self.color, (30, 5), (5, 30), 6)
        
        # Злые глаза
        pygame.draw.circle(self.image, YELLOW, (12, 15), 4)
        pygame.draw.circle(self.image, YELLOW, (23, 15), 4)
        pygame.draw.circle(self.image, BLACK, (12, 15), 2)
        pygame.draw.circle(self.image, BLACK, (23, 15), 2)
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (self.x, self.y), self.size)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Космический Шутер: Крестики")
        self.clock = pygame.time.Clock()
        self.settings = load_settings()
        self.running = True
        self.game_active = False
        self.score = 0
        self.high_score = self.settings.get("high_score", 0)
        self.frame_count = 0
        
        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Игрок
        self.player = Player(self.settings)
        self.all_sprites.add(self.player)
        
        # Звезды
        self.stars = [Star() for _ in range(100)]
        
        # Шрифт
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Меню настройки
        self.settings_menu = False
        self.selected_setting = 0
        self.setting_keys = list(self.settings.keys())
        
    def spawn_enemy(self):
        enemy = Enemy(self.settings)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        
    def play_sound(self, sound):
        if sound and self.settings.get("sound_enabled", True):
            volume = self.settings.get("volume", 70) / 100
            sound.set_volume(volume)
            sound.play()
        
    def show_start_screen(self):
        bg_color = tuple(self.settings.get("bg_color", [0, 0, 30]))
        self.screen.fill(bg_color)
        
        # Звезды
        for star in self.stars:
            star.draw(self.screen)
        
        title = self.big_font.render("КОСМИЧЕСКИЙ ШУТЕР", True, CYAN)
        subtitle = self.font.render("КРЕСТИКИ В КОСМОСЕ", True, WHITE)
        start_text = self.font.render("Нажмите ПРОБЕЛ для старта", True, GREEN)
        settings_text = self.font.render("Нажмите S для настроек", True, YELLOW)
        quit_text = self.font.render("Нажмите ESC для выхода", True, RED)
        high_score_text = self.font.render(f"Рекорд: {self.high_score}", True, YELLOW)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 220))
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 300))
        self.screen.blit(settings_text, (SCREEN_WIDTH//2 - settings_text.get_width()//2, 360))
        self.screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 420))
        
        # Рисуем игрока для демонстрации
        demo_player = Player(self.settings)
        demo_player.rect.centerx = SCREEN_WIDTH // 2
        demo_player.rect.centery = 500
        self.screen.blit(demo_player.image, demo_player.rect)
        
        pygame.display.flip()
        
    def show_settings_screen(self):
        bg_color = tuple(self.settings.get("bg_color", [0, 0, 30]))
        self.screen.fill(bg_color)
        
        title = self.big_font.render("НАСТРОЙКИ", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Список настроек (только те, которые можно менять)
        editable_settings = [
            ("volume", "Громкость"),
            ("player_speed", "Скорость игрока"),
            ("bullet_speed", "Скорость пули"),
            ("enemy_speed", "Скорость врагов"),
            ("spawn_rate", "Частота появления"),
            ("show_fps", "Показать FPS"),
            ("sound_enabled", "Звук вкл/выкл"),
        ]
        
        for i, (key, name) in enumerate(editable_settings):
            if i == self.selected_setting:
                color = YELLOW
                marker = "> "
            else:
                color = WHITE
                marker = "  "
                
            value = self.settings.get(key)
            if isinstance(value, bool):
                value_str = "ВКЛ" if value else "ВЫКЛ"
            else:
                value_str = str(value)
                
            text = self.font.render(f"{marker}{name}: {value_str}", True, color)
            self.screen.blit(text, (100, 150 + i * 40))
        
        help_text = self.font.render("Стрелки ВВЕРХ/ВНИЗ - выбор, ВЛЕВО/ВПРАВО - изменение", True, GREEN)
        back_text = self.font.render("Нажмите ESC для возврата", True, CYAN)
        self.screen.blit(help_text, (100, 450))
        self.screen.blit(back_text, (100, 500))
        
        pygame.display.flip()
        
    def handle_settings_input(self, event):
        editable_settings = [key for key, _ in [
            ("volume", "Громкость"),
            ("player_speed", "Скорость игрока"),
            ("bullet_speed", "Скорость пули"),
            ("enemy_speed", "Скорость врагов"),
            ("spawn_rate", "Частота появления"),
            ("show_fps", "Показать FPS"),
            ("sound_enabled", "Звук вкл/выкл"),
        ]]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_setting = (self.selected_setting - 1) % len(editable_settings)
            elif event.key == pygame.K_DOWN:
                self.selected_setting = (self.selected_setting + 1) % len(editable_settings)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                key = editable_settings[self.selected_setting]
                value = self.settings.get(key)
                
                if isinstance(value, bool):
                    self.settings[key] = not value
                elif event.key == pygame.K_RIGHT:
                    if key == "volume":
                        self.settings[key] = min(100, value + 5)
                    elif key == "player_speed":
                        self.settings[key] = min(10, value + 1)
                    elif key == "bullet_speed":
                        self.settings[key] = min(15, value + 1)
                    elif key == "enemy_speed":
                        self.settings[key] = min(8, value + 1)
                    elif key == "spawn_rate":
                        self.settings[key] = min(120, value + 5)
                elif event.key == pygame.K_LEFT:
                    if key == "volume":
                        self.settings[key] = max(0, value - 5)
                    elif key == "player_speed":
                        self.settings[key] = max(1, value - 1)
                    elif key == "bullet_speed":
                        self.settings[key] = max(3, value - 1)
                    elif key == "enemy_speed":
                        self.settings[key] = max(1, value - 1)
                    elif key == "spawn_rate":
                        self.settings[key] = max(20, value - 5)
                
                # Сохраняем настройки (кроме рекорда)
                save_settings(self.settings)
                
                # Применяем изменения
                self.player.speed = self.settings.get("player_speed", 5)
                
    def show_game_over(self):
        # Обновляем рекорд ТОЛЬКО если текущий счет больше
        if self.score > self.high_score:
            self.high_score = self.score
            self.settings["high_score"] = self.high_score
            save_settings(self.settings)
        
        bg_color = tuple(self.settings.get("bg_color", [0, 0, 30]))
        self.screen.fill(bg_color)
        
        game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"Рекорд: {self.high_score}", True, YELLOW)
        restart_text = self.font.render("Нажмите ПРОБЕЛ для рестарта", True, GREEN)
        menu_text = self.font.render("Нажмите ESC для меню", True, CYAN)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 300))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 400))
        self.screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 460))
        
        pygame.display.flip()
        
        self.play_sound(game_over_sound)
        
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if not self.game_active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.settings_menu:
                                self.settings_menu = False
                            else:
                                self.running = False
                        elif event.key == pygame.K_s and not self.settings_menu:
                            self.settings_menu = True
                        elif event.key == pygame.K_SPACE:
                            if self.settings_menu:
                                self.settings_menu = False
                            else:
                                self.start_game()
                    elif self.settings_menu:
                        self.handle_settings_input(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            bullet = Bullet(self.player.rect.centerx, self.player.rect.top, self.settings)
                            self.all_sprites.add(bullet)
                            self.bullets.add(bullet)
                            self.play_sound(shoot_sound)
            
            # Обновление
            if self.settings_menu:
                self.show_settings_screen()
            elif not self.game_active:
                self.show_start_screen()
                # Обновляем звезды даже в меню
                for star in self.stars:
                    star.update()
            else:
                self.update_game()
                self.draw_game()
            
            pygame.display.flip()
        
        pygame.quit()
        
    def start_game(self):
        self.game_active = True
        self.score = 0
        self.frame_count = 0
        
        # Очищаем все спрайты
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemies.empty()
        
        # Создаем нового игрока
        self.player = Player(self.settings)
        self.all_sprites.add(self.player)
        
    def update_game(self):
        # Обновление звезд
        for star in self.stars:
            star.update()
        
        # Обновление спрайтов
        self.all_sprites.update()
        
        # Спавн врагов
        spawn_rate = self.settings.get("spawn_rate", 60)
        self.frame_count += 1
        if self.frame_count % spawn_rate == 0:
            self.spawn_enemy()
        
        # Проверка попаданий
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 10
            self.play_sound(explosion_sound)
        
        # Проверка столкновений с игроком
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.lives -= 1
            self.play_sound(hit_sound)
            if self.player.lives <= 0:
                self.game_active = False
        
        # Проверка выхода за экран
        for enemy in self.enemies:
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()
                
    def draw_game(self):
        bg_color = tuple(self.settings.get("bg_color", [0, 0, 30]))
        self.screen.fill(bg_color)
        
        # Рисуем звезды
        for star in self.stars:
            star.draw(self.screen)
        
        # Рисуем все спрайты
        self.all_sprites.draw(self.screen)
        
        # Интерфейс
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Жизни: {self.player.lives}", True, RED)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        
        if self.settings.get("show_fps", False):
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, GREEN)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 150, 10))

if __name__ == "__main__":
    game = Game()
    game.run()
