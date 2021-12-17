import copy


class Piece:

    def __init__(self, color: bool, pieceType: str):
        self._color = color
        self._pieceType = pieceType

    def __repr__(self):
        if self._color:
            return self._pieceType.upper()
        else:
            return self._pieceType

    def getColor(self):
        return self._color

    def getType(self):
        return self._pieceType


class Board:
    # startingFenString = "2Q2bnr/4p1pq/5pkr/7p/7P/4P3/PPPP1PP1/RNB1KBNR"
    startingFenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self):
        self._grid: list = [[None for _ in range(8)] for _ in range(8)]

    def popCell(self, row: int, col: int) -> Piece:
        temp: Piece = self._grid[row][col]
        self._grid[row][col] = None
        return temp

    def editCell(self, row, col, piece):
        self._grid[row][col] = piece

    def initializeBoard(self):
        fillPointer: int = 0
        selectedRow: int = 0
        for ch in self.startingFenString:
            if ch != "/":
                if ch.isalpha():
                    if ch.isupper():
                        newPiece = Piece(True, ch.lower())
                    else:
                        newPiece = Piece(False, ch)
                    self._grid[selectedRow][fillPointer] = newPiece
                    fillPointer += 1
                elif ch.isnumeric():
                    fillPointer += int(ch)
            else:
                fillPointer = 0
                selectedRow += 1

    def prettyPrint(self):
        print("  A B C D E F G H  ")
        rowCount = 8
        for row in self._grid:
            print(rowCount, end=" ")
            piece: Piece
            for piece in row:
                if piece is None:
                    print("0", end=" ")
                else:
                    if piece.getColor():
                        color = "\033[96m"
                    else:
                        color = "\033[92m"
                    print(f"{color}{piece}\033[0m", end=" ")
            print(str(rowCount))
            rowCount -= 1
        print("  A B C D E F G H  ")

    def getGrid(self):
        return self._grid


class MoveErrors(Exception):
    """Super Class for errors while processing the move"""


class AmbiguousMoveError(MoveErrors):
    """Error to indicate that there is more than one possible move that could get the piece in that position"""


class InvalidMoveError(MoveErrors):
    """Completely invalid move that has been inputted"""


class IncorrectMoveStringLengthError(MoveErrors):
    """When the move string has the wrong length"""


class Move:

    def __init__(self, oR, oC, tR, tC, pieceType):
        self._originRow = oR
        self._originCol = oC
        self._targetRow = tR
        self._targetCol = tC
        self._moveID = self._originRow * 512 + self._originCol * 64 + self._targetRow * 8 + self._targetCol
        self._pieceType = pieceType

    def getOriginRow(self):
        return self._originRow

    def getOriginCol(self):
        return self._originCol

    def getTargetRow(self):
        return self._targetRow

    def getTargetCol(self):
        return self._targetCol

    def __eq__(self, other):
        other: Move
        if self._moveID == other.getMoveID():
            return True
        else:
            return False

    def __repr__(self):
        originString = chr(self._originCol + 97) + str(8 - self._originRow)
        targetString = chr(self._targetCol + 97) + str(8 - self._targetRow)
        return f"{self._pieceType}{originString}{targetString}"

    def getMoveID(self):
        return self._moveID

    def getTargetRowAndCol(self):
        return self._targetRow, self._targetCol

    def getPieceType(self):
        return self._pieceType


class EnPassantMove(Move):

    def __init__(self, oR, oC, tR, tC, eR, eC, pieceType):
        super().__init__(oR, oC, tR, tC, pieceType)
        self.enemyRow = eR
        self.enemyCol = eC

    def getEnemyRow(self):
        return self.enemyRow

    def getEnemyCol(self):
        return self.enemyCol


