# Chess Engine Explanation


## Overview
This file documents the internal working of `Chess/ChessEngine.py`. 

**Important Definition**: In the context of this project, "Engine" refers to a **Game State Manager** and **Rules Validator**. I call it an engine only because it sounds cool. It handles the logic of chess rules (valid moves, checkmate, castling) but **does not currently contain an Artificial Intelligence (AI)** to play against. It is effectively a "Rules Engine" designed to facilitate a 2-player game (PvP).

## Logic & Architecture

### 1. Board Representation
The board is represented as a **8x8 2D List** (Array of Arrays) in Python.
-   **Structure**: `self.board[row][col]`
-   **Data**: Strings of 2 characters.
    -   1st char: Color ('w' for White, 'b' for Black).
    -   2nd char: Type ('P', 'R', 'N', 'B', 'Q', 'K').
    -   Empty squares are represented by `"--"`.

### 2. Move Generation Strategy
The engine uses a "Pseudo-Legal" to "Legal" move generation pipeline:
1.  **Generate All Possible Moves**: Iterate through every square on the board. If the piece belongs to the active player, generate all physically possible moves for that piece (ignoring checks).
    -   *Sliding Pieces (Rook, Bishop, Queen)*: Iteratively check along directions until blocked.
    -   *Stepping Pieces (Knight, King)*: Check fixed offsets.
    -   *Pawns*: Complex logic including single/double steps, diagonal captures, and En Passant.
2.  **Filter for Legality**: For every generated "possible" move:
    -   **Simulate**: Make the move on the board.
    -   **Verify**: Check if the current player's King is under attack (`inCheck()`).
    -   **Undo**: Revert the move.
    -   If the King remained safe, the move is added to the **Valid Moves** list.

### 3. Special Rules Implementation
-   **Castling**: Managed via a `CastleRights` class ensuring Kings/Rooks haven't moved. Logic checks for empty squares and safe path (king cannot pass through check).
-   **En Passant**: Tracked via `enPassantPossible` coordinate, updated every turn.
-   **Promotion**: Strings are modified (e.g., 'wP' becomes 'wQ') upon reaching the 8th rank.

## Performance Analysis

### Computational Complexity
-   **Move Generation**: Slow ($O(N)$ with high constant factors). Python lists are slower than low-level arrays.
-   **Validation Cost**: Expensive. To verify *one* move, the engine must generate *all* opponent moves to ensure the King isn't attacked. This leads to a complexity of roughly $O(M^2)$ per turn (where M is valid moves), which is significant.
    -   *Impact*: Fine for humans (seconds/instant), but would be extremely slow for an AI trying to search millions of positions.

### Comparison to Popular Engines (e.g., Stockfish)

| Feature | This Engine | Stockfish / Modern Engines |
| :--- | :--- | :--- |
| **Logic** | 2D List, Naive Loop | Bitboards (64-bit integers), CPU instructions |
| **Language** | Python (Interpreted) | C++ / Assembly (Compiled, optimized) |
| **Move Gen** | ~100s-1000s positions/sec | >200,000,000 positions/sec |
| **AI / Search** | **None** (cannot play) | Alpha-Beta Pruning, Negamax, Quiescence |
| **Evaluation** | None | Neural Nets (NNUE), Hand-tuned Heuristics |
| **Strength** | **0 ELO** (Rule Enforcer) | **3500+ ELO** (Superhuman) |

### 4. User Interface (Retro Tactile Python)
The primary interface is built using **PyGame** in `ChessMain.py`, featuring a custom design system:
-   **Game Layout**: 
    -   **Visual Hierarchy**: Dynamic board rendering on the left (Auto-flips based on active player turn), and a dual-column Move Log on the right.
    -   **Status Dialog (CRT)**: A specialized panel utilizing Pygame border shadowing, phosphor-colored masks, and alpha-blended scanlines to deliver transient game states.
    -   **Media Window**: Below the Status Dialog, cycles through `.png`/`.jpg` files located in `Chess/images/media/` asynchronously using a `p.time.get_ticks()` modulo rendering loop. 
-   **Design Language**:
    -   **Tactile Palette**: Earthy colors combined with physical panel CSS-like manipulations (Corner radii, inset shadows, depressed tiles). See `STYLE_GUIDE.md` for exact hex codes.
    -   **Asset Styling**: 
        -   **Pieces**: Smooth-scaled to 85% of square size for consistent padding.
        -   **Coordinates**: Integrated file/rank labels with dynamic color contrast based on tile parity.
-   **Move Log**: Features a specialized auto-scrolling buffer showing the latest moves in Algebraic Notation (e.g. `1. e4 e5`), ensuring UI stability during long matches.

## Conclusion
This engine is a **foundational framework** for a Chess UI. It correctly enforces the rules of Chess, allowing two humans to play in a premium-feeling environment. Future work will focus on the Artificial Intelligence layers (Minimax/Alpha-Beta) to transform it from a rule enforcer into a tactical opponent.

---

## Appendix: Status & Error Messages (CRT Dialog)

The following transient and persistent messages are displayed in the Pygame CRT Status Dialog based on game state events:

### Turn States (Persistent)
- `White to Move`
- `Black to Move`

### Game End States (Persistent)
- `Checkmate! White Wins`
- `Checkmate! Black Wins`
- `Stalemate`

### In-Game Events (Transient)
- `Check!` (Displayed briefly when a King is attacked, text turns brown)

### Error Messages (Transient)
Displayed when the user attempts an invalid action (text turns terra/red):
- `Invalid: Not your piece` (Clicking an empty square or opponent's piece)
- `Invalid: You are in Check` (Attempting to move a piece that doesn't resolve a check)
- `Illegal: Must escape Check` (Attempting a move destination that leaves the King in check)
- `Illegal: Invalid destination` (Attempting to move a piece to a non-valid square)
- `Move Undone` (Triggered via Undo button or `Z` key)
