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

    gs = ChessEngine.GameState()     #Initialize the game state
    validMoves = []
    validMoves = gs.getValidMoves()    #Will store the valid moveset at each turn to compare with the players 
    moveMade = False                 #Move detector flag
    
    loadImages()      #Load images before entering the game loop

    sqSelected = ()   #Click, empty initially (x, y)
    playerClicks = [] #[(x1, y1), (x2, y2)]
    
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:       #Mouse logic
                location = p.mouse.get_pos() 
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):        #Case where same tile is clicked twice
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:          #Two clicks are registered
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board )
                    print(move.getChessNotation())
                    if move in validMoves:          
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()                 #Reset clicks
                    playerClicks = []
                    
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:                  #Undo on z click
                    if len(gs.moveLog) > 0:         #Check if there's a move to undo
                        gs.undoMove()
                        moveMade = True
                        print("Undo")
        
        if moveMade :
            validMoves = gs.getValidMoves()
            movemade = not moveMade
    
        drawGameState(screen, gs, validMoves, sqSelected)
        
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def highlightSquares(screen, gs, validMoves, sqSelected):
    """Highlight square selected and moves for piece selected"""
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    """Draw the current game state."""
    drawBoard(screen)             # Draw squares
    highlightSquares(screen, gs, validMoves, sqSelected) # Draw highlights
    drawPieces(screen, gs.board)  # Draw pieces

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


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
