#!/usr/bin/env python3
"""
Игра с графикой, звуком и настройками через интерфейс.
Для Linux - использует файл конфигурации вместо реестра.
Сохраняет 10 различных значений, рекорд не сбрасывается при запуске.
"""

import pygame
import json
import os
import random
import sys

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (135, 206, 235)

# Пути для Linux (файл конфигурации вместо реестра)
CONFIG_DIR = os.path.expanduser("~/.my_game")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Значения по умолчанию (10 параметров)
DEFAULT_SETTINGS = {
    "volume": 50,              # Громкость звука (0-100)
    "music_volume": 30,        # Громкость музыки (0-100)
    "difficulty": 2,           # Сложность (1-5)
    "player_speed": 5,         # Скорость игрока (1-10)
    "enemy_speed": 3,          # Скорость врагов (1-10)
    "max_enemies": 5,          # Максимум врагов (1-20)
    "player_color": [0, 0, 255],  # Цвет игрока (RGB)
    "background_color": [0, 0, 0],  # Цвет фона (RGB)
    "show_fps": True,          # Показывать FPS
    "fullscreen": False,       # Полноэкранный режим
    "high_score": 0            # Рекорд (НЕ меняется случайно!)
}


class SettingsManager:
    """Менеджер настроек - работает как реестр в Windows"""
    
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Обновляем только существующие ключи, сохраняем структуру
                    for key in self.settings:
                        if key in loaded and key != "high_score":
                            self.settings[key] = loaded[key]
                    # high_score берём из файла если есть, иначе оставляем 0
                    if "high_score" in loaded:
                        self.settings["high_score"] = loaded["high_score"]
                print(f"Настройки загружены из {CONFIG_FILE}")
            else:
                # Создаём директорию и файл с настройками по умолчанию
                os.makedirs(CONFIG_DIR, exist_ok=True)
                self.save_settings()
                print(f"Создана папка с настройками: {CONFIG_DIR}")
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.settings = DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Настройки сохранены в {CONFIG_FILE}")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get(self, key, default=None):
        """Получает значение параметра"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Устанавливает значение параметра (кроме high_score)"""
        if key == "high_score":
            print("Предупреждение: high_score нельзя изменить через интерфейс!")
            return False
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
            return True
        return False
    
    def update_high_score(self, score):
        """Обновляет рекорд ТОЛЬКО если новый счет больше текущего"""
        if score > self.settings["high_score"]:
            self.settings["high_score"] = score
            self.save_settings()
            print(f"Новый рекорд: {score}")
            return True
        return False


