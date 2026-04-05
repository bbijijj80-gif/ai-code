#!/bin/bash
# Скрипт запуска космического шутера "Крестики"

cd "$(dirname "$0")"

# Проверка установки pygame
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Установка pygame..."
    pip3 install pygame --user
fi

# Запуск игры
python3 main.py
