# 🎮 Retro Arcade Tic-Tac-Toe

A modern, responsive **Retro Arcade** themed Tic-Tac-Toe game built with **Python** and **Streamlit**. Features offline 2-player local multiplayer and an unbeatable Player vs Computer mode powered by a **recursive Minimax defense algorithm**.

---

## ✨ Features

- **Two Game Modes**
  - 👥 **Player vs Player (PvP)** — Local offline multiplayer on the same device.
  - 🤖 **Player vs Computer (PvC)** — Play against an AI that uses recursive Minimax to block your winning moves.
- **Shape Selection** — Both players can choose between ❌ Cross (X) and ⭕ Circle (O) before starting.
- **Undo Move** — Step back moves at any time using the ↩️ Undo button.
- **Move Replay & Highlights** — After a match ends, view a step-by-step replay of every move with a turn slider.
- **Winning Strike Line** — A red line visually highlights the winning row, column, or diagonal.
- **Celebration Effects** — Balloons and confetti on win/draw outcomes.
- **Retro Arcade Theme** — Custom dark-mode UI with neon accents, pixel-inspired aesthetics, and smooth animations.
- **Fully Responsive** — Works on desktop and mobile browsers.

---

## 🛠️ Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.10+** | Core game logic, recursive Minimax AI |
| **Streamlit** | Web-based UI framework |
| **HTML / CSS** | Custom retro arcade theme styling |
| **JSON** | Theme configuration (`game-theme.json`) |

---

## 📁 Project Structure

```
Retro-Arcade-Tic-Tac-Toe/
├── app.py                  # Main application (game logic + UI)
├── game-theme.json         # Retro arcade theme configuration
├── test_tictactoe.py       # Unit tests for game logic & Minimax AI
├── test_undo_highlights.py # Unit tests for undo & highlight system
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 📦 Prerequisites

### 1. Python Installation
Make sure **Python 3.10 or higher** is installed on your system.

```bash
python --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

### 2. Install Streamlit

Run the following command in your terminal:

```bash
pip install streamlit
```

> **Tip for Windows users with multiple Python versions:**
> ```bash
> python -m pip install streamlit
> ```
> or specify the version:
> ```bash
> py -3.13 -m pip install streamlit
> ```

### 3. Verify Installation

```bash
streamlit --version
```

You should see output like:
```
Streamlit, version 1.66.0 (or newer)
```

---

## 🚀 How to Run

### Method 1: Using the `streamlit` command (Recommended)

1. Open your terminal (PowerShell / Command Prompt / Terminal).
2. Navigate to the project folder:
   ```bash
   cd path/to/Retro-Arcade-Tic-Tac-Toe
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Your default browser will open automatically at:
   ```
   http://localhost:8501
   ```

### Method 2: Using the Python module flag

If `streamlit` is not on your system PATH:

```bash
python -m streamlit run app.py
```

---

## 🧪 Running Tests

Run the automated test suites to verify game logic, AI behavior, undo system, and replay mechanics:

```bash
python test_tictactoe.py
python test_undo_highlights.py
```

Both test suites will run simulations and verify all game mechanics with a **100% pass rate**.

---

## 🕹️ Game Controls

| Control | Description |
| :--- | :--- |
| **Mode Selector** | Switch between `👥 2 Players (PvP)` and `🤖 vs Computer (PvC)` |
| **Shape Selector** | Choose between `❌ Cross (X)` and `⭕ Circle (O)` before starting |
| **Undo Move** | Click `↩️ Undo Move` to step back moves |
| **Restart Game** | Click `🔄 Restart Game` to clear the board and pick new shapes |
| **Move Replay** | After a match, click `🎬 View Move Highlights` to step through every move |

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| `'streamlit' is not recognized` | Use `python -m streamlit run app.py` instead |
| `Port 8501 is already in use` | Close the other Streamlit instance, or use a different port: `streamlit run app.py --server.port 8502` |
| `ModuleNotFoundError: No module named 'streamlit'` | Run `python -m pip install streamlit` to install in your active Python environment |
| Changes not updating on the page | Click **Rerun** in the Streamlit toolbar, or press `Ctrl + R` to refresh |

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

> Built with ❤️ using Python & Streamlit
