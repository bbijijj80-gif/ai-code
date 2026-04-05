"""
Космический шутер - Основная логика игры
Общая версия для Windows и Linux
"""

import pygame
import random
import math
import os
import json
import sys
from datetime import datetime

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 150, 0)

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
    """Игрок"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.draw_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 8
        self.health = 100
        self.score = 0
        self.shoot_timer = 0
        self.shoot_delay = 150
        
    def draw_ship(self):
        # Рисуем космический корабль
        points = [(30, 0), (0, 80), (30, 65), (60, 80)]
        pygame.draw.polygon(self.image, BLUE, points)
        pygame.draw.polygon(self.image, CYAN, [(30, 10), (15, 70), (30, 60), (45, 70)])
        # Огонь из двигателя
        flame_points = [(25, 80), (30, 95 + random.randint(0, 10)), (35, 80)]
        pygame.draw.polygon(self.image, ORANGE, flame_points)
        
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
        
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > self.shoot_delay:
            self.shoot_timer = now
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Bullet(pygame.sprite.Sprite):
    """Пуля игрока"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 20))
        pygame.draw.rect(self.image, WHITE, (2, 0, 2, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -12
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """Враг"""
    def __init__(self, difficulty=1):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.enemy_type = random.choice(['fighter', 'bomber', 'scout'])
        self.draw_enemy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -50)
        self.speed_y = random.uniform(2, 5) * difficulty
        self.speed_x = random.uniform(-1, 1)
        self.health = {'fighter': 3, 'bomber': 5, 'scout': 1}[self.enemy_type] * difficulty
        self.score_value = {'fighter': 100, 'bomber': 200, 'scout': 50}[self.enemy_type]
        
    def draw_enemy(self):
        if self.enemy_type == 'fighter':
            color = RED
            points = [(25, 50), (0, 0), (25, 20), (50, 0)]
        elif self.enemy_type == 'bomber':
            color = PURPLE
            points = [(0, 0), (50, 0), (40, 50), (10, 50)]
        else:  # scout
            color = GREEN
            points = [(25, 0), (50, 25), (25, 50), (0, 25)]
        
        pygame.draw.polygon(self.image, color, points)
        pygame.draw.polygon(self.image, WHITE, [(p[0]+5, p[1]+5) for p in points], 2)
        
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
            
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    """Бонусы"""
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['health', 'speed', 'multishot'])
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        colors = {'health': GREEN, 'speed': CYAN, 'multishot': ORANGE}
        pygame.draw.circle(self.image, colors[self.type], (15, 15), 15)
        font = pygame.font.Font(None, 24)
        text = font.render({'health': '+', 'speed': 'S', 'multishot': 'M'}[self.type], True, BLACK)
        self.image.blit(text, (10, 8))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 3
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Взрыв"""
    def __init__(self, center):
        super().__init__()
        self.frame = 0
        self.max_frames = 10
        self.images = []
        for i in range(self.max_frames):
            img = pygame.Surface((60, 60), pygame.SRCALPHA)
            radius = 5 + i * 5
            alpha = 255 - i * 25
            pygame.draw.circle(img, (*YELLOW[:3], alpha), (30, 30), radius)
            pygame.draw.circle(img, (*RED[:3], alpha), (30, 30), radius - 5)
            self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
        else:
            self.image = self.images[self.frame]

class SoundManager:
    """Менеджер звуков"""
    def __init__(self):
        self.sounds = {}
        self.music_loaded = False
        
    def generate_sound(self, sound_type):
        """Генерация простых звуков программно"""
        sample_rate = 44100
        duration = 0.3
        
        if sound_type == 'shoot':
            # Звук выстрела
            samples = int(sample_rate * duration)
            buf = bytearray(samples * 2)
            for i in range(samples):
                t = i / sample_rate
                value = int(10000 * math.sin(2 * math.pi * 800 * t) * (1 - t/duration))
                buf[i*2:i*2+2] = value.to_bytes(2, 'little', signed=True)
            sound = pygame.mixer.Sound(buffer=buf)
            
        elif sound_type == 'explosion':
            # Звук взрыва (шум)
            samples = int(sample_rate * 0.5)
            buf = bytearray(samples * 2)
            for i in range(samples):
                value = random.randint(-8000, 8000) * (1 - i/samples)
                buf[i*2:i*2+2] = value.to_bytes(2, 'little', signed=True)
            sound = pygame.mixer.Sound(buffer=buf)
            
        elif sound_type == 'powerup':
            # Звук бонуса
            samples = int(sample_rate * 0.2)
            buf = bytearray(samples * 2)
            for i in range(samples):
                t = i / sample_rate
                value = int(8000 * math.sin(2 * math.pi * 1200 * t + i/50))
                buf[i*2:i*2+2] = value.to_bytes(2, 'little', signed=True)
            sound = pygame.mixer.Sound(buffer=buf)
            
        elif sound_type == 'hit':
            # Звук попадания
            samples = int(sample_rate * 0.2)
            buf = bytearray(samples * 2)
            for i in range(samples):
                t = i / sample_rate
                value = int(5000 * math.sin(2 * math.pi * 400 * t) * (1 - t/duration))
                buf[i*2:i*2+2] = value.to_bytes(2, 'little', signed=True)
            sound = pygame.mixer.Sound(buffer=buf)
            
        else:
            return None
            
        self.sounds[sound_type] = sound
        return sound
    
    def play(self, sound_type):
        if sound_type in self.sounds:
            self.sounds[sound_type].play()
        else:
            sound = self.generate_sound(sound_type)
            if sound:
                sound.play()
    
    def start_music(self):
        """Фоновая музыка"""
        try:
            sample_rate = 44100
            duration = 30
            samples = int(sample_rate * duration)
            buf = bytearray(samples * 2)
            
            for i in range(samples):
                t = i / sample_rate
                value = 0
                value += int(3000 * math.sin(2 * math.pi * 200 * t))
                value += int(2000 * math.sin(2 * math.pi * 300 * t))
                value += int(1500 * math.sin(2 * math.pi * 400 * t))
                value = max(-32767, min(32767, value))
                buf[i*2:i*2+2] = value.to_bytes(2, 'little', signed=True)
            
            pygame.mixer.music.load(buffer=buf)
            pygame.mixer.music.play(-1)
            self.music_loaded = True
        except:
            pass

class RegistryManager:
    """Менеджер реестра/конфигурации"""
    def __init__(self):
        self.platform = sys.platform
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
        self.config_file = 'space_shooter_config.json'
        self.load_data()
        
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)
                    for key in saved_data:
                        if key in self.registry_data:
                            self.registry_data[key] = saved_data[key]
            except:
                pass
                
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.registry_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
            
    def get_value(self, key):
        return self.registry_data.get(key, 0)
        
    def set_value(self, key, value):
        if key in self.registry_data:
            self.registry_data[key] = value
            self.save_data()
            
    def increment(self, key, amount=1):
        if key in self.registry_data:
            self.registry_data[key] += amount
            self.save_data()
            
    def update_best_score(self, score):
        if score > self.registry_data['best_score']:
            self.registry_data['best_score'] = score
            self.save_data()
            return True
        return False

class Game:
    """Основной класс игры"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Космический Шутер")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.registry = RegistryManager()
        self.sound_manager = SoundManager()
        
        self.stars = [Star() for _ in range(100)]
        
        self.reset_game()
        
    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1500
        self.game_over = False
        self.paused = False
        self.start_time = pygame.time.get_ticks()
        
    def spawn_enemy(self):
        enemy = Enemy(self.registry.get_value('difficulty'))
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        
    def handle_events(self):
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
                        self.registry.increment('total_shots_fired')
                        if self.registry.get_value('sound_enabled'):
                            self.sound_manager.play('shoot')
                            
        return True
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        self.all_sprites.update()
        
        # Спавн врагов
        now = pygame.time.get_ticks()
        if now - self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.enemy_spawn_timer = now
            self.spawn_enemy()
            self.enemy_spawn_delay = max(500, 1500 - self.player.score // 10)
            
        # Попадания пуль во врагов
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= len(bullets)
            if enemy.health <= 0:
                self.player.score += enemy.score_value
                self.registry.increment('total_enemies_destroyed')
                
                # Шанс выпадения бонуса
                if random.random() < 0.15:
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery)
                    self.all_sprites.add(powerup)
                    self.powerups.add(powerup)
                    
                explosion = Explosion(enemy.rect.center)
                self.all_sprites.add(explosion)
                self.explosions.add(explosion)
                
                if self.registry.get_value('sound_enabled'):
                    self.sound_manager.play('explosion')
                    
                enemy.kill()
                
        # Столкновения с игроком
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for enemy in hits:
            self.player.health -= 20
            explosion = Explosion(enemy.rect.center)
            self.all_sprites.add(explosion)
            self.explosions.add(explosion)
            if self.registry.get_value('sound_enabled'):
                self.sound_manager.play('hit')
                
        # Сбор бонусов
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            if powerup.type == 'health':
                self.player.health = min(100, self.player.health + 25)
            elif powerup.type == 'speed':
                self.player.speed = min(15, self.player.speed + 2)
            elif powerup.type == 'multishot':
                self.player.shoot_delay = max(50, self.player.shoot_delay - 30)
            self.registry.increment('total_powerups_collected')
            if self.registry.get_value('sound_enabled'):
                self.sound_manager.play('powerup')
                
        # Проверка game over
        if self.player.health <= 0:
            self.game_over = True
            end_time = pygame.time.get_ticks()
            play_time = (end_time - self.start_time) // 1000
            self.registry.increment('total_games')
            self.registry.increment('play_time_seconds', play_time)
            self.registry.update_best_score(self.player.score)
            self.registry.set_value('last_played', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
    def draw(self):
        # Фон
        self.screen.fill(BLACK)
        for star in self.stars:
            star.update()
            star.draw(self.screen)
            
        # Игровые объекты
        self.all_sprites.draw(self.screen)
        
        # Интерфейс
        health_text = self.font.render(f"Здоровье: {self.player.health}", True, GREEN)
        score_text = self.font.render(f"Счёт: {self.player.score}", True, WHITE)
        best_text = self.font.render(f"Рекорд: {self.registry.get_value('best_score')}", True, YELLOW)
        
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(score_text, (10, 50))
        self.screen.blit(best_text, (10, 90))
        
        # Пауза
        if self.paused:
            pause_text = self.big_font.render("ПАУЗА", True, WHITE)
            self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2))
            
        # Game Over
        if self.game_over:
            go_text = self.big_font.render("GAME OVER", True, RED)
            final_score = self.font.render(f"Финальный счёт: {self.player.score}", True, WHITE)
            restart_text = self.font.render("Нажмите R для рестарта или ESC для выхода", True, YELLOW)
            
            self.screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
            
        pygame.display.flip()
        
    def run(self):
        running = True
        self.sound_manager.start_music()
        
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            self.update()
            self.draw()
            
        self.registry.save_data()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
