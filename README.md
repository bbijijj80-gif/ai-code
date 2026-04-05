# Space Shooter Game

Space shooter game with great graphics, sound, and smart AI enemies.

## Features

- 🎮 Dynamic gameplay
- 🎵 Procedural sound and music generation
- ✨ Beautiful animated starfield background
- 🎯 20 saved parameters (including best score)
- 🤖 Smart enemies with different behaviors
- 💥 Explosion effects
- ⚡ Power-ups and upgrades

## 20 Saved Values

1. **best_score** - Best score achieved
2. **total_games** - Total games played
3. **total_enemies_destroyed** - Enemies destroyed
4. **total_shots_fired** - Shots fired
5. **total_powerups_collected** - Power-ups collected
6. **play_time_seconds** - Total play time
7. **last_played** - Last played date
8. **player_name** - Player name
9. **difficulty** - Difficulty level
10. **sound_enabled** - Sound on/off
11. **music_enabled** - Music on/off
12. **screen_width** - Screen width
13. **screen_height** - Screen height
14. **fullscreen** - Fullscreen mode
15. **ship_color_r** - Ship color (Red)
16. **ship_color_g** - Ship color (Green)
17. **ship_color_b** - Ship color (Blue)
18. **particles_enabled** - Particles on/off
19. **show_fps** - Show FPS
20. **language** - Interface language

## Installation & Running

### Windows

1. Open the `windows_version` folder
2. Run `install.bat` to install dependencies
3. Run the game: `python space_shooter.py`

**Data Storage:** Windows Registry  
**Path:** `HKEY_CURRENT_USER\Software\SpaceShooterGame`

### Linux

1. Open the `linux_version` folder
2. Run `./install.sh` to install dependencies
3. Run the game: `python3 space_shooter.py`

**Data Storage:** Configuration file  
**Path:** `~/.config/space_shooter/settings.json`

## Controls

- **Arrow Keys** or **WASD** - Move ship
- **Space** - Shoot
- **ESC** - Pause
- **R** - Restart (after game over)

## Requirements

- Python 3.8 or higher
- pygame library

## Project Structure

```
/workspace
├── game_core.py              # Main game code
├── assets/                   # Game resources
├── windows_version/          # Windows version
│   ├── space_shooter.py      # Game with Windows registry
│   └── install.bat           # Installer
└── linux_version/            # Linux version
    ├── space_shooter.py      # Game with file storage
    └── install.sh            # Installer
```

## Notes

- Values in registry/config are **NOT reset** on each launch
- Best score is automatically saved
- All 20 parameters are saved after each change
- Windows version uses native registry API via ctypes
