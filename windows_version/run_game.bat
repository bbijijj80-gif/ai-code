@echo off
REM Скрипт запуска для Windows
echo Запуск Космического Шутера...

REM Проверка установки Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не найден!
    echo Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Проверка и установка pygame если нужно
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Установка pygame...
    pip install pygame
)

REM Запуск игры
cd /d "%~dp0"
python space_shooter.py

echo Игра завершена.
pause
