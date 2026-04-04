import pygame
import random
import sys
import os
import math

# Проверка платформы и импорт реестра только для Windows
if sys.platform == 'win32':
    import winreg
else:
    winreg = None

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

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
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
LIGHT_BLUE = (100, 150, 255)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Pro")
clock = pygame.time.Clock()

# Пути для сохранения (резервный вариант для не-Windows)
SAVE_DIR = os.path.join(os.path.expanduser("~"), "SpaceShooterGame")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.txt")

class SoundManager:
    """Класс для управления звуковыми эффектами"""
    
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.music_playing = False
        
        # Генерируем простые звуки программно
        self._create_sounds()
    
    def _create_sounds(self):
        """Создает простые звуковые эффекты"""
        sample_rate = 22050
        
        # Звук выстрела (высокий писк)
        shoot_samples = []
        for i in range(int(sample_rate * 0.1)):
            t = i / sample_rate
            value = int(127 * math.sin(2 * math.pi * 800 * t) * (1 - t * 10))
            shoot_samples.append(max(-128, min(127, value)))
        
        # Звук взрыва (шум)
        explosion_samples = []
        for i in range(int(sample_rate * 0.3)):
            t = i / sample_rate
            value = int(random.uniform(-1, 1) * 127 * (1 - t * 3))
            explosion_samples.append(value)
        
        # Звук получения очков (приятный звон)
        score_samples = []
        for i in range(int(sample_rate * 0.15)):
            t = i / sample_rate
            value = int(100 * math.sin(2 * math.pi * 1200 * t) * (1 - t * 6))
            score_samples.append(max(-128, min(127, value)))
        
        # Звук game over (низкий гул)
        gameover_samples = []
        for i in range(int(sample_rate * 0.5)):
            t = i / sample_rate
            value = int(80 * math.sin(2 * math.pi * 200 * t) * (1 - t * 2))
            gameover_samples.append(max(-128, min(127, value)))
        
        # Создаем звуки
        try:
            self.sounds['shoot'] = pygame.mixer.Sound(buffer=bytes([s + 128 for s in shoot_samples]))
            self.sounds['shoot'].set_volume(0.3)
            
            self.sounds['explosion'] = pygame.mixer.Sound(buffer=bytes([s + 128 for s in explosion_samples]))
            self.sounds['explosion'].set_volume(0.4)
            
            self.sounds['score'] = pygame.mixer.Sound(buffer=bytes([s + 128 for s in score_samples]))
            self.sounds['score'].set_volume(0.3)
            
            self.sounds['gameover'] = pygame.mixer.Sound(buffer=bytes([s + 128 for s in gameover_samples]))
            self.sounds['gameover'].set_volume(0.5)
        except:
            self.enabled = False
    
    def play(self, sound_name):
        """Воспроизводит звук по имени"""
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            self.sounds[sound_name].play()
        except:
            pass
    
    def toggle(self):
        """Включает/выключает звук"""
        self.enabled = not self.enabled
        return self.enabled


