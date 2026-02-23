# Retro Chess Engine

We will dethrone chess.com, Insha'Allah.

## Constraints
- **Over-the-board PvP:** Two players take turns on the same device, with the board rotating so each player always plays from the bottom.
- **No AI Support (Yet):** Currently supports only real-world, two-player matches—no bot integration.

I have documented how the engine works in [Engine Explanation](ENGINE_EXPLANATION.md). 

## Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/SaqibMasoodi/ChessEngine.git
cd ChessEngine
pip install -r requirements.txt
```

## How to Play
Run the application:

```bash
python Chess/ChessMain.py
```

**Controls**:
- **Mouse / Touch:** Click to select, highlight valid targets, and move pieces.
- **Button Panel:** Located at the bottom right. Features pixelated icons for:
  - **Undo**: Reverts the last move (and restores captured pieces/castling rights).
  - **Redo**: Tracks alternate timeline moves unless a new divergent move is played.
  - **Reset**: Instantly resets the board securely without holding ghost states.
  - **Mute**: Toggles sound engine.
- **Keyboard Shortcut:** Press `Z` to rapidly Undo.

## Credits
For a full breakdown of the assets, audio, and algorithmic resources used in this project, refer to [Credits](CREDITS.md) .

---
![Here is a screengrab!](image.png)

