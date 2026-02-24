"""
Will store game state.
Will display valid moves. 
Will keep a move log.
"""

class GameState:
    """
    Manages the current state of a chess game, handles move logic, and validates rules.
    """
    def __init__(self):
        # The board is an 8x8 2D list. Each element has 2 characters:
        # 1st char: Color ('w' or 'b')
        # 2nd char: Piece type ('P', 'R', 'N', 'B', 'Q', 'K')
        # "--": Empty square
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()  # Coordinates of the square where an en passant capture is possible
        
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.enPassantPossibleLog = [self.enPassantPossible]

    def makeMove(self, move):
        """
        Executes a move on the board (standard moves, en passant, promotion, castling).
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        
        # Track King location for check validation
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Handle Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChoice

        # Handle En Passant capture
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"
        
        # Update en passant possibilities
        self.enPassantPossibleLog.append(self.enPassantPossible)
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Execute Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # Kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else: # Queenside
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # Update castling rights and logs
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        
    def undoMove(self):
        """
        Reverts the last move made.
        """
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            
            # Revert King location
            if lastMove.pieceMoved == 'wK':
                self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == 'bK':
                self.blackKingLocation = (lastMove.startRow, lastMove.startCol)
            
            # Undo En Passant
            if lastMove.isEnPassantMove:
                self.board[lastMove.endRow][lastMove.endCol] = "--"
                self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
            
            self.enPassantPossible = self.enPassantPossibleLog.pop()
            
            # Undo Castle Rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # Undo Castle piece movements
            if lastMove.isCastleMove:
                if lastMove.endCol - lastMove.startCol == 2: # Kingside
                    self.board[lastMove.endRow][lastMove.endCol+1] = self.board[lastMove.endRow][lastMove.endCol-1]
                    self.board[lastMove.endRow][lastMove.endCol-1] = '--'
                else: # Queenside
                    self.board[lastMove.endRow][lastMove.endCol-2] = self.board[lastMove.endRow][lastMove.endCol+1]
                    self.board[lastMove.endRow][lastMove.endCol+1] = '--'

            self.checkMate = False
            self.staleMate = False
    
    def updateCastleRights(self, move):
        """
        Updates castling rights based on Rook or King movements.
        """
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.bks = False
          
    def getValidMoves(self):
        """
        Returns all moves that do not result in the King being in check.
        """
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        
        # 1. Generate all possible moves
        moves = self.getAllPossibleMoves()
        
        # Add Castle moves
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
            
        # 2. Filter out moves that lead to check
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove # Switch to validate current player's King
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove # Switch back
            self.undoMove()
        
        # Check for Checkmate or Stalemate
        if not moves:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
            
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves
    
    def inCheck(self):
        """
        Returns True if the current player is in check.
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        """
        Determines if a square is being attacked by the opponent.
        """
        self.whiteToMove = not self.whiteToMove # Switch to opponent
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    def getAllPossibleMoves(self):
        """
        Generates all moves without filtering for King safety.
        """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves
        
    def scoreBoard(self):
        """
        Calculates the material score of the board. Positive favors White, negative favors Black.
        """
        pieceValues = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
        score = 0
        for row in self.board:
            for square in row:
                if square[0] == 'w':
                    score += pieceValues[square[1]]
                elif square[0] == 'b':
                    score -= pieceValues[square[1]]
        return score
    
    def getPawnMoves(self, r, c, moves):
        """
        Handles pawn movement, diagonal captures, and en passant.
        """
        if self.whiteToMove:
            if self.board[r-1][c] == "--": # 1 square advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # 2 square advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: # Left capture
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))
            if c+1 <= 7: # Right capture
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnPassantMove=True))

        else: # Black pawn moves
            if self.board[r+1][c] == "--": # 1 square advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": # 2 square advance
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0: # Left capture
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnPassantMove=True))
            if c+1 <= 7: # Right capture
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        """
        Sliding moves for Rooks.
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off board
                    break

    def getKnightMoves(self, r, c, moves):
        """
        Returns all pseudo-legal moves for the Knight.
        """
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][endCol][0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        """
        Sliding moves for Bishops along diagonals.
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow, endCol = r + d[0] * i, c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        """
        Returns all pseudo-legal moves for the Queen (combines Rook and Bishop logic).
        """
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """
        Returns all pseudo-legal moves for the King.
        """
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in kingMoves:
            endRow, endCol = r + m[0], c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][endCol][0] != allyColor:
                     moves.append(Move((r, c), (endRow, endCol), self.board))
    
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return # Can't castle in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)
        
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    
class CastleRights:
    """
    Stores the state of castling rights for both players.
    """
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
        
class Move:
    """
    Represents a single move on the chess board including utility mappings for chess notation.
    """
    # Map chess notation to indices
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove=False, promotionChoice='Q'):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.promotionChoice = promotionChoice
        
        # Detect special move types
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or \
                               (self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        self.isCastleMove = isCastleMove

        # Unique ID for move comparison
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
            
    def getChessNotation(self):
        """
        Converts move coordinates to chess algebraic notation (e.g., e2e4).
        """
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    
