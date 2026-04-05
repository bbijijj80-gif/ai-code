import pygame
import random
import math
import os
import json

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
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
ORANGE = (255, 165, 0)

# Настройка экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Космический Шутер - Галактическая Битва")
clock = pygame.time.Clock()

# Классы
class Star:
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
    
    def draw(self):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.draw_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 7
        self.health = 100
        self.shoot_delay = 150
        self.last_shot = pygame.time.get_ticks()
    
    def draw_ship(self):
        # Основной корпус
        points = [(30, 0), (0, 80), (30, 65), (60, 80)]
        pygame.draw.polygon(self.image, CYAN, points)
        # Кабина
        pygame.draw.circle(self.image, BLUE, (30, 35), 12)
        # Двигатель
        pygame.draw.ellipse(self.image, ORANGE, (20, 70, 20, 15))
        # Крылья
        pygame.draw.polygon(self.image, PURPLE, [(0, 50), (15, 60), (0, 80)])
        pygame.draw.polygon(self.image, PURPLE, [(60, 50), (45, 60), (60, 80)])
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx, self.rect.top, -12, BLUE)
        return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.enemy_type = random.choice(['fighter', 'bomber', 'scout'])
        self.draw_enemy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.uniform(2, 5)
        self.speed_x = random.uniform(-1, 1)
        self.health = {'fighter': 30, 'bomber': 60, 'scout': 15}[self.enemy_type]
        self.score_value = {'fighter': 100, 'bomber': 200, 'scout': 50}[self.enemy_type]
    
    def draw_enemy(self):
        if self.enemy_type == 'fighter':
            pygame.draw.polygon(self.image, RED, [(25, 0), (0, 50), (50, 50)])
            pygame.draw.circle(self.image, YELLOW, (25, 30), 8)
        elif self.enemy_type == 'bomber':
            pygame.draw.ellipse(self.image, PURPLE, (5, 10, 40, 35))
            pygame.draw.rect(self.image, RED, (15, 0, 20, 20))
        else:  # scout
            pygame.draw.polygon(self.image, ORANGE, [(25, 0), (10, 25), (40, 25)])
            pygame.draw.circle(self.image, CYAN, (25, 20), 6)
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        super().__init__()
        self.image = pygame.Surface((6, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, color, (0, 0, 6, 20))
        pygame.draw.ellipse(self.image, WHITE, (2, 0, 2, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frame = 0
        self.max_frames = 15
        self.images = []
        for i in range(self.max_frames):
            img = pygame.Surface((60 + i*4, 60 + i*4), pygame.SRCALPHA)
            alpha = 255 - i * 17
            radius = 30 + i * 2
            pygame.draw.circle(img, (*RED[:3], alpha), (img.get_width()//2, img.get_height()//2), radius)
            pygame.draw.circle(img, (*YELLOW[:3], alpha), (img.get_width()//2, img.get_height()//2), radius//2)
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

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['health', 'speed', 'multishot'])
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        colors = {'health': GREEN, 'speed': CYAN, 'multishot': PURPLE}
        pygame.draw.circle(self.image, colors[self.type], (15, 15), 15)
        font = pygame.font.Font(None, 24)
        text = font.render({'health': '+', 'speed': 'S', 'multishot': 'M'}[self.type], True, WHITE)
        self.image.blit(text, (10, 8))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 3
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.reset_game()
        self.create_sounds()
        self.stars = [Star() for _ in range(150)]
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
    
    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1500
    
    def create_sounds(self):
        self.shoot_sound = self.generate_sound(440, 0.1, 'square')
        self.explosion_sound = self.generate_sound(100, 0.3, 'noise')
        self.powerup_sound = self.generate_sound(880, 0.2, 'sine')
    
    def generate_sound(self, freq, duration, wave_type):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytes()
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'square':
                value = 127 if math.sin(2 * math.pi * freq * t) > 0 else -127
            elif wave_type == 'sine':
                value = int(127 * math.sin(2 * math.pi * freq * t))
            else:  # noise
                value = random.randint(-127, 127)
            buf += bytes([value + 128])
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(0.3)
        return sound
    
    def spawn_enemy(self):
        enemy = Enemy()
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
    
    def spawn_powerup(self, center):
        if random.random() < 0.15:
            powerup = PowerUp(center)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)
    
    def draw_background(self):
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(10 + 20 * ratio)
            g = int(5 + 15 * ratio)
            b = int(30 + 40 * ratio)
            pygame.draw.line(gradient, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        screen.blit(gradient, (0, 0))
        
        for star in self.stars:
            star.update()
            star.draw()
    
    def draw_ui(self):
        score_text = self.font_small.render(f"Счёт: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        level_text = self.font_small.render(f"Уровень: {self.level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 200, 20))
        
        health_width = 200
        health_height = 20
        health_ratio = max(0, self.player.health / 100)
        pygame.draw.rect(screen, RED, (20, 60, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (20, 60, int(health_width * health_ratio), health_height))
        pygame.draw.rect(screen, WHITE, (20, 60, health_width, health_height), 2)
        health_text = self.font_small.render("Здоровье", True, WHITE)
        screen.blit(health_text, (20, 85))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("ИГРА ОКОНЧЕНА", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
        
        final_score = self.font_medium.render(f"Финальный счёт: {self.score}", True, WHITE)
        screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2))
        
        restart_text = self.font_small.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("ПАУЗА", True, CYAN)
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        
        resume_text = self.font_small.render("Нажмите P для продолжения", True, WHITE)
        screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_over:
                            running = False
                        else:
                            self.paused = not self.paused
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
            
            if self.paused:
                self.draw_background()
                self.draw_ui()
                self.draw_pause()
                pygame.display.flip()
                continue
            
            if not self.game_over:
                self.enemy_spawn_timer += clock.get_time()
                if self.enemy_spawn_timer > self.enemy_spawn_delay:
                    self.spawn_enemy()
                    self.enemy_spawn_timer = 0
                
                if self.score >= self.level * 1000:
                    self.level += 1
                    self.enemy_spawn_delay = max(500, 1500 - self.level * 100)
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    bullet = self.player.shoot()
                    if bullet:
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)
                        self.shoot_sound.play()
                
                self.all_sprites.update()
                
                hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
                for enemy in hits:
                    enemy.health -= 10
                    if enemy.health <= 0:
                        self.score += enemy.score_value
                        explosion = Explosion(enemy.rect.center)
                        self.all_sprites.add(explosion)
                        self.explosions.add(explosion)
                        self.spawn_powerup(enemy.rect.center)
                        self.explosion_sound.play()
                        enemy.kill()
                
                hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
                for enemy in hits:
                    self.player.health -= 20
                    explosion = Explosion(enemy.rect.center)
                    self.all_sprites.add(explosion)
                    self.explosions.add(explosion)
                    self.explosion_sound.play()
                
                hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
                for powerup in hits:
                    if powerup.type == 'health':
                        self.player.health = min(100, self.player.health + 25)
                    elif powerup.type == 'speed':
                        self.player.speed = min(12, self.player.speed + 1)
                    elif powerup.type == 'multishot':
                        self.player.shoot_delay = max(80, self.player.shoot_delay - 20)
                    self.powerup_sound.play()
                
                if self.player.health <= 0:
                    self.game_over = True
            
            self.draw_background()
            self.all_sprites.draw(screen)
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
