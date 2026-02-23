"""Main driver file for displaying the game state."""

import pygame as p
import sys
import os
sys.path.append('C:\\Users\\masud\\Desktop\\Me')  # Explicitly adds the directory for module lookups
from Chess import ChessEngine

# Constants and Configuration
BOARD_SIZE = 512
MOVE_LOG_WIDTH = 250
BOARD_PADDING = 24
WIDTH = BOARD_SIZE + BOARD_PADDING * 3 + MOVE_LOG_WIDTH
HEIGHT = BOARD_SIZE + BOARD_PADDING * 2
DIMENSION = 8
SQ_SIZE = BOARD_SIZE // DIMENSION
MAX_FPS = 30

# Assets cache
IMAGES = {}
SOUNDS = {}
MEDIA = [] # List of loaded media images

# Retro Color Palette
COLORS = {
    "bg": (230, 218, 206),        # #e6dace
    "panel": (253, 251, 247),     # #fdfbf7
    "border": (234, 221, 207),    # #eaddcf
    "terra": (193, 107, 70),      # #c16b46
    "dark": (74, 59, 50),         # #4a3b32
    "brown": (139, 94, 60),       # #8b5e3c
    "cream": (243, 234, 218),     # #f3eada
    "shadow": (203, 188, 168)     # #cbbca8
}
# Alias duplicate colors
COLORS["square_light"] = COLORS["cream"]
COLORS["square_dark"] = COLORS["terra"]

def loadSounds():
    """
    Loads audio assets into the cache safely. Missing files will be logged but won't crash the game.
    """
    sound_files = {
        "move": "move.mp3",
        "capture": "capture.mp3",
        "check": "check.mp3",
        "error": "error.mp3", # User will download this later
        "in_check_error": "youAreInCheck.mp3",
        "click": "click.mp3",
        "deselect": "deselect.mp3",
        "reset": "reset.mp3",
        "select": "select.mp3"
    }
    
    for key, filename in sound_files.items():
        try:
            SOUNDS[key] = p.mixer.Sound(f"Chess/sounds/{filename}")
        except Exception as e:
            print(f"Audio loading warning: Missing {filename}")

def loadImages():
    """
    Loads piece images, icons, and applies scaling for consistent UI layout.
    """
    # Load and scale chess pieces
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        image_path = f"Chess/images/{piece}.png"
        img = p.image.load(image_path).convert_alpha()
        # Scale to 85% of square size for a comfortable padding look
        IMAGES[piece] = p.transform.smoothscale(img, (int(SQ_SIZE * 0.85), int(SQ_SIZE * 0.85)))
        
    # Load and scale icons
    icon_map = {
        "undo": "noun-arrow-left-1507912.png",
        "redo": "noun-arrow-right-1507911.png",
        "reset": "noun-reset-1507869.png",
        "sound_on": "noun-speaker-1507885.png",
        "sound_off": "noun-mute-1507856.png"
    }
    
    icon_size = 20 # Standard size for button icons
    for key, filename in icon_map.items():
        try:
            img = p.image.load(f"Chess/images/icon-library/{filename}").convert_alpha()
            IMAGES[key] = p.transform.smoothscale(img, (icon_size, icon_size))
        except Exception as e:
            print(f"Icon loading warning: {e}")
            
    # Load Media Window Images
    media_dir = "Chess/images/media"
    if os.path.exists(media_dir):
        for filename in os.listdir(media_dir):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                try:
                    img = p.image.load(os.path.join(media_dir, filename)).convert_alpha()
                    # Scale to fit horizontally in the sidebar (250 width - padding)
                    target_width = MOVE_LOG_WIDTH - 20
                    ratio = target_width / img.get_width()
                    target_height = int(img.get_height() * ratio)
                    
                    # Cap height to prevent it from busting the layout
                    if target_height > 150:
                        target_height = 150
                        ratio = target_height / img.get_height()
                        target_width = int(img.get_width() * ratio)
                        
                    scaled_img = p.transform.smoothscale(img, (target_width, target_height))
                    MEDIA.append(scaled_img)
                except Exception as e:
                    print(f"Media loading warning: {e}")



