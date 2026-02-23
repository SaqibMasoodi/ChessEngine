# Retro Chess Engine

We will dethrone chess.com, Insha'Allah.

## Features
- **Retro UI:** Simple brown and cream colors with 3D buttons.
- **Auto-Flip Board:** Rotates so you always play from the bottom.
- **Alerts:** On-screen messages for check, checkmate, and invalid moves.
- **Image Viewer:** Shows changing pictures from the `Chess/images/media/` folder.
- **Move Log:** Shows the history of white and black moves.
- **Chess Rules:** Includes castling, en passant, and pawn promotion.
- **Sounds:** Plays audio for moves, captures, checks, and errors.

For more details on how the engine works, read the [Engine Explanation](ENGINE_EXPLANATION.md).

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
For a full breakdown of the assets, audio, and algorithmic resources used in this project, please refer to my [CREDITS.md](Credits) file.

---
![Here is a screengrab!](image-1.png)