class RegistryManager:
    """Класс для работы с реестром Windows"""
    
    def __init__(self):
        self.registry_path = r"Software\SpaceShooterGame"
        self.values_count = 10
        self.editable_values = [
            "GamesPlayed",
            "TotalEnemiesDestroyed", 
            "TotalBulletsFired",
            "PlayTimeSeconds",
            "HighestCombo",
            "PowerUpsCollected",
            "DamageTaken",
            "BossesDefeated",
            "SecretsFound"
        ]
        if sys.platform == 'win32' and winreg:
            self.create_registry_keys()
    
    def create_registry_keys(self):
        """Создает 10 значений в реестре (только если их нет)"""
        try:
            # Сначала пробуем открыть существующий ключ
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path)
                # Если ключ открылся успешно, значит он уже существует - просто закрываем его
                winreg.CloseKey(key)
                print(f"✓ Раздел реестра уже существует, пропускаем инициализацию")
                return
            except FileNotFoundError:
                # Ключ не найден, создаем новый
                pass
            
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            
            # 10 различных значений (устанавливаются только при первом запуске!)
            values = {
                "MaxScore": 0,  # Начинаем с 0, игрок сам набивает рекорд
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
            print(f"✓ Создано {len(values)} значений в реестре (первый запуск)")
            
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
    
    def get_value(self, value_name):
        """Получает значение из реестра"""
        if sys.platform != 'win32' or not winreg:
            return 0
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return value
        except:
            return 0
    
    def set_value(self, value_name, value):
        """Устанавливает значение в реестр (кроме MaxScore)"""
        if value_name == "MaxScore":
            return False  # MaxScore нельзя менять через интерфейс
        
        if sys.platform == 'win32' and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                winreg.CloseKey(key)
                return True
            except Exception as e:
                print(f"Ошибка записи в реестр: {e}")
        return False
    
    def increment_games_played(self):
        """Увеличивает счетчик сыгранных игр"""
        self._increment_value("GamesPlayed")
    
    def increment_enemies_destroyed(self, count=1):
        """Увеличивает счетчик уничтоженных врагов"""
        self._increment_value("TotalEnemiesDestroyed", count)
    
    def increment_bullets_fired(self, count=1):
        """Увеличивает счетчик выпущенных пуль"""
        self._increment_value("TotalBulletsFired", count)
    
    def update_play_time(self, seconds):
        """Обновляет время игры"""
        current = self.get_value("PlayTimeSeconds")
        self.set_value("PlayTimeSeconds", current + seconds)
    
    def update_highest_combo(self, combo):
        """Обновляет максимальное комбо"""
        current = self.get_value("HighestCombo")
        if combo > current:
            self.set_value("HighestCombo", combo)
    
    def _increment_value(self, value_name, amount=1):
        """Увеличивает значение на amount"""
        if sys.platform == 'win32' and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
                current, _ = winreg.QueryValueEx(key, value_name)
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, current + amount)
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
        self.sound_manager = SoundManager()
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
        self.small_font = pygame.font.Font(None, 28)
        self.game_over = False
        self.paused = False
        self.show_stats = False
        self.clock_time = 0
        self.start_time = pygame.time.get_ticks()
        self.selected_stat_index = 0
        self.stat_edit_mode = False
        self.edit_value_buffer = ""
    
    def create_explosion(self, x, y, color):
        for _ in range(15):
            particle = Particle(x, y, color)
            self.all_sprites.add(particle)
            self.particles.add(particle)
    
    def draw_button(self, text, x, y, width, height, color, hover_color=None, active=False):
        """Рисует кнопку и возвращает True если нажата"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        rect = pygame.Rect(x, y, width, height)
        is_hovered = rect.collidepoint(mouse_pos)
        
        if is_hovered and hover_color:
            draw_color = hover_color
        elif active:
            draw_color = GREEN
        else:
            draw_color = color
        
        pygame.draw.rect(screen, draw_color, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
        
        text_surface = self.small_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        
        return is_hovered and mouse_clicked
    
    def draw_stats_panel(self):
        """Рисует панель статистики с возможностью редактирования"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Заголовок
        title = self.big_font.render("СТАТИСТИКА ИГРЫ", True, LIGHT_BLUE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 50)))
        
        stats = self.registry.get_all_stats()
        editable = self.registry.editable_values
        
        y_offset = 100
        row_height = 35
        
        # Отображение статистики
        for i, stat_name in enumerate(editable + ["MaxScore"]):
            if stat_name in stats:
                value = stats[stat_name]
                is_editable = stat_name != "MaxScore"
                
                # Цвет строки
                if stat_name == "MaxScore":
                    color = YELLOW
                elif i == self.selected_stat_index and self.stat_edit_mode:
                    color = GREEN
                elif i == self.selected_stat_index:
                    color = LIGHT_BLUE
                else:
                    color = WHITE
                
                # Текст
                display_name = stat_name.replace("Total", "").replace("Seconds", " сек").replace("Played", " игр")
                text = f"{display_name}: {value:,}"
                
                if is_editable and i == self.selected_stat_index and self.stat_edit_mode:
                    text = f"{display_name}: {self.edit_value_buffer}_"
                    color = GREEN
                
                text_surface = self.small_font.render(text, True, color)
                screen.blit(text_surface, (100, y_offset + i * row_height))
        
        # Подсказки
        hints_y = HEIGHT - 120
        hint1 = self.small_font.render("↑↓ - выбор значения", True, GRAY)
        hint2 = self.small_font.render("Enter - редактировать | +/- или цифры - изменить значение", True, GRAY)
        hint3 = self.small_font.render("ESC - закрыть панель | M - звук вкл/выкл", True, GRAY)
        
        screen.blit(hint1, (100, hints_y))
        screen.blit(hint2, (100, hints_y + 30))
        screen.blit(hint3, (100, hints_y + 60))
        
        # Кнопка выхода
        if self.draw_button("Закрыть", WIDTH//2 - 60, HEIGHT - 50, 120, 40, RED, DARK_GRAY):
            self.show_stats = False
    
    def handle_stat_input(self, event):
        """Обработка ввода для редактирования статистики"""
        editable = self.registry.editable_values
        stats_list = editable + ["MaxScore"]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_stats = False
                self.stat_edit_mode = False
                self.edit_value_buffer = ""
            elif event.key == pygame.K_UP:
                if not self.stat_edit_mode:
                    self.selected_stat_index = (self.selected_stat_index - 1) % len(stats_list)
            elif event.key == pygame.K_DOWN:
                if not self.stat_edit_mode:
                    self.selected_stat_index = (self.selected_stat_index + 1) % len(stats_list)
            elif event.key == pygame.K_RETURN:
                if self.selected_stat_index < len(editable):
                    stat_name = editable[self.selected_stat_index]
                    current_value = self.registry.get_value(stat_name)
                    self.edit_value_buffer = str(current_value)
                    self.stat_edit_mode = True
            elif event.key == pygame.K_BACKSPACE:
                if self.stat_edit_mode:
                    self.edit_value_buffer = self.edit_value_buffer[:-1]
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                if self.stat_edit_mode:
                    try:
                        val = int(self.edit_value_buffer) if self.edit_value_buffer else 0
                        self.edit_value_buffer = str(val + 1)
                    except:
                        self.edit_value_buffer = "1"
            elif event.key == pygame.K_MINUS:
                if self.stat_edit_mode:
                    try:
                        val = int(self.edit_value_buffer) if self.edit_value_buffer else 0
                        self.edit_value_buffer = str(max(0, val - 1))
                    except:
                        self.edit_value_buffer = "0"
            elif event.unicode.isdigit():
                if self.stat_edit_mode:
                    self.edit_value_buffer += event.unicode
            
            elif event.key == pygame.K_SPACE and self.stat_edit_mode:
                # Сохранение значения
                try:
                    new_value = int(self.edit_value_buffer)
                    stat_name = editable[self.selected_stat_index]
                    if self.registry.set_value(stat_name, new_value):
                        self.stat_edit_mode = False
                        self.edit_value_buffer = ""
                except:
                    pass
    
    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Обработка панели статистики
                if self.show_stats:
                    self.handle_stat_input(event)
                    continue
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_over:
                            running = False
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_TAB and not self.game_over:
                        # Открытие/закрытие панели статистики
                        self.show_stats = True
                        self.selected_stat_index = 0
                        self.stat_edit_mode = False
                    elif event.key == pygame.K_m:
                        # Включение/выключение звука
                        sound_state = self.sound_manager.toggle()
                        print(f"Звук: {'ВКЛ' if sound_state else 'ВЫКЛ'}")
                    elif event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                        bullet = self.player.shoot()
                        if bullet:
                            self.all_sprites.add(bullet)
                            self.bullets.add(bullet)
                            self.registry.increment_bullets_fired()
                            self.sound_manager.play('shoot')
                    elif event.key == pygame.K_r and self.game_over:
                        self.__init__()
            
            # Отрисовка панели статистики
            if self.show_stats:
                screen.fill(BLACK)
                self.draw_stats_panel()
                pygame.display.flip()
                continue
            
            if not self.paused and not self.game_over:
                self.all_sprites.update()
                
                # Стрельба врагов (упрощено)
                hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
                for enemy in hits:
                    self.create_explosion(enemy.rect.centerx, enemy.rect.centery, RED)
                    self.sound_manager.play('explosion')
                    self.sound_manager.play('score')
                    enemy.kill()
                    self.score += 10
                    self.combo += 1
                    self.registry.increment_enemies_destroyed()
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
                    self.sound_manager.play('gameover')
                    
                    # Обновляем статистику в реестре
                    self.registry.set_max_score(self.score)  # Только если больше текущего
                    self.registry.increment_games_played()
                    self.registry.update_highest_combo(self.max_combo)
                    
                    # Получаем обновленный макс счет для отображения
                    self.max_score = self.registry.get_max_score()
                
                self.clock_time += 1
                
                # Обновление времени игры каждые 60 кадров (1 секунда)
                if self.clock_time % 60 == 0:
                    self.registry.update_play_time(1)
            
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
            
            # Индикатор звука
            sound_icon = "🔊" if self.sound_manager.enabled else "🔇"
            sound_text = self.small_font.render(sound_icon, True, WHITE)
            
            screen.blit(score_text, (10, 10))
            screen.blit(max_score_text, (10, 50))
            screen.blit(combo_text, (10, 90))
            screen.blit(sound_text, (WIDTH - 40, 10))
            
            # Подсказка для панели статистики
            stats_hint = self.small_font.render("TAB - Статистика", True, GRAY)
            screen.blit(stats_hint, (WIDTH - 150, 40))
            
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
    print("🚀 SPACE SHOOTER PRO - Космический Шутер")
    print("=" * 50)
    print(f"Платформа: {sys.platform}")
    
    if sys.platform == 'win32':
        print("✓ Режим Windows: работа с реестром активна")
        print("📁 Игра создаст раздел: HKEY_CURRENT_USER\\Software\\SpaceShooterGame")
        print("📊 10 значений будут сохранены в реестре")
        print("💾 MaxScore начинается с 0 и обновляется только при новом рекорде!")
        print("⚠️  Рекорд НЕ будет перезаписываться при каждом запуске!")
        print("✏️  9 значений можно редактировать через интерфейс игры (TAB)")
    else:
        print("⚠ Не Windows: данные сохраняются в файл")
        print(f"📁 Путь: {SAVE_DIR}")
    
    print("\n🎮 Управление:")
    print("  Стрелки или WASD - движение")
    print("  Пробел - стрельба")
    print("  ESC - пауза/выход")
    print("  R - рестарт после проигрыша")
    print("  TAB - панель статистики (редактирование значений)")
    print("  M - включить/выключить звук")
    print("\n📝 В панели статистики (TAB):")
    print("  ↑↓ - выбор значения")
    print("  Enter - начать редактирование")
    print("  Цифры, +, -, Backspace - изменение")
    print("  Пробел - сохранить значение")
    print("  ESC - закрыть панель")
    print("=" * 50)
    
    game = Game()
    game.run()