def main():
    """
    Main entry point: initializes Pygame, loads assets, and handles the game loop.
    """
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Retro Chess - Tactical Interface")
    clock = p.time.Clock()
    
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag for when a move is made to recalculate valid moves
    
    loadImages()
    loadSounds()

    sqSelected = ()   # Last square selected by user (row, col)
    playerClicks = [] # Track player clicks (start and end squares)
    
    undone_moves = []
    sound_enabled = True
    current_message = "White to Move"
    message_timer = 0 # To handle transient messages
    
    # Control Bar Layout Constants (Single Row, Bottom)
    control_panel_height_layout = 65
    btn_start_x = BOARD_SIZE + BOARD_PADDING * 2 + 15
    # Bottom of control panel aligns with bottom of board frame (-12 top, +12 padding) -> BOARD_PADDING + BOARD_SIZE + 12
    control_panel_y = (BOARD_PADDING + BOARD_SIZE + 12) - control_panel_height_layout
    btn_start_y = control_panel_y + 15
    btn_gap = 12
    btn_width = (MOVE_LOG_WIDTH - 30 - (3 * btn_gap)) // 4
    btn_height = 35

    buttons = {
        "undo": p.Rect(btn_start_x, btn_start_y, btn_width, btn_height),
        "redo": p.Rect(btn_start_x + btn_width + btn_gap, btn_start_y, btn_width, btn_height),
        "reset": p.Rect(btn_start_x + 2 * (btn_width + btn_gap), btn_start_y, btn_width, btn_height),
        "sound": p.Rect(btn_start_x + 3 * (btn_width + btn_gap), btn_start_y, btn_width, btn_height)
    }
    
    
    # Helper for safe sound playback
    def play_sound(sound_key):
        if sound_enabled and sound_key in SOUNDS:
            SOUNDS[sound_key].play()

    running = True
    while running:
        board_rect = p.Rect(BOARD_PADDING, BOARD_PADDING, BOARD_SIZE, BOARD_SIZE)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # Mouse click handling
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                
                # Check control buttons first
                for action, rect in buttons.items():
                    if rect.collidepoint(location):
                        if action == "undo":
                            if len(gs.moveLog) > 0:
                                undone_moves.append(gs.moveLog[-1])
                                gs.undoMove()
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                                play_sound("move")
                        elif action == "redo":
                            if len(undone_moves) > 0:
                                move = undone_moves.pop()
                                gs.makeMove(move)
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                                # Optional visual/sound feedback
                                if gs.inCheck(): 
                                    play_sound("check")
                                    current_message = "Check!"
                                    message_timer = p.time.get_ticks()
                                elif move.pieceCaptured != '--': 
                                    play_sound("capture")
                                    current_message = "White to Move" if gs.whiteToMove else "Black to Move"
                                else: 
                                    play_sound("move")
                                    current_message = "White to Move" if gs.whiteToMove else "Black to Move"
                        elif action == "reset":
                            gs = ChessEngine.GameState()
                            validMoves = gs.getValidMoves()
                            sqSelected = ()
                            playerClicks = []
                            moveMade = False
                            undone_moves.clear()
                            play_sound("reset")
                            current_message = "White to Move"
                        elif action == "sound":
                            sound_enabled = not sound_enabled
                            play_sound("click")
                            
            # Reset transient message timer on input
            if e.type in (p.MOUSEBUTTONDOWN, p.KEYDOWN):
                message_timer = p.time.get_ticks()
                
                # Board Clicks
                if e.type == p.MOUSEBUTTONDOWN and board_rect.collidepoint(location):
                    col = (location[0] - BOARD_PADDING) // SQ_SIZE
                    row = (location[1] - BOARD_PADDING) // SQ_SIZE
                    
                    if not gs.whiteToMove:
                        col = 7 - col
                        row = 7 - row
                    
                    if sqSelected == (row, col): # Deselect if clicking the same square
                        sqSelected = ()
                        playerClicks = []
                        play_sound("deselect")
                    else:
                        if len(playerClicks) == 0: # First click
                            # Must verify they are picking up a valid piece of their own color
                            if gs.board[row][col] != "--" and gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)
                                play_sound("select")
                            else:
                                if gs.inCheck(): 
                                    play_sound("in_check_error")
                                    current_message = "Invalid: You are in Check"
                                else: 
                                    play_sound("error")
                                    current_message = "Invalid: Not your piece"
                                
                        else: # Second click confirmed
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    # Intercept Pawn Promotion to ask user for choice
                                    if validMoves[i].isPawnPromotion:
                                        piece_choice = showPromotionDialog(screen, gs.whiteToMove)
                                        validMoves[i].promotionChoice = piece_choice
                                        
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    undone_moves.clear() # Clear redo stack on new move
                                    
                                    
                                    # Play appropriate sound based on game state
                                    if gs.inCheck(): 
                                        play_sound("check")
                                        current_message = "Check!"
                                    elif validMoves[i].pieceCaptured != '--': 
                                        play_sound("capture")
                                        current_message = "White to Move" if gs.whiteToMove else "Black to Move"
                                    else: 
                                        play_sound("move")
                                        current_message = "White to Move" if gs.whiteToMove else "Black to Move"
                                        
                                    sqSelected = ()
                                    playerClicks = []
                                    break
                                    
                            if not moveMade:
                                # Not a valid move. Did they click their own piece to re-select?
                                if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
                                    sqSelected = (row, col)
                                    playerClicks = [sqSelected]
                                    play_sound("select")
                                else:
                                    # Truly invalid move (empty square or enemy piece)
                                    sqSelected = ()
                                    playerClicks = []
                                    if gs.inCheck(): 
                                        play_sound("in_check_error")
                                        current_message = "Illegal: Must escape Check"
                                    else: 
                                        play_sound("error")
                                        current_message = "Illegal: Invalid destination"
            
            # Keyboard handling (Z for Undo)
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if len(gs.moveLog) > 0:
                        undone_moves.append(gs.moveLog[-1])
                        gs.undoMove()
                        moveMade = True
                        sqSelected = ()
                        playerClicks = []
                        current_message = "Move Undone"
                        message_timer = p.time.get_ticks()
        
        # Recalculate move tree if a move was executed
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
    
        # Handle transient messages
        if p.time.get_ticks() - message_timer > 1500: # 1.5 seconds
            if gs.checkMate:
                current_message = "Checkmate! " + ('Black' if gs.whiteToMove else 'White') + " Wins"
            elif gs.staleMate:
                current_message = "Stalemate"
            else:
                current_message = "White to Move" if gs.whiteToMove else "Black to Move"
        
        # Rendering
        drawGameState(screen, gs, validMoves, sqSelected, buttons, sound_enabled, current_message)
        
        # Optional: Full screen text overlay for end game
        if gs.checkMate:
            drawStatusText(screen, 'Checkmate! ' + ('Black' if gs.whiteToMove else 'White') + ' Wins')
        elif gs.staleMate:
            drawStatusText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()



