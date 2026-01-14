
import sys
sys.path.append('C:\\Users\\masud\\Desktop\\Me')
from Chess import ChessEngine

def test_en_passant():
    print("Initializing Board...")
    gs = ChessEngine.GameState()
    
    # Setup En Passant Scenario
    # 1. e4 c6
    # 2. e5 d5
    # 3. exd6 (En Passant)
    
    moves_to_make = [
        ((6, 4), (4, 4)), # e2 -> e4
        ((1, 2), (2, 2)), # c7 -> c6
        ((4, 4), (3, 4)), # e4 -> e5
        ((1, 3), (3, 3))  # d7 -> d5 (Double Step)
    ]
    
    print("Executing Setup Moves:")
    for start, end in moves_to_make:
        move = ChessEngine.Move(start, end, gs.board)
        gs.makeMove(move)
        print(f"Moved: {move.getChessNotation()}")
        
    # Verify State before En Passant
    print(f"\nEn Passant Possible Square: {gs.enPassantPossible}")
    expected_ep = (2, 3) # d6 is (2, 3)
    if gs.enPassantPossible == expected_ep:
        print("PASS: En Passant square is correctly set to d6 (2, 3)")
    else:
        print(f"FAIL: En Passant square is {gs.enPassantPossible}, expected {expected_ep}")
        
    # Attempt En Passant Capture
    # White Pawn at e5 (3, 4) captures d6 (2, 3)
    ep_move = ChessEngine.Move((3, 4), (2, 3), gs.board, isEnPassantMove=True)
    
    print("\nExecuting En Passant Capture (e5xd6)...")
    gs.makeMove(ep_move)
    
    # Verify Board State
    # 1. White Pawn should be at d6
    # 2. Black Pawn at d5 should be GONE
    
    piece_at_d6 = gs.board[2][3]
    piece_at_d5 = gs.board[3][3] # The captured pawn location
    
    print(f"Piece at d6 (Destination): {piece_at_d6}")
    print(f"Piece at d5 (Captured Sq): {piece_at_d5}")
    
    if piece_at_d6 == 'wP' and piece_at_d5 == '--':
        print("PASS: En Passant capture successful. Enemy pawn removed.")
    else:
        print("FAIL: Board state incorrect after capture.")

    # Undo
    print("\nExecuting Undo...")
    gs.undoMove()
    
    piece_at_d6_undo = gs.board[2][3]
    piece_at_d5_undo = gs.board[3][3]
    
    print(f"Piece at d6: {piece_at_d6_undo}")
    print(f"Piece at d5: {piece_at_d5_undo}")
    
    if piece_at_d6_undo == '--' and piece_at_d5_undo == 'bP':
         print("PASS: Undo successful. Pawn restored.")
    else:
         print("FAIL: Undo failed.")

if __name__ == "__main__":
    test_en_passant()