class SoundManager:
    """Менеджер звука"""
    
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.sounds = {}
        self.music_playing = False
        
    def generate_beep_sound(self, frequency=440, duration=0.1):
        """Генерирует простой звук (синусоидальная волна)"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        
        import math
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            value = int(127 * math.sin(2 * math.pi * frequency * t))
            buf.append(value + 128)
        
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(self.settings.get("volume", 50) / 100.0)
        return sound
    
    def play_click(self):
        """Воспроизводит звук клика"""
        if "click" not in self.sounds:
            self.sounds["click"] = self.generate_beep_sound(800, 0.05)
        self.sounds["click"].play()
    
    def play_score(self):
        """Воспроизводит звук получения очка"""
        if "score" not in self.sounds:
            self.sounds["score"] = self.generate_beep_sound(1000, 0.1)
        self.sounds["score"].play()
    
    def play_game_over(self):
        """Воспроизводит звук конца игры"""
        if "gameover" not in self.sounds:
            self.sounds["gameover"] = self.generate_beep_sound(200, 0.3)
        self.sounds["gameover"].play()


class Button:
    """Кнопка интерфейса"""
    
    def __init__(self, x, y, width, height, text, color=GRAY, hover_color=LIGHT_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class Slider:
    """Ползунок для настройки значений"""
    
    def __init__(self, x, y, width, min_val, max_val, current_val, label=""):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = current_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 28)
    
    def get_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.left + int(ratio * (self.rect.width - 20))
    
    def draw(self, screen):
        # Рисуем фон ползунка
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Рисуем ручку
        handle_x = self.get_handle_pos()
        handle_rect = pygame.Rect(handle_x, self.rect.top - 5, 20, 30)
        pygame.draw.rect(screen, LIGHT_BLUE, handle_rect)
        pygame.draw.rect(screen, WHITE, handle_rect, 2)
        
        # Рисуем метку и значение
        label_surface = self.font.render(f"{self.label}: {int(self.value)}", True, WHITE)
        screen.blit(label_surface, (self.rect.left, self.rect.top - 30))
    
    def check_drag(self, mouse_pos, mouse_pressed):
        handle_x = self.get_handle_pos()
        handle_rect = pygame.Rect(handle_x - 5, self.rect.top - 5, 30, 30)
        
        if mouse_pressed and handle_rect.collidepoint(mouse_pos):
            self.dragging = True
        elif not mouse_pressed:
            self.dragging = False
        
        if self.dragging:
            ratio = (mouse_pos[0] - self.rect.left) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
            return True
        return False


class ColorPicker:
    """Выбор цвета"""
    
    def __init__(self, x, y, current_color, label=""):
        self.rect = pygame.Rect(x, y, 50, 30)
        self.color = list(current_color)
        self.label = label
        self.font = pygame.font.Font(None, 28)
    
    def draw(self, screen):
        # Метка
        label_surface = self.font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.rect.left, self.rect.top - 25))
        
        # Квадрат цвета
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Текст с цветом
        color_text = f"({self.color[0]}, {self.color[1]}, {self.color[2]})"
        text_surface = self.font.render(color_text, True, WHITE)
        screen.blit(text_surface, (self.rect.right + 10, self.rect.top))
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class Game:
    """Основной класс игры"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра с Настройками")
        self.clock = pygame.time.Clock()
        
        self.settings = SettingsManager()
        self.sound_manager = SoundManager(self.settings)
        
        self.state = "menu"  # menu, settings, game, game_over
        self.player = {"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT - 50, "width": 40, "height": 40}
        self.enemies = []
        self.score = 0
        self.spawn_timer = 0
        
        # Элементы интерфейса настроек
        self.setup_settings_ui()
        
        # Кнопки меню
        self.play_button = Button(SCREEN_WIDTH//2 - 100, 200, 200, 50, "ИГРАТЬ")
        self.settings_button = Button(SCREEN_WIDTH//2 - 100, 280, 200, 50, "НАСТРОЙКИ")
        self.quit_button = Button(SCREEN_WIDTH//2 - 100, 360, 200, 50, "ВЫХОД")
        
        # Кнопки в игре
        self.back_to_menu_button = Button(10, 10, 150, 40, "МЕНЮ")
        
        # Кнопка возврата из настроек
        self.back_from_settings_button = Button(SCREEN_WIDTH//2 - 100, 520, 200, 50, "НАЗАД")
        
        # Кнопка рестарта
        self.restart_button = Button(SCREEN_WIDTH//2 - 100, 350, 200, 50, "ЗАНОВО")
        
        self.running = True
    
    def setup_settings_ui(self):
        """Настраивает интерфейс настроек"""
        y_start = 80
        y_step = 60
        
        self.sliders = {
            "volume": Slider(200, y_start, 400, 0, 100, self.settings.get("volume"), "Громкость"),
            "music_volume": Slider(200, y_start + y_step, 400, 0, 100, self.settings.get("music_volume"), "Музыка"),
            "difficulty": Slider(200, y_start + 2*y_step, 400, 1, 5, self.settings.get("difficulty"), "Сложность"),
            "player_speed": Slider(200, y_start + 3*y_step, 400, 1, 10, self.settings.get("player_speed"), "Скорость игрока"),
            "enemy_speed": Slider(200, y_start + 4*y_step, 400, 1, 10, self.settings.get("enemy_speed"), "Скорость врагов"),
            "max_enemies": Slider(200, y_start + 5*y_step, 400, 1, 20, self.settings.get("max_enemies"), "Макс. врагов"),
        }
        
        self.color_pickers = {
            "player_color": ColorPicker(200, y_start + 6*y_step, self.settings.get("player_color"), "Цвет игрока"),
            "background_color": ColorPicker(450, y_start + 6*y_step, self.settings.get("background_color"), "Цвет фона"),
        }
        
        self.show_fps_checkbox = pygame.Rect(200, y_start + 7*y_step, 30, 30)
        self.fullscreen_checkbox = pygame.Rect(450, y_start + 7*y_step, 30, 30)
    
    def handle_events(self):
        """Обрабатывает события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == "menu":
                    if self.play_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.state = "game"
                        self.reset_game()
                    elif self.settings_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.state = "settings"
                    elif self.quit_button.is_clicked(mouse_pos, True):
                        self.running = False
                
                elif self.state == "settings":
                    if self.back_from_settings_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.save_settings_from_ui()
                        self.state = "menu"
                    
                    # Проверка чекбоксов
                    if self.show_fps_checkbox.collidepoint(mouse_pos):
                        self.settings.set("show_fps", not self.settings.get("show_fps"))
                        self.sound_manager.play_click()
                    if self.fullscreen_checkbox.collidepoint(mouse_pos):
                        self.settings.set("fullscreen", not self.settings.get("fullscreen"))
                        self.toggle_fullscreen()
                        self.sound_manager.play_click()
                    
                    # Проверка цветовых пикеров
                    for key, picker in self.color_pickers.items():
                        if picker.is_clicked(mouse_pos, True):
                            # Циклическая смена цветов
                            colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [0, 255, 255]]
                            current_idx = colors.index(picker.color) if picker.color in colors else 0
                            new_color = colors[(current_idx + 1) % len(colors)]
                            picker.color = new_color
                            self.settings.set(key, new_color)
                            self.sound_manager.play_click()
                
                elif self.state == "game":
                    if self.back_to_menu_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.state = "menu"
                
                elif self.state == "game_over":
                    if self.restart_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.state = "game"
                        self.reset_game()
                    elif self.back_to_menu_button.is_clicked(mouse_pos, True):
                        self.sound_manager.play_click()
                        self.state = "menu"
    
    def save_settings_from_ui(self):
        """Сохраняет настройки из UI"""
        for key, slider in self.sliders.items():
            self.settings.set(key, slider.value)
        
        for key, picker in self.color_pickers.items():
            self.settings.set(key, picker.color)
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        if self.settings.get("fullscreen"):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def reset_game(self):
        """Сбрасывает игру (НО НЕ РЕКОРД!)"""
        self.player = {"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT - 50, "width": 40, "height": 40}
        self.enemies = []
        self.score = 0
        self.spawn_timer = 0
    
    def update(self):
        """Обновляет логику игры"""
        if self.state == "game":
            # Движение игрока
            keys = pygame.key.get_pressed()
            speed = self.settings.get("player_speed", 5)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player["x"] -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player["x"] += speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player["y"] -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player["y"] += speed
            
            # Ограничение границ
            self.player["x"] = max(0, min(SCREEN_WIDTH - self.player["width"], self.player["x"]))
            self.player["y"] = max(0, min(SCREEN_HEIGHT - self.player["height"], self.player["y"]))
            
            # Спавн врагов
            self.spawn_timer += 1
            difficulty = self.settings.get("difficulty", 2)
            spawn_rate = max(20, 60 - difficulty * 10)
            max_enemies = self.settings.get("max_enemies", 5)
            
            if self.spawn_timer >= spawn_rate and len(self.enemies) < max_enemies:
                enemy_size = random.randint(20, 50)
                enemy = {
                    "x": random.randint(0, SCREEN_WIDTH - enemy_size),
                    "y": -enemy_size,
                    "width": enemy_size,
                    "height": enemy_size,
                    "speed": self.settings.get("enemy_speed", 3)
                }
                self.enemies.append(enemy)
                self.spawn_timer = 0
            
            # Движение врагов
            enemy_speed = self.settings.get("enemy_speed", 3)
            for enemy in self.enemies[:]:
                enemy["y"] += enemy_speed
                
                # Проверка столкновения
                if self.check_collision(self.player, enemy):
                    self.sound_manager.play_game_over()
                    self.settings.update_high_score(self.score)
                    self.state = "game_over"
                
                # Удаление врагов за экраном
                if enemy["y"] > SCREEN_HEIGHT:
                    self.enemies.remove(enemy)
                    self.score += 1
                    self.sound_manager.play_score()
    
    def check_collision(self, rect1, rect2):
        """Проверяет столкновение двух прямоугольников"""
        return (rect1["x"] < rect2["x"] + rect2["width"] and
                rect1["x"] + rect1["width"] > rect2["x"] and
                rect1["y"] < rect2["y"] + rect2["height"] and
                rect1["y"] + rect1["height"] > rect2["y"])
    
    def draw(self):
        """Рисует всё на экране"""
        bg_color = tuple(self.settings.get("background_color", [0, 0, 0]))
        self.screen.fill(bg_color)
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "game":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Рисует меню"""
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("СУПЕР ИГРА", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Показываем рекорд
        high_score = self.settings.get("high_score", 0)
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"РЕКОРД: {high_score}", True, GREEN)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(score_text, score_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.check_hover(mouse_pos)
        self.play_button.draw(self.screen)
        
        self.settings_button.check_hover(mouse_pos)
        self.settings_button.draw(self.screen)
        
        self.quit_button.check_hover(mouse_pos)
        self.quit_button.draw(self.screen)
    
    def draw_settings(self):
        """Рисует настройки"""
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("НАСТРОЙКИ", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 40))
        self.screen.blit(title, title_rect)
        
        # Рисуем ползунки
        for slider in self.sliders.values():
            slider.draw(self.screen)
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            slider.check_drag(mouse_pos, mouse_pressed)
        
        # Рисуем выбор цвета
        for picker in self.color_pickers.values():
            picker.draw(self.screen)
        
        # Чекбокс Show FPS
        checkbox_font = pygame.font.Font(None, 28)
        fps_text = checkbox_font.render("Показывать FPS", True, WHITE)
        self.screen.blit(fps_text, (self.show_fps_checkbox.right + 10, self.show_fps_checkbox.top + 5))
        pygame.draw.rect(self.screen, DARK_GRAY, self.show_fps_checkbox)
        if self.settings.get("show_fps", True):
            pygame.draw.line(self.screen, GREEN, 
                           (self.show_fps_checkbox.left + 5, self.show_fps_checkbox.top + 5),
                           (self.show_fps_checkbox.right - 5, self.show_fps_checkbox.bottom - 5), 3)
            pygame.draw.line(self.screen, GREEN,
                           (self.show_fps_checkbox.left + 5, self.show_fps_checkbox.bottom - 5),
                           (self.show_fps_checkbox.right - 5, self.show_fps_checkbox.top + 5), 3)
        pygame.draw.rect(self.screen, WHITE, self.show_fps_checkbox, 2)
        
        # Чекбокс Fullscreen
        fs_text = checkbox_font.render("Полный экран", True, WHITE)
        self.screen.blit(fs_text, (self.fullscreen_checkbox.right + 10, self.fullscreen_checkbox.top + 5))
        pygame.draw.rect(self.screen, DARK_GRAY, self.fullscreen_checkbox)
        if self.settings.get("fullscreen", False):
            pygame.draw.line(self.screen, GREEN,
                           (self.fullscreen_checkbox.left + 5, self.fullscreen_checkbox.top + 5),
                           (self.fullscreen_checkbox.right - 5, self.fullscreen_checkbox.bottom - 5), 3)
            pygame.draw.line(self.screen, GREEN,
                           (self.fullscreen_checkbox.left + 5, self.fullscreen_checkbox.bottom - 5),
                           (self.fullscreen_checkbox.right - 5, self.fullscreen_checkbox.top + 5), 3)
        pygame.draw.rect(self.screen, WHITE, self.fullscreen_checkbox, 2)
        
        # Информация о том, что рекорд нельзя менять
        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render("* Рекорд сохраняется автоматически и не может быть изменён вручную", True, GRAY)
        self.screen.blit(info_text, (50, 490))
        
        mouse_pos = pygame.mouse.get_pos()
        self.back_from_settings_button.check_hover(mouse_pos)
        self.back_from_settings_button.draw(self.screen)
    
    def draw_game(self):
        """Рисует игру"""
        player_color = tuple(self.settings.get("player_color", [0, 0, 255]))
        pygame.draw.rect(self.screen, player_color, 
                        (self.player["x"], self.player["y"], self.player["width"], self.player["height"]))
        
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, RED, 
                           (enemy["x"], enemy["y"], enemy["width"], enemy["height"]))
        
        # Счёт
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Счёт: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 60))
        
        # Рекорд
        high_score = self.settings.get("high_score", 0)
        hs_text = score_font.render(f"Рекорд: {high_score}", True, GREEN)
        self.screen.blit(hs_text, (10, 110))
        
        # Кнопка меню
        mouse_pos = pygame.mouse.get_pos()
        self.back_to_menu_button.check_hover(mouse_pos)
        self.back_to_menu_button.draw(self.screen)
        
        # FPS
        if self.settings.get("show_fps", True):
            fps = int(self.clock.get_fps())
            fps_font = pygame.font.Font(None, 28)
            fps_text = fps_font.render(f"FPS: {fps}", True, WHITE)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
    
    def draw_game_over(self):
        """Рисует экран конца игры"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("ИГРА ОКОНЧЕНА", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(game_over_text, text_rect)
        
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Ваш счёт: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(score_text, score_rect)
        
        high_score = self.settings.get("high_score", 0)
        hs_text = score_font.render(f"Рекорд: {high_score}", True, GREEN)
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH//2, 340))
        self.screen.blit(hs_text, hs_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        self.restart_button.draw(self.screen)
        
        self.back_to_menu_button.check_hover(mouse_pos)
        self.back_to_menu_button.draw(self.screen)
    
    def run(self):
        """Запускает игровой цикл"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