def drawTactilePanel(screen, rect, border_color, bg_color, shadow_offset=4, border_radius=8):
    """Draws a panel with a tactile shadow effect."""
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    p.draw.rect(screen, COLORS["shadow"], shadow_rect, border_radius=border_radius)
    p.draw.rect(screen, bg_color, rect, border_radius=border_radius)
    p.draw.rect(screen, border_color, rect, 2, border_radius=border_radius)

def drawControls(screen, buttons, sound_enabled):
    """Renders the bottom control bar with tactile buttons and icons."""
    control_panel_height = 65
    panel_y = (BOARD_PADDING + BOARD_SIZE + 12) - control_panel_height
    panel_rect = p.Rect(BOARD_SIZE + (BOARD_PADDING * 2), panel_y, MOVE_LOG_WIDTH, control_panel_height)
    drawTactilePanel(screen, panel_rect, COLORS["border"], COLORS["panel"])
    
    for action, rect in buttons.items():
        # Action button visuals (pushable keys)
        drawTactilePanel(screen, rect, COLORS["shadow"], COLORS["square_light"], shadow_offset=2, border_radius=6)
        
        # Determine which icon to display
        if action == "sound":
            icon_key = "sound_on" if sound_enabled else "sound_off"
        else:
            icon_key = action
            
        # Draw the icon if it loaded successfully
        if icon_key in IMAGES:
            icon = IMAGES[icon_key]
            # Custom coloration for these specific icons (turning them dark brown)
            # This ensures they fit the palette regardless of their original PNG color
            color_surface = p.Surface(icon.get_size()).convert_alpha()
            color_surface.fill(COLORS["dark"])
            icon_copy = icon.copy()
            icon_copy.blit(color_surface, (0,0), special_flags=p.BLEND_RGBA_MULT)
            
            screen.blit(icon_copy, (rect.centerx - icon.get_width() // 2, rect.centery - icon.get_height() // 2))

def drawMoveLog(screen, gs):
    """
    Renders the right sidebar containing the move log in a two-column format.
    """
    control_panel_height = 65
    gap_between_panels = 15
    
    # We will need space for Status (e.g. 50px) and Media (e.g. 150px) below this
    status_height = 50
    media_height = 150
    
    # Calculate panel bounds
    panel_y = BOARD_PADDING - 12
    # The bottom of the entirity of right-side panels
    right_side_bottom = (BOARD_PADDING + BOARD_SIZE + 12)
    
    # Calculate how much space is left for the Move Log
    # Total space = (bottom - top) - control_panel - gaps - status - media
    panel_height = (right_side_bottom - panel_y) - control_panel_height - status_height - media_height - (3 * gap_between_panels)
    
    panel_rect = p.Rect(BOARD_SIZE + (BOARD_PADDING * 2), panel_y, MOVE_LOG_WIDTH, panel_height)
    drawTactilePanel(screen, panel_rect, COLORS["border"], COLORS["panel"])
    
    # Render Sidebar Header & Column Titles
    font = p.font.SysFont("Courier New", 16, True)
    text = font.render("MOVES", True, COLORS["dark"])
    screen.blit(text, (panel_rect.centerx - text.get_width() // 2, panel_rect.y + 12))
    
    # Column Subheaders
    font_sub = p.font.SysFont("Courier New", 12, True)
    white_header = font_sub.render("White", True, COLORS["brown"])
    black_header = font_sub.render("Black", True, COLORS["brown"])
    
    # Column X coordinates
    num_x = panel_rect.x + 15
    white_x = panel_rect.x + 60
    black_x = panel_rect.x + 150
    
    screen.blit(white_header, (white_x, panel_rect.y + 40))
    screen.blit(black_header, (black_x, panel_rect.y + 40))
    
    # Draw a subtle separator line
    p.draw.line(screen, COLORS["shadow"], (panel_rect.x + 10, panel_rect.y + 58), (panel_rect.x + MOVE_LOG_WIDTH - 10, panel_rect.y + 58), 1)

    # Process move log for two-column display
    moveLog = gs.moveLog
    moveRows = []
    for i in range(0, len(moveLog), 2):
        turn_string = str(i // 2 + 1) + "."
        white_string = str(moveLog[i].getChessNotation())
        black_string = str(moveLog[i + 1].getChessNotation()) if i + 1 < len(moveLog) else ""
        moveRows.append((turn_string, white_string, black_string))
        
    font_moves = p.font.SysFont("Courier New", 14)
    line_spacing = 22
    start_y = panel_rect.y + 65
    
    # Auto-scrolling logic
    max_visible_float = (panel_rect.height - 70) / line_spacing
    max_visible = max(1, int(max_visible_float))
    start_idx = max(0, len(moveRows) - max_visible)
    
    for i in range(start_idx, len(moveRows)):
        row_idx = i - start_idx
        y_pos = start_y + (row_idx * line_spacing)
        
        # Prevent drawing outside the bottom of the panel
        if y_pos + line_spacing > panel_rect.bottom:
            break
        
        turn_num, white_mv, black_mv = moveRows[i]
        
        # Turn Number
        text_num = font_moves.render(turn_num, True, COLORS["brown"])
        screen.blit(text_num, (num_x, y_pos))
        
        # White Move
        text_white = font_moves.render(white_mv, True, COLORS["dark"])
        screen.blit(text_white, (white_x, y_pos))
        
        # Black Move
        if black_mv != "":
            text_black = font_moves.render(black_mv, True, COLORS["dark"])
            screen.blit(text_black, (black_x, y_pos))

def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Visually highlights the selected square and all valid moves for that piece.
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            visual_r = r if gs.whiteToMove else 7 - r
            visual_c = c if gs.whiteToMove else 7 - c
            
            # Highlight selection square
            s = p.Surface((SQ_SIZE - 4, SQ_SIZE - 4))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (BOARD_PADDING + visual_c * SQ_SIZE + 2, BOARD_PADDING + visual_r * SQ_SIZE + 2))
            
            # Highlight valid move target squares
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    move_visual_r = move.endRow if gs.whiteToMove else 7 - move.endRow
                    move_visual_c = move.endCol if gs.whiteToMove else 7 - move.endCol
                    screen.blit(s, (BOARD_PADDING + move_visual_c * SQ_SIZE + 2, BOARD_PADDING + move_visual_r * SQ_SIZE + 2))

def drawGameState(screen, gs, validMoves, sqSelected, buttons, sound_enabled, current_message):
    """Draw the current game state."""
    screen.fill(COLORS["bg"])
    drawControls(screen, buttons, sound_enabled)
    drawMoveLog(screen, gs)
    drawStatusDialog(screen, current_message)
    drawMediaWindow(screen)
    
    drawBoard(screen, sqSelected, gs.whiteToMove)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board, sqSelected, gs.whiteToMove)
    
def drawStatusDialog(screen, current_message):
    """
    Renders the quick-feedback status dialog with a CRT monitor aesthetic.
    """
    control_panel_height = 65
    gap_between_panels = 15
    status_height = 50
    
    # The bottom of the entirity of right-side panels
    right_side_bottom = (BOARD_PADDING + BOARD_SIZE + 12)
    
    # Calculate Y by going up from Control Panel
    control_panel_y = right_side_bottom - control_panel_height
    status_y = control_panel_y - gap_between_panels - status_height
    
    panel_rect = p.Rect(BOARD_SIZE + (BOARD_PADDING * 2), status_y, MOVE_LOG_WIDTH, status_height)
    
    # Outer Bezel (Tactile panel)
    drawTactilePanel(screen, panel_rect, COLORS["border"], COLORS["panel"])
    
    # Inner CRT Screen
    crt_rect = panel_rect.inflate(-12, -12)
    p.draw.rect(screen, COLORS["bg"], crt_rect, border_radius=4) # Earthy background
    
    # Inset Shadow for CRT Screen
    p.draw.rect(screen, COLORS["shadow"], crt_rect, width=2, border_radius=4)
    p.draw.rect(screen, COLORS["dark"], crt_rect.inflate(-4, -4), width=1, border_radius=3)
    
    font = p.font.SysFont("Courier New", 14, True)
    
    # Phosphor Colors
    text_color = COLORS["dark"] # Dark
    if "Invalid" in current_message or "Illegal" in current_message:
        text_color = COLORS["terra"] # Red/Orange for errors
    elif "Checkmate" in current_message or "Check!" in current_message:
        text_color = COLORS["brown"] # Amber/Brown
        
    text = font.render(current_message, True, text_color)
    screen.blit(text, (crt_rect.centerx - text.get_width() // 2, crt_rect.centery - text.get_height() // 2))
    
    # CRT Scanlines
    scanline_surf = p.Surface((crt_rect.width, crt_rect.height), p.SRCALPHA)
    for y in range(0, crt_rect.height, 2):
        p.draw.line(scanline_surf, (0, 0, 0, 80), (0, y), (crt_rect.width, y))
    screen.blit(scanline_surf, crt_rect.topleft)

def drawMediaWindow(screen):
    """
    Renders the bottom-most display panel above the control bar for images/gifs.
    Uses depression and beveling effects to embed the images inside the panel.
    """
    control_panel_height = 65
    gap_between_panels = 15
    status_height = 50
    media_height = 150
    
    # The bottom of the entirity of right-side panels
    right_side_bottom = (BOARD_PADDING + BOARD_SIZE + 12)
    
    # Calculate Y
    control_panel_y = right_side_bottom - control_panel_height
    status_y = control_panel_y - gap_between_panels - status_height
    media_y = status_y - gap_between_panels - media_height
    
    panel_rect = p.Rect(BOARD_SIZE + (BOARD_PADDING * 2), media_y, MOVE_LOG_WIDTH, media_height)
    
    # Draw depressed panel background
    p.draw.rect(screen, COLORS["cream"], panel_rect.move(1, 1), border_radius=8) # Highlight
    p.draw.rect(screen, COLORS["shadow"], panel_rect.move(-1, -1), border_radius=8) # Shadow
    p.draw.rect(screen, COLORS["bg"], panel_rect, border_radius=8) # Deep bg
    
    # Render Media if available
    if len(MEDIA) > 0:
        # Loop through images every 750ms
        current_time = p.time.get_ticks()
        frame_duration = 750 # (ms) 
        frame_idx = (current_time // frame_duration) % len(MEDIA)
        img = MEDIA[frame_idx]
        
        img_rect = img.get_rect(center=panel_rect.center)
        screen.blit(img, img_rect)
        
        # Round the images and bevel them so they look inside the panel
        # Mask the square corners of the image with the background color (thick border)
        p.draw.rect(screen, COLORS["bg"], img_rect.inflate(8, 8), width=8, border_radius=12)
        # Inner shadow to simulate depression of the image itself
        p.draw.rect(screen, COLORS["shadow"], img_rect.inflate(2, 2), width=3, border_radius=8)
        p.draw.rect(screen, COLORS["dark"], img_rect.inflate(-2, -2), width=1, border_radius=8) # extra depth
    else:
        # Placeholder text if no media found
        font = p.font.SysFont("Courier New", 12)
        text = font.render("No Media Art Found", True, COLORS["shadow"])
        screen.blit(text, (panel_rect.centerx - text.get_width() // 2, panel_rect.centery - text.get_height() // 2))

def drawBoard(screen, sqSelected, whiteToMove):
    """Draw the chessboard with retro colors and tactile tiles."""
    # Draw the board's wooden/brown outer framing
    board_frame = p.Rect(BOARD_PADDING - 12, BOARD_PADDING - 12, BOARD_SIZE + 24, BOARD_SIZE + 24)
    drawTactilePanel(screen, board_frame, COLORS["dark"], COLORS["brown"], shadow_offset=6)

    colors = [COLORS["square_light"], COLORS["square_dark"]]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            
            visual_r = r if whiteToMove else 7 - r
            visual_c = c if whiteToMove else 7 - c
            
            # 3D Tile effect
            tile_rect = p.Rect(BOARD_PADDING + visual_c * SQ_SIZE + 2, BOARD_PADDING + visual_r * SQ_SIZE + 2, SQ_SIZE - 4, SQ_SIZE - 4)
            is_selected = sqSelected == (r, c)
            
            if is_selected:
                # Depressed tile: push the tile down, obscuring the shadow
                tile_rect.move_ip(2, 2)
                p.draw.rect(screen, color, tile_rect, border_radius=4)
            else:
                # Normal raised tile: draw shadow then tile
                shadow_rect = tile_rect.move(2, 2)
                p.draw.rect(screen, COLORS["dark"], shadow_rect, border_radius=4)
                p.draw.rect(screen, color, tile_rect, border_radius=4)
            
            # Coordinates
            font = p.font.SysFont("Courier New", 10, True)
            if visual_c == 0: # Ranks
                lbl = font.render(str(8-r), True, colors[1] if (r+c)%2==0 else colors[0])
                screen.blit(lbl, (BOARD_PADDING + 4, BOARD_PADDING + visual_r * SQ_SIZE + 4))
            if visual_r == 7: # Files
                lbl = font.render(chr(ord('a') + c), True, colors[1] if (r+c)%2==0 else colors[0])
                screen.blit(lbl, (BOARD_PADDING + (visual_c+1)*SQ_SIZE - 12, BOARD_PADDING + BOARD_SIZE - 14))

def drawPieces(screen, board, sqSelected, whiteToMove):
    """
    Renders pieces on the board with centered square positioning and depth awareness.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                img = IMAGES[piece]
                offset = (SQ_SIZE - img.get_width()) // 2
                
                visual_r = r if whiteToMove else 7 - r
                visual_c = c if whiteToMove else 7 - c
                
                # Shift piece down if the tile it's sitting on is depressed
                is_selected = sqSelected == (r, c)
                y_offset = offset + (2 if is_selected else 0)
                x_offset = offset + (2 if is_selected else 0)
                
                screen.blit(img, p.Rect(BOARD_PADDING + visual_c * SQ_SIZE + x_offset, BOARD_PADDING + visual_r * SQ_SIZE + y_offset, SQ_SIZE, SQ_SIZE))

def drawStatusText(screen, text):
    """
    Renders an overlay with game status text (Checkmate, Stalemate).
    """
    font = p.font.SysFont("Courier New", 32, True)
    text_surf = font.render(text, True, COLORS["dark"])
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Semi-transparent overlay background
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((255, 255, 255))
    screen.blit(overlay, (0, 0))
    
    screen.blit(text_surf, text_rect)

def showPromotionDialog(screen, isWhite):
    """
    Halts the main loop to render a tactile popup dialog asking the user which piece
    they want to promote their pawn to. Returns the character 'Q', 'R', 'B', or 'N'.
    """
    dialog_width = 300
    dialog_height = 120
    dialog_rect = p.Rect((WIDTH - dialog_width) // 2, (HEIGHT - dialog_height) // 2, dialog_width, dialog_height)
    
    # Needs to wait for a choice
    choosing = True
    color_prefix = 'w' if isWhite else 'b'
    options = ['Q', 'R', 'B', 'N']
    
    # Calculate button zones
    btn_width = 50
    btn_height = 50
    gap = 15
    start_x = dialog_rect.x + (dialog_width - (4 * btn_width + 3 * gap)) // 2
    y_pos = dialog_rect.y + 50
    
    buttons = []
    for i, opt in enumerate(options):
        bx = start_x + i * (btn_width + gap)
        buttons.append((p.Rect(bx, y_pos, btn_width, btn_height), opt))

    clock = p.time.Clock()
    
    while choosing:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                loc = p.mouse.get_pos()
                for rect, opt in buttons:
                    if rect.collidepoint(loc):
                        return opt # Choice made
                        
        # Draw overlay to dim the game
        overlay = p.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw Dialog
        drawTactilePanel(screen, dialog_rect, COLORS["border"], COLORS["cream"], border_radius=12)
        
        font = p.font.SysFont("Courier New", 16, True)
        title = font.render("Choose Promotion:", True, COLORS["dark"])
        screen.blit(title, (dialog_rect.centerx - title.get_width() // 2, dialog_rect.y + 15))
        
        # Draw Option Buttons
        for rect, opt in buttons:
            drawTactilePanel(screen, rect, COLORS["shadow"], COLORS["square_light"], shadow_offset=2, border_radius=8)
            piece_img = IMAGES[color_prefix + opt]
            
            # Center the piece in the button
            img_x = rect.x + (btn_width - piece_img.get_width()) // 2
            img_y = rect.y + (btn_height - piece_img.get_height()) // 2
            screen.blit(piece_img, (img_x, img_y))
            
        p.display.flip()
        clock.tick(MAX_FPS)
        
    return 'Q' # Fallback

if __name__ == "__main__":
    main()

