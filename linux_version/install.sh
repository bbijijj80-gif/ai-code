#!/bin/bash

echo "====================================="
echo "Космический Шутер - Версия для Linux"
echo "====================================="
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден!"
    echo "Установите Python 3.8 или выше:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "Проверка версии Python..."
python3 --version

# Установка pygame
echo ""
echo "Установка библиотеки pygame..."
pip3 install pygame --user

echo ""
echo "====================================="
echo "Установка завершена!"
echo "====================================="
echo ""
echo "Для запуска игры выполните:"
echo "  python3 space_shooter.py"
echo ""
echo "Настройки сохраняются в:"
echo "  ~/.config/space_shooter/settings.json"
echo ""
echo "Игра хранит 20 значений:"
echo "  - best_score (лучший счёт)"
echo "  - total_games (всего игр)"
echo "  - total_enemies_destroyed (уничтожено врагов)"
echo "  - total_shots_fired (сделано выстрелов)"
echo "  - total_powerups_collected (собрано бонусов)"
echo "  - play_time_seconds (время игры)"
echo "  - last_played (последний запуск)"
echo "  - player_name (имя игрока)"
echo "  - difficulty (сложность)"
echo "  - sound_enabled (звук включён)"
echo "  - music_enabled (музыка включена)"
echo "  - screen_width (ширина экрана)"
echo "  - screen_height (высота экрана)"
echo "  - fullscreen (полноэкранный режим)"
echo "  - ship_color_r (цвет корабля R)"
echo "  - ship_color_g (цвет корабля G)"
echo "  - ship_color_b (цвет корабля B)"
echo "  - particles_enabled (частицы включены)"
echo "  - show_fps (показывать FPS)"
echo "  - language (язык)"
echo ""
