@echo off
echo Installing Space Shooter for Windows...
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден! Пожалуйста, установите Python 3.8 или выше.
    echo Скачайте с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Установка необходимых библиотек...
pip install pygame

echo.
echo Установка завершена!
echo.
echo Для запуска игры выполните: python space_shooter.py
echo.
echo Игра сохраняет 20 значений в реестре Windows:
echo HKEY_CURRENT_USER\Software\SpaceShooterGame
echo.
pause
