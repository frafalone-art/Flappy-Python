# Flappy Python 🐦

A Flappy Bird-inspired clone built with Python and pygame, developed as a personal learning project to explore game development fundamentals.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Purpose](https://img.shields.io/badge/Purpose-Educational-orange)

---

# 🎮 Gameplay

- Press **SPACE** or click **▶ PLAY** to start
- Press **SPACE** to flap
- Avoid the pipes and the ground
- Try to beat your highest score
- Scores are automatically saved locally

---

# ✨ Features

- Animated main menu
- Day / night cycle based on real local time
- Local Top 5 leaderboard system
- Credits screen
- Smooth scrolling background and ground
- Sound effects and background music
- Game Over screen with highlighted best score
- Mouse and keyboard support

---

# 🛠️ Requirements

Install pygame:

```bash
pip install pygame
```

---

# ▶️ Run from source

```bash
python Flappy_Bird.py
```

---

# 📦 EXE Version

A standalone Windows `.exe` version will be available in the repository Releases section.

The executable includes:
- all images
- sound effects
- music
- leaderboard support

No Python installation is required.

---

# 📁 Project Structure

```text
flappy-python/
│
├── assets/
│   │
│   ├── images/
│   │   ├── FlappyBird.png
│   │   ├── background_day.png
│   │   ├── background_night.png
│   │   ├── ground.png
│   │   ├── bird.jpeg
│   │   ├── pipe.png
│   │   └── game_over.png
│   │
│   └── sounds/
│       ├── battito.wav
│       ├── defeat.wav
│       ├── point.wav
│       └── musica.mp3
│
├── data/
│   └── leaderboard.json
│
├── Flappy_Bird.py
├── README.md
└── LICENSE
```

---

# 🧠 Concepts Covered

This project was built to practice:

- Object-oriented programming
- Game loop architecture
- State management
- Collision detection using `pygame.Rect`
- File handling with `json`
- Audio management with pygame mixer
- Smooth animations using math functions
- Keyboard and mouse event handling

---

# 🎨 Screens Included

- Main Menu
- Gameplay
- Leaderboard
- Credits
- Game Over

---

# ⚠️ Disclaimer

This project was created for educational and personal purposes only.

The original Flappy Bird concept belongs to Dong Nguyen.

This repository is not affiliated with or endorsed by the original creator.

All included graphics and audio assets are personal assets made for this project.

---

# 👨‍💻 Author

**Francesco Falone**

Personal project made to improve Python and pygame development skills.

---

# 📄 License

This project is licensed under the MIT License.
