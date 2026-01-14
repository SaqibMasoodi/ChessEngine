# Chess Engine Explanation

## Overview
This file documents the internal working of the Chess implementation found in `Chess/ChessEngine.py`. 

**Important Definition**: In the context of this project, "Engine" refers to a **Game State Manager** and **Rules Validator**. It handles the logic of chess rules (valid moves, checkmate, castling) but **does not currently contain an Artificial Intelligence (AI)** to play against. It is effectively a "Rules Engine" designed to facilitate a 2-player game (PvP).

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

### 4. User Interface (Python/PyGame)
The primary interface is built using **PyGame** in `ChessMain.py`.
-   **Game Loop**: A standard event loop runs at 15 FPS, handling user input (mouse clicks) and rendering updates.
-   **Visuals**:
    -   **Board & Pieces**: Renders the 8x8 grid and overlays PNG images for pieces.
    -   **Move Log**: A custom-drawn panel (`drawMoveLog`) displays the history of moves in algebraic notation, constructed manually via text blitting.
    -   **Highlights**: Selected squares and valid moves are highlighted for better UX.

## 5. Standalone Web Preview
A separate, frontend-only preview is available in `index.html`.
-   **Purpose**: To demonstrate a modernized, aesthetic UI concept ("Retro Tactile") without taking a dependency on the Python backend.
-   **Tech Stack**: HTML, **Tailwind CSS** (via CDN for styling), and Vanilla JavaScript (for board generation and simple interactivity).
-   **Status**: This is a *visual prototype*. It has no game logic, rule enforcement, or AI connectivity. It solely renders a static board state or simple interactive demo.

## Conclusion
This engine is a **foundational framework** for a Chess UI. It correctly enforces the rules of Chess, allowing two humans to play. To make it "smart" (AI), one would need to add:
1.  **Evaluation Function**: To score a board position (e.g., Material count).
2.  **Search Algorithm**: Minimax or Negamax to look ahead.
3.  **Optimizations**: Alpha-Beta pruning to filter bad moves early.
