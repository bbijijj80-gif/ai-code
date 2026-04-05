"""
Космический шутер - Версия для Linux
С хранением настроек в файле конфигурации
"""

import pygame
import random
import math
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Импортируем основной код игры
exec(open('../game_core.py').read().replace('if __name__ == "__main__":', 'if False:'))

class LinuxConfigManager:
    """Менеджер конфигурации для Linux (аналог реестра)"""
    
    def __init__(self):
        # Путь к конфигу в домашней директории пользователя
        self.config_dir = Path.home() / '.config' / 'space_shooter'
        self.config_file = self.config_dir / 'settings.json'
        
        self.registry_data = {
            'best_score': 0,
            'total_games': 0,
            'total_enemies_destroyed': 0,
            'total_shots_fired': 0,
            'total_powerups_collected': 0,
            'play_time_seconds': 0,
            'last_played': '',
            'player_name': 'Pilot',
            'difficulty': 1,
            'sound_enabled': 1,
            'music_enabled': 1,
            'screen_width': SCREEN_WIDTH,
            'screen_height': SCREEN_HEIGHT,
            'fullscreen': 0,
            'ship_color_r': 0,
            'ship_color_g': 100,
            'ship_color_b': 255,
            'particles_enabled': 1,
            'show_fps': 0,
            'language': 'ru'
        }
        
        # Создаем директорию если не существует
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_from_file()
    
    def load_from_file(self):
        """Загрузка всех 20 значений из файла конфигурации"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)
                    for key in saved_data:
                        if key in self.registry_data:
                            self.registry_data[key] = saved_data[key]
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_to_file(self):
        """Сохранение всех 20 значений в файл конфигурации"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.registry_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_value(self, key):
        return self.registry_data.get(key, 0)
    
    def set_value(self, key, value):
        if key in self.registry_data:
            self.registry_data[key] = value
            self.save_to_file()
    
    def increment(self, key, amount=1):
        if key in self.registry_data:
            self.registry_data[key] += amount
            self.save_to_file()
    
    def update_best_score(self, score):
        if score > self.registry_data['best_score']:
            self.registry_data['best_score'] = score
            self.save_to_file()
            return True
        return False
    
    def export_to_registry_format(self):
        """Экспорт в формат похожий на реестр (для совместимости)"""
        reg_file = self.config_dir / 'registry_export.reg'
        with open(reg_file, 'w') as f:
            f.write("Windows Registry Editor Version 5.00\n\n")
            f.write("[HKEY_CURRENT_USER\\Software\\SpaceShooterGame]\n")
            for key, value in self.registry_data.items():
                if isinstance(value, str):
                    f.write(f'"{key}"="{value}"\n')
                else:
                    f.write(f'"{key}"=dword:{value:08x}\n')

class LinuxGame(Game):
    """Версия игры для Linux с файловым хранилищем"""
    
    def __init__(self):
        self.registry = LinuxConfigManager()
        
        # Инициализация остальной части игры
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Космический Шутер - Linux Version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.sound_manager = SoundManager()
        self.stars = [Star() for _ in range(100)]
        self.reset_game()
    
    def run(self):
        running = True
        self.sound_manager.start_music()
        
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.update()
            self.draw()
            
        self.registry.save_to_file()
        pygame.quit()

if __name__ == "__main__":
    game = LinuxGame()
    game.run()
