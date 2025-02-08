"""Main driver file for displaying the game state."""

import pygame as p
import sys
sys.path.append('C:\\Users\\masud\\Desktop\\Me')  # Explicitly adds the directory for module lookups
from Chess import ChessEngine

# Constants to be used down the road
WIDTH = HEIGHT = 512  # Dimensions of the game window
DIMENSION = 8         
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}           


def loadImages():
    """Load chess piece images without resizing."""
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        image_path = f"Chess/images/{piece}.png"
        IMAGES[piece] = p.image.load(image_path).convert_alpha()


def main():
    """Main function to initialize the game and handle the main loop."""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()  # Initialize the game state
    loadImages()  # Load images before entering the game loop

    sqSelected = () #Click, empty initially (x, y)
    playerClicks = [] #[(x1, y1), (x2, y2)]
    
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: #Mouse logic
                location = p.mouse.get_pos() 
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col): #Case where same tile is clicked twice
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2: #Two clicks are registered
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board )
                    print(move.getChessNotation())
                    gs.makeMove(move)
                    sqSelected = () #reset clicks
                    playerClicks = []
    
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    """Draw the current game state."""
    drawBoard(screen)             # Draw squares
    drawPieces(screen, gs.board)  # Draw pieces


def drawBoard(screen):
    """Draw the chessboard."""
    colors = [p.Color(255, 255, 255), p.Color(115, 149, 80)]  
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    """Draw the chess pieces on the board."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
if __name__ == "__main__":
    main()