class GameController:

    def __init__(self):
        self._board = Board()
        self._board.initializeBoard()
        self._activeColor = True
        self._promotionSquares = []
        self._whiteKingPos = (7, 4)
        self._tempWhiteKingPos = tuple()
        self._whiteCastleAvailability = [True, True]
        self._whiteCanCastleThisTurn = [False, False]
        self._blackKingPos = (0, 4)
        # self._blackKingPos = (2, 6)
        self._tempBlackKingPos = tuple()
        self._blackCastleAvailability = [True, True]
        self._blackCanCastleThisTurn = [False, False]
        self._moves = []
        self._attackedSquares = set()
        self._enPassantSquare = tuple()
        self._tempEnPassantSquare = tuple()

    # def turnIntoMove(self, moveString) -> Move:
    #     if len(moveString) == 3:
    #         pass  # IMPLEMENT LATER THIS IS HARD AS SHIT TO IMPLEMENT
    #     elif len(moveString) == 5:
    #         originCol = ord(moveString[1]) - 97
    #         originRow = 8 - int(moveString[2])
    #         targetCol = ord(moveString[3]) - 97
    #         targetRow = 8 - int(moveString[4])
    #         moveID = originRow * 512 + originCol * 64 + targetRow * 8 + targetCol
    #         return Move(originRow, originCol, targetRow, targetCol, moveID)

    def getActiveColor(self):
        return self._activeColor

    def setActiveColor(self, color):
        self._activeColor = color

    def getBoard(self):
        return self._board

    def getMoves(self):
        return self._moves

    def makeMove(self, move, customBoard=None):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        if isinstance(move, EnPassantMove):
            pawn = board.popCell(move.getOriginRow(), move.getOriginCol())
            board.editCell(move.getTargetRow(), move.getTargetCol(), pawn)
            board.popCell(move.getEnemyRow(), move.getEnemyCol())

        # elif isinstance(move, CastleMove):
        #     pass
        else:
            piece = board.popCell(move.getOriginRow(), move.getOriginCol())
            board.editCell(move.getTargetRow(), move.getTargetCol(), piece)
            if piece.getType() == "p":
                if customBoard is None:
                    if move.getTargetRow() - move.getOriginRow() == 2:
                        self._enPassantSquare = (move.getTargetRow(), move.getTargetCol(), False)
                    elif move.getTargetRow() - move.getOriginRow() == -2:
                        self._enPassantSquare = (move.getTargetRow(), move.getTargetCol(), True)
                else:
                    if move.getTargetRow() - move.getOriginRow() == 2:
                        self._tempEnPassantSquare = (move.getTargetRow(), move.getTargetCol(), False)
                    elif move.getTargetRow() - move.getOriginRow() == -2:
                        self._tempEnPassantSquare = (move.getTargetRow(), move.getTargetCol(), True)
            elif piece.getType() == "k":
                if customBoard is None:
                    if piece.getColor():
                        self._whiteKingPos = (move.getTargetRow(), move.getTargetCol())
                    else:
                        self._blackKingPos = (move.getTargetRow(), move.getTargetCol())
                else:
                    if piece.getColor():
                        self._tempWhiteKingPos = (move.getTargetRow(), move.getTargetCol())
                    else:
                        self._tempBlackKingPos = (move.getTargetRow(), move.getTargetCol())

    def processMove(self, moveString):
        finalizedMove = None
        finalizedMoves = []
        moveString = moveString.lower()
        if moveString == "0-0":
            if self._activeColor:
                canCastle = self._whiteCanCastleThisTurn
            else:
                canCastle = self._blackCanCastleThisTurn
            if canCastle[0]:
                # predefined values because there can be only one type of white king side castle.
                finalizedMoves.append(Move(7, 7, 7, 5, "r"))
                finalizedMoves.append(Move(7, 4, 7, 6, "k"))
            else:
                raise InvalidMoveError
        elif len(moveString) == 3:
            try:
                targetRow = 8 - int(moveString[2])
                targetCol = ord(moveString[1].lower()) - 97
                targetType = moveString[0]
            except ValueError:
                raise ValueError
            move: Move
            possibleMove = [move for move in self._moves if
                            move.getTargetRowAndCol() == (targetRow, targetCol) and move.getPieceType() == targetType]
            if len(possibleMove) == 1:
                finalizedMove = possibleMove[0]
            elif len(possibleMove) > 1:
                raise AmbiguousMoveError
            else:
                raise InvalidMoveError
        elif len(moveString) == 5:
            targetRow = 8 - int(moveString[4])
            targetCol = ord(moveString[3].lower()) - 97
            originRow = 8 - int(moveString[2])
            originCol = ord(moveString[1].lower()) - 97
            targetType = moveString[0]
            possibleMove = Move(originRow, originCol, targetRow, targetCol, targetType)
            if possibleMove in self._moves:
                finalizedMove = possibleMove
            else:
                raise InvalidMoveError
        else:
            raise IncorrectMoveStringLengthError
        if finalizedMove is not None:
            self.makeMove(finalizedMove)
        if len(finalizedMoves) != 0:
            for move in finalizedMoves:
                self.makeMove(move)

    def calculateMoves(self):
        self._whiteCanCastleThisTurn = [False, False]
        self._blackCanCastleThisTurn = [False, False]
        self._promotionSquares = []
        self._moves = []
        for rowNum, row in enumerate(self._board.getGrid()):
            for colNum, piece in enumerate(row):
                piece: Piece
                if piece is not None and piece.getColor() is self._activeColor:
                    if piece.getType() == "p":
                        self._moves += self.calculatePawnMoves(rowNum, colNum)
                    elif piece.getType() == "r":
                        self._moves += self.calculateRookMoves(rowNum, colNum)
                    elif piece.getType() == "b":
                        self._moves += self.calculateBishopMoves(rowNum, colNum)
                    elif piece.getType() == "n":
                        self._moves += self.calculateKnightMoves(rowNum, colNum)
                    elif piece.getType() == "q":
                        self._moves += self.calculateQueenMoves(rowNum, colNum)
                    elif piece.getType() == "k":
                        self._moves += self.calculateKingMoves(rowNum, colNum)

    def calculateSpecialMoves(self):
        # En Passant
        if self._enPassantSquare != ():
            if self._enPassantSquare[2] == self._activeColor:
                self._enPassantSquare = ()
            else:
                # for columns 2-8 check the left square
                if self._enPassantSquare[1] > 0:
                    leftPiece = self._board.getGrid()[self._enPassantSquare[0]][self._enPassantSquare[1] - 1]
                    leftPiece: Piece
                    if leftPiece is not None and leftPiece.getColor() is self._activeColor and leftPiece.getType() == "p":
                        if self._activeColor:
                            self._moves.append(EnPassantMove(self._enPassantSquare[0], self._enPassantSquare[1] - 1,
                                                             self._enPassantSquare[0] - 1, self._enPassantSquare[1],
                                                             self._enPassantSquare[0], self._enPassantSquare[1], "p"))
                        else:
                            self._moves.append(EnPassantMove(self._enPassantSquare[0], self._enPassantSquare[1] - 1,
                                                             self._enPassantSquare[0] + 1, self._enPassantSquare[1],
                                                             self._enPassantSquare[0], self._enPassantSquare[1], "p"
                                                             ))
                # for columns 1-7 check the right square
                if self._enPassantSquare[1] < 7:
                    rightPiece = self._board.getGrid()[self._enPassantSquare[0]][self._enPassantSquare[1] + 1]
                    rightPiece: Piece
                    if rightPiece is not None and rightPiece.getColor() is self._activeColor and rightPiece.getType() == "p":
                        if self._activeColor:
                            self._moves.append(EnPassantMove(self._enPassantSquare[0], self._enPassantSquare[1] + 1,
                                                             self._enPassantSquare[0] - 1, self._enPassantSquare[1],
                                                             self._enPassantSquare[0], self._enPassantSquare[1], "p"))
                        else:
                            self._moves.append(EnPassantMove(self._enPassantSquare[0], self._enPassantSquare[1] + 1,
                                                             self._enPassantSquare[0] + 1, self._enPassantSquare[1],
                                                             self._enPassantSquare[0], self._enPassantSquare[1], "p"))
        # Castling
        if self._activeColor:
            if self._whiteCastleAvailability[0] and not self.calculateValidMoves(
                    [Move(self._whiteKingPos[0], self._whiteKingPos[1], self._whiteKingPos[0], self._whiteKingPos[1],
                          "k")]):
                # white king side castle check
                kingSubMoves = []
                for i in range(1, 3):
                    if self._board.getGrid()[self._whiteKingPos[0]][self._whiteKingPos[1] + i] is None:
                        kingSubMoves.append(Move(self._whiteKingPos[0], self._whiteKingPos[1], self._whiteKingPos[0],
                                                 self._whiteKingPos[1] + i, "k"))
                    else:
                        break
                self.calculateValidMoves(kingSubMoves)
                if len(kingSubMoves) == 2:
                    self._whiteCanCastleThisTurn[0] = True
            if self._whiteCastleAvailability[1]:
                # white queen side castle check
                pass

    def calculatePawnMoves(self, row: int, col: int, customBoard=None, customPromoList=None):
        moves = []
        if customPromoList is None:
            promotionSquareList = self._promotionSquares
        else:
            promotionSquareList = customPromoList
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        if self._activeColor:
            if board.getGrid()[row - 1][col] is None:
                moves.append(Move(row, col, row - 1, col, "p"))
                if row == 1:
                    promotionSquareList.append((row - 1, col))
                if row == 6 and board.getGrid()[row - 2][col] is None:
                    moves.append(Move(row, col, row - 2, col, "p"))
                    # self._enPassantSquare = (row - 2, col, True)
            if col < 7:
                enemyPiece = board.getGrid()[row - 1][col + 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row - 1, col + 1, "p"))
                    if row == 1:
                        promotionSquareList.append((row - 1, col + 1))
            if col > 0:
                enemyPiece = board.getGrid()[row - 1][col - 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row - 1, col - 1, "p"))
                    if row == 1:
                        promotionSquareList.append((row - 1, col - 1))
        else:
            if board.getGrid()[row + 1][col] is None:
                moves.append(Move(row, col, row + 1, col, "p"))
                if row == 6:
                    promotionSquareList.append((row + 1, col))
                if row == 1 and board.getGrid()[row + 2][col] is None:
                    moves.append(Move(row, col, row + 2, col, "p"))
                    # self._enPassantSquare = (row + 2, col, False)
            if col < 7:
                enemyPiece = board.getGrid()[row + 1][col + 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row + 1, col + 1, "p"))
                    if row == 6:
                        promotionSquareList.append((row + 1, col + 1))
            if col > 0:
                enemyPiece = board.getGrid()[row + 1][col - 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row + 1, col - 1, "p"))
                    if row == 6:
                        promotionSquareList.append((row + 1, col - 1))
        return moves

    def calculateRookMoves(self, row: int, col: int, customBoard=None):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))  # up down right left
        return self.calculateRayMoves(row, col, directions, "r", customBoard)

    def calculateKnightMoves(self, row: int, col: int, customBoard=None):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        potentialSquares = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        for square in potentialSquares:
            targetRow = row + square[0]
            targetCol = col + square[1]
            if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                targetPiece = board.getGrid()[targetRow][targetCol]
                if targetPiece is None:
                    moves.append(Move(row, col, targetRow, targetCol, "n"))
                else:
                    targetPiece: Piece
                    if targetPiece.getColor() != self._activeColor:
                        moves.append(Move(row, col, targetRow, targetCol, "n"))
        return moves

    def calculateBishopMoves(self, row: int, col: int, customBoard=None):
        directions = ((-1, 1), (1, 1), (-1, -1), (1, -1))  # up-right down-right up-left down-left
        return self.calculateRayMoves(row, col, directions, "b", customBoard)

    def calculateQueenMoves(self, row: int, col: int, customBoard=None):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        return self.calculateRayMoves(row, col, directions, "q", customBoard)

    def calculateRayMoves(self, row, col, directions, pieceType, customBoard):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        for direction in directions:
            for times in range(1, 8):
                targetRow = row + direction[0] * times
                targetCol = col + direction[1] * times
                if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                    targetPiece = board.getGrid()[targetRow][targetCol]
                    if targetPiece is None:
                        moves.append(Move(row, col, targetRow, targetCol, pieceType))
                    else:
                        targetPiece: Piece
                        if targetPiece.getColor() != self._activeColor:
                            moves.append(Move(row, col, targetRow, targetCol, pieceType))
                        break
                else:
                    break
        return moves

    def calculateKingMoves(self, row: int, col: int, customBoard=None):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        for direction in directions:
            targetRow = row + direction[0]
            targetCol = col + direction[1]
            if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                targetPiece = board.getGrid()[targetRow][targetCol]
                if targetPiece is None:
                    moves.append(Move(row, col, targetRow, targetCol, "k"))
                else:
                    targetPiece: Piece
                    if targetPiece.getColor() != self._activeColor:
                        moves.append(Move(row, col, targetRow, targetCol, "k"))
            # if considerSafeMovesOnly:
            #     if (targetRow, targetCol) not in self._attackedSquares:
            # else:
            #     moves.append(Move(row, col, targetRow, targetCol, "k"))
        return moves

    def calculateValidMoves(self, moveList=None):
        if moveList is None:
            moves = self._moves
        else:
            moves = moveList
        move: Move
        for move in list(moves):
            self._tempEnPassantSquare = self._enPassantSquare
            self._tempBlackKingPos = self._blackKingPos
            self._tempWhiteKingPos = self._whiteKingPos
            tempBoard = copy.deepcopy(self._board)
            self.makeMove(move, tempBoard)
            if self.calculateEnemyMoves(tempBoard):
                moves.remove(move)

    def calculateEnemyMoves(self, tempBoard):
        for rowNum, row in enumerate(tempBoard.getGrid()):
            for colNum, piece in enumerate(row):
                piece: Piece
                if piece is not None and piece.getColor() is not self._activeColor:
                    self._activeColor = not self._activeColor
                    enemyMoves = []
                    if piece.getType() == "p":
                        enemyMoves = self.calculatePawnMoves(rowNum, colNum, tempBoard)
                    elif piece.getType() == "r":
                        enemyMoves = self.calculateRookMoves(rowNum, colNum, tempBoard)
                    elif piece.getType() == "b":
                        enemyMoves = self.calculateBishopMoves(rowNum, colNum, tempBoard)
                    elif piece.getType() == "n":
                        enemyMoves = self.calculateKnightMoves(rowNum, colNum, tempBoard)
                    elif piece.getType() == "q":
                        enemyMoves = self.calculateQueenMoves(rowNum, colNum, tempBoard)
                    elif piece.getType() == "k":
                        enemyMoves = self.calculateKingMoves(rowNum, colNum, tempBoard)
                    self._activeColor = not self._activeColor
                    enemyMove: Move
                    for enemyMove in enemyMoves:
                        if self._activeColor:
                            if enemyMove.getTargetRowAndCol() == self._tempWhiteKingPos:
                                return True
                        else:
                            if enemyMove.getTargetRowAndCol() == self._tempBlackKingPos:
                                return True

    def inCheck(self):
        if self._activeColor:
            kingPos = self._whiteKingPos
        else:
            kingPos = self._blackKingPos
        self._activeColor = not self._activeColor
        self.calculateMoves()
        self._activeColor = not self._activeColor
        move: Move
        for move in self._moves:
            if move.getTargetRow() == kingPos[0] and move.getTargetCol() == kingPos[1]:
                return True
        return False
