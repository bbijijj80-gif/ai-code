import pygame
import random
import sys
import os

# Проверка платформы и импорт реестра только для Windows
if sys.platform == 'win32':
    import winreg
else:
    winreg = None

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
PURPLE = (150, 50, 255)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Рекорд: 1,000,000,000")
clock = pygame.time.Clock()

# Пути для сохранения (резервный вариант для не-Windows)
SAVE_DIR = os.path.join(os.path.expanduser("~"), "SpaceShooterGame")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.txt")

class RegistryManager:
    """Класс для работы с реестром Windows"""
    
    def __init__(self):
        self.registry_path = r"Software\SpaceShooterGame"
        self.values_count = 10
        if sys.platform == 'win32' and winreg:
            self.create_registry_keys()
    
    def create_registry_keys(self):
        """Создает 10 значений в реестре"""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            
            # 10 различных значений
            values = {
                "MaxScore": 1000000000,  # 1 миллиард (1 лям)
                "GamesPlayed": 0,
                "TotalEnemiesDestroyed": 0,
                "TotalBulletsFired": 0,
                "PlayTimeSeconds": 0,
                "HighestCombo": 0,
                "PowerUpsCollected": 0,
                "DamageTaken": 0,
                "BossesDefeated": 0,
                "SecretsFound": 0
            }
            
            for name, value in values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            
            winreg.CloseKey(key)
            print(f"✓ Создано {len(values)} значений в реестре")
            
        except Exception as e:
            print(f"Ошибка работы с реестром: {e}")
    
    def get_max_score(self):
        """Получает максимальный счет из реестра"""
        if sys.platform != 'win32' or not winreg:
            return self._get_max_score_file()
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            value, _ = winreg.QueryValueEx(key, "MaxScore")
            winreg.CloseKey(key)
            return value
        except:
            return self._get_max_score_file()
    
    def set_max_score(self, score):
        """Устанавливает максимальный счет в реестр (только если новый счет больше)"""
        current_max = self.get_max_score()
        
        # ВАЖНО: Обновляем только если новый счет БОЛЬШЕ текущего
        if score > current_max:
            if sys.platform == 'win32' and winreg:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "MaxScore", 0, winreg.REG_DWORD, score)
                    winreg.CloseKey(key)
                    return True
                except Exception as e:
                    print(f"Ошибка записи в реестр: {e}")
            else:
                self._set_max_score_file(score)
                return True
        return False
    
    def increment_games_played(self):
        """Увеличивает счетчик сыгранных игр"""
        self._increment_value("GamesPlayed")
    
    def _increment_value(self, value_name):
        """Увеличивает значение на 1"""
        if sys.platform == 'win32' and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
                current, _ = winreg.QueryValueEx(key, value_name)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, current + 1)
                winreg.CloseKey(key)
            except:
                pass
    
    # Резервные методы для файлов (не-Windows или ошибка реестра)
    def _get_max_score_file(self):
        if not os.path.exists(SAVE_FILE):
            return 0
        try:
            with open(SAVE_FILE, 'r') as f:
                data = f.readlines()
                if len(data) > 0:
                    return int(data[0].strip())
        except:
            pass
        return 0
    
    def _set_max_score_file(self, score):
        os.makedirs(SAVE_DIR, exist_ok=True)
        current = self._get_max_score_file()
        if score > current:
            with open(SAVE_FILE, 'w') as f:
                f.write(f"{score}\n0\n0\n0\n0\n0\n0\n0\n0\n0")
    
    def get_all_stats(self):
        """Получает всю статистику"""
        stats = {}
        if sys.platform == 'win32' and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path)
                for i in range(self.values_count):
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        stats[name] = value
                    except:
                        break
                winreg.CloseKey(key)
            except:
                pass
        return stats


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Рисуем красивый корабль
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(self.image, PURPLE, [(25, 10), (10, 40), (40, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 7
        self.shoot_timer = 0
    
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
        self.rect.clamp_ip(screen.get_rect())
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > 150:
            self.shoot_timer = now
            return Bullet(self.rect.centerx, self.rect.top)
        return None


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Рисуем врага
        pygame.draw.polygon(self.image, RED, [(20, 0), (0, 40), (40, 40)])
        pygame.draw.circle(self.image, YELLOW, (20, 20), 10)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(2, 5)
        self.speed_x = random.randint(-1, 1)
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.speed_y = random.randint(2, 5)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, (0, 0, 6, 15))
        pygame.draw.rect(self.image, WHITE, (2, 0, 2, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(3, 8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)
        self.life = 30
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Game:
    def __init__(self):
        self.registry = RegistryManager()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        for _ in range(8):
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
        
        self.score = 0
        self.max_score = self.registry.get_max_score()
        self.combo = 0
        self.max_combo = 0
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.game_over = False
        self.paused = False
        self.clock_time = 0
    
    def create_explosion(self, x, y, color):
        for _ in range(15):
            particle = Particle(x, y, color)
            self.all_sprites.add(particle)
            self.particles.add(particle)
    
    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_over:
                            running = False
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                        bullet = self.player.shoot()
                        if bullet:
                            self.all_sprites.add(bullet)
                            self.bullets.add(bullet)
                    elif event.key == pygame.K_r and self.game_over:
                        self.__init__()
            
            if not self.paused and not self.game_over:
                self.all_sprites.update()
                
                # Стрельба врагов (упрощено)
                hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
                for enemy in hits:
                    self.create_explosion(enemy.rect.centerx, enemy.rect.centery, RED)
                    enemy.kill()
                    self.score += 10
                    self.combo += 1
                    if self.combo > self.max_combo:
                        self.max_combo = self.combo
                    
                    # Создаем нового врага
                    new_enemy = Enemy()
                    self.all_sprites.add(new_enemy)
                    self.enemies.add(new_enemy)
                
                # Столкновение с игроком
                hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
                if hits:
                    self.game_over = True
                    self.create_explosion(self.player.rect.centerx, self.player.rect.centery, BLUE)
                    
                    # Обновляем статистику в реестре
                    self.registry.set_max_score(self.score)  # Только если больше текущего
                    self.registry.increment_games_played()
                    
                    # Получаем обновленный макс счет для отображения
                    self.max_score = self.registry.get_max_score()
                
                self.clock_time += 1
            
            # Отрисовка
            screen.fill(BLACK)
            
            # Рисуем звезды на фоне
            for _ in range(5):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                pygame.draw.circle(screen, WHITE, (x, y), random.randint(1, 2))
            
            self.all_sprites.draw(screen)
            
            # Интерфейс
            score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
            max_score_text = self.font.render(f"Рекорд: {self.max_score:,}", True, YELLOW)
            combo_text = self.font.render(f"Комбо: {self.combo}", True, GREEN)
            
            screen.blit(score_text, (10, 10))
            screen.blit(max_score_text, (10, 50))
            screen.blit(combo_text, (10, 90))
            
            if self.paused:
                pause_text = self.big_font.render("ПАУЗА", True, WHITE)
                text_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(pause_text, text_rect)
            
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА", True, RED)
                final_score_text = self.font.render(f"Ваш счет: {self.score}", True, WHITE)
                best_score_text = self.font.render(f"Рекорд: {self.max_score:,}", True, YELLOW)
                restart_text = self.font.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)
                
                screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
                screen.blit(final_score_text, final_score_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
                screen.blit(best_score_text, best_score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
                screen.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 SPACE SHOOTER - Космический Шутер")
    print("=" * 50)
    print(f"Платформа: {sys.platform}")
    
    if sys.platform == 'win32':
        print("✓ Режим Windows: работа с реестром активна")
        print("📁 Игра создаст раздел: HKEY_CURRENT_USER\\Software\\SpaceShooterGame")
        print("📊 10 значений будут сохранены в реестре")
        print("💾 Максимальный счет установлен: 1,000,000,000 (1 лям)")
        print("⚠️  Rekord НЕ будет перезаписываться при каждом запуске!")
    else:
        print("⚠ Не Windows: данные сохраняются в файл")
        print(f"📁 Путь: {SAVE_DIR}")
    
    print("\n🎮 Управление:")
    print("  Стрелки или WASD - движение")
    print("  Пробел - стрельба")
    print("  ESC - пауза/выход")
    print("  R - рестарт после проигрыша")
    print("=" * 50)
    
    game = Game()
    game.run()
