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

## Conclusion
This engine is a **foundational framework** for a Chess UI. It correctly enforces the rules of Chess, allowing two humans to play. To make it "smart" (AI), one would need to add:
1.  **Evaluation Function**: To score a board position (e.g., Material count).
2.  **Search Algorithm**: Minimax or Negamax to look ahead.
3.  **Optimizations**: Alpha-Beta pruning to filter bad moves early.
