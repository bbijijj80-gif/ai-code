"""
Космический шутер - Версия для Windows
С интеграцией реестра Windows (HKCU\Software)
"""

import pygame
import random
import math
import os
import json
import sys
import ctypes
from datetime import datetime
from ctypes import wintypes

# Импортируем основной код игры
exec(open('game_core.py').read().replace('if __name__ == "__main__":', 'if False:'))

# Константы Windows для реестра
HKEY_CURRENT_USER = 0x80000001
KEY_SET_VALUE = 0x0002
KEY_QUERY_VALUE = 0x0001
REG_SZ = 1
REG_DWORD = 4

class WindowsRegistryManager:
    """Менеджер реестра Windows для хранения 20 значений игры"""
    
    def __init__(self):
        self.registry_path = r"Software\SpaceShooterGame"
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
        self.load_from_registry()
        
    def _open_registry_key(self, create=False):
        """Открытие ключа реестра"""
        try:
            advapi32 = ctypes.windll.advapi32
            
            if create:
                result = advapi32.RegCreateKeyW(
                    HKEY_CURRENT_USER,
                    self.registry_path,
                    ctypes.byref(ctypes.c_void_p())
                )
            else:
                result = advapi32.RegOpenKeyExW(
                    HKEY_CURRENT_USER,
                    self.registry_path,
                    0,
                    KEY_SET_VALUE | KEY_QUERY_VALUE,
                    ctypes.byref(ctypes.c_void_p())
                )
            
            if result == 0:
                return True
            return False
        except:
            return False
    
    def _set_value(self, name, value, value_type=REG_DWORD):
        """Установка значения в реестр"""
        try:
            advapi32 = ctypes.windll.advapi32
            
            hkey = ctypes.c_void_p()
            if advapi32.RegCreateKeyW(HKEY_CURRENT_USER, self.registry_path, ctypes.byref(hkey)) != 0:
                return False
            
            if value_type == REG_DWORD:
                data = ctypes.c_ulong(int(value))
                data_size = ctypes.sizeof(ctypes.c_ulong)
            else:  # REG_SZ
                data = ctypes.create_unicode_buffer(str(value))
                data_size = (len(str(value)) + 1) * 2
            
            result = advapi32.RegSetValueExW(
                hkey,
                name,
                0,
                value_type,
                ctypes.byref(data),
                data_size
            )
            
            advapi32.RegCloseKey(hkey)
            return result == 0
        except Exception as e:
            print(f"Registry set error: {e}")
            return False
    
    def _get_value(self, name, default=0, value_type=REG_DWORD):
        """Получение значения из реестра"""
        try:
            advapi32 = ctypes.windll.advapi32
            
            hkey = ctypes.c_void_p()
            if advapi32.RegOpenKeyExW(
                HKEY_CURRENT_USER,
                self.registry_path,
                0,
                KEY_QUERY_VALUE,
                ctypes.byref(hkey)
            ) != 0:
                return default
            
            if value_type == REG_DWORD:
                data = ctypes.c_ulong()
                data_size = ctypes.c_ulong(ctypes.sizeof(ctypes.c_ulong))
            else:
                data = ctypes.create_unicode_buffer(256)
                data_size = ctypes.c_ulong(512)
            
            type_buffer = ctypes.c_ulong()
            if advapi32.RegQueryValueExW(
                hkey,
                name,
                None,
                ctypes.byref(type_buffer),
                ctypes.byref(data),
                ctypes.byref(data_size)
            ) == 0:
                advapi32.RegCloseKey(hkey)
                if value_type == REG_DWORD:
                    return data.value
                else:
                    return data.value
            else:
                advapi32.RegCloseKey(hkey)
                return default
        except Exception as e:
            print(f"Registry get error: {e}")
            return default
    
    def load_from_registry(self):
        """Загрузка всех 20 значений из реестра Windows"""
        for key in self.registry_data:
            if key in ['last_played', 'player_name', 'language']:
                value = self._get_value(key, self.registry_data[key], REG_SZ)
            else:
                value = self._get_value(key, self.registry_data[key], REG_DWORD)
            self.registry_data[key] = value
    
    def save_to_registry(self):
        """Сохранение всех 20 значений в реестр Windows"""
        for key, value in self.registry_data.items():
            if key in ['last_played', 'player_name', 'language']:
                self._set_value(key, value, REG_SZ)
            else:
                self._set_value(key, value, REG_DWORD)
    
    def get_value(self, key):
        return self.registry_data.get(key, 0)
    
    def set_value(self, key, value):
        if key in self.registry_data:
            self.registry_data[key] = value
            self.save_to_registry()
    
    def increment(self, key, amount=1):
        if key in self.registry_data:
            self.registry_data[key] += amount
            self.save_to_registry()
    
    def update_best_score(self, score):
        if score > self.registry_data['best_score']:
            self.registry_data['best_score'] = score
            self.save_to_registry()
            return True
        return False

class WindowsGame(Game):
    """Версия игры для Windows с реестром"""
    
    def __init__(self):
        self.registry = WindowsRegistryManager()
        
        # Инициализация остальной части игры
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Космический Шутер - Windows Version")
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
            
        self.registry.save_to_registry()
        pygame.quit()

if __name__ == "__main__":
    game = WindowsGame()
    game.run()
