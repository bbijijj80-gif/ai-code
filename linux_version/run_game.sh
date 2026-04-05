#!/bin/bash

# Скрипт запуска для Linux
echo "Запуск Космического Шутера..."

# Проверка установки Python 3
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python 3 не найден!"
    echo "Установите Python 3: sudo apt-get install python3"
    exit 1
fi

# Проверка и установка pygame если нужно
if ! python3 -c "import pygame" &> /dev/null; then
    echo "Установка pygame..."
    pip3 install --user pygame
fi

# Запуск игры
cd "$(dirname "$0")"
python3 space_shooter.py

echo "Игра завершена."
