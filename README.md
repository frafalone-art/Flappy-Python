# Flappy Python 🐦

A Flappy Bird-inspired clone built with Python and pygame, developed as a personal learning project to explore game development fundamentals.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python) ![Pygame](https://img.shields.io/badge/Pygame-2.x-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Purpose](https://img.shields.io/badge/Purpose-Educational-orange)

---

## 🎮 Gameplay
- Press **SPACE** or click **▶ PLAY** to start
- Press **SPACE** to flap
- Avoid the pipes and the ground
- Scores are saved automatically to a local leaderboard

## ✨ Features
- Animated main menu
- Parallax scrolling background
- Automatic day/night cycle based on real local time
- Local Top 5 leaderboard (saved to JSON)
- Gold-highlighted record on the game over screen
- Sound effects and background music
- Credits screen

## 🛠️ Requirements
Python 3.x and pygame:
```bash
pip install pygame
```

## ▶️ Running the game
```bash
python Flappy_Bird.py
```
All asset files (images, sounds) must be placed in the same folder as `Flappy_Bird.py`.

## 📁 Project structure
```
flappy-python/
├── Flappy_Bird.py          # Main source code
├── FlappyBird.png          # Game logo
├── Sfondo.png              # Daytime background
├── notte.png               # Nighttime background
├── Pavimento.png           # Ground sprite
├── uccelo.jpeg             # Bird sprite
├── Tubo verticale.png      # Pipe sprite
├── Game Over.png           # Game over screen
├── battito.wav             # Flap sound effect
├── sconfitta.wav           # Death sound effect
├── punto.wav               # Score sound effect
├── musica.mp3              # Background music
├── leaderboard.json        # Auto-generated on first run
├── README.md
└── LICENSE
```

## 🧠 Concepts covered
This project was built to practice the following Python fundamentals:
- Object-oriented programming (classes, methods, `__init__`)
- Game loop architecture and state machines (`menu / game / game_over`)
- Collision detection with `pygame.Rect`
- File I/O with `json` and `os`
- Math utilities (`math.sin` for smooth animations)
- Event handling and keyboard/mouse input

## ⚠️ Disclaimer
This project is made **for educational and personal purposes only**.  
The Flappy Bird concept is the original work of **Dong Nguyen** ([@dongatory](https://twitter.com/dongatory)).  
All graphic and audio assets used are original creations by the author.  
This project is not affiliated with, sponsored by, or endorsed by the original creator.  
It is not distributed or used for any commercial purpose.

## 👨‍💻 Author
**Francesco Falone** — personal project to learn Python and pygame.

## 📄 License
This project is licensed under the [MIT License](LICENSE).
