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
    startingFenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    # startingFenString = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR"

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
    pass


class AmbiguousMoveError(MoveErrors):
    pass


class InvalidMoveError(MoveErrors):
    pass


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


class GameController:

    def __init__(self):
        self._board = Board()
        self._board.initializeBoard()
        self._activeColor = True
        self._promotionSquare = []
        self._whiteKingPos = [7, 4]
        self._blackKingPos = [0, 4]
        self._moves = []
        self._attackedSquares = []

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

    def getValidMoves(self):
        return self._moves

    def clearPromotionSquares(self):
        self._promotionSquare = []

    def makeMove(self, move: Move):
        piece = self._board.popCell(move.getOriginRow(), move.getOriginCol())
        self._board.editCell(move.getTargetRow(), move.getTargetCol(), piece)

    def processMove(self, moveString):
        finalizedMove = None
        if len(moveString) == 3:
            targetRow = 8 - int(moveString[2])
            targetCol = ord(moveString[1].lower()) - 97
            targetType = moveString[0]
            move: Move
            possibleMove = [move for move in self._moves if move.getTargetRowAndCol() == (targetRow, targetCol) and move.getPieceType() == targetType]
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
        if finalizedMove is not None:
            self.makeMove(finalizedMove)

    def calculateMoves(self):
        for rowNum, row in enumerate(self._board.getGrid()):
            for colNum, piece in enumerate(row):
                if piece is not None:
                    piece: Piece
                    if (piece.getColor() and self._activeColor) or (not piece.getColor() and not self._activeColor):
                        self._moves += self.pieceTypeToFunction[piece.getType()](self, rowNum, colNum)

    def calculatePawnMoves(self, row: int, col: int):
        moves = []
        if self._activeColor and row > 0:
            if self._board.getGrid()[row - 1][col] is None:
                moves.append(Move(row, col, row - 1, col, "p"))
                if row == 1:
                    self._promotionSquare.append((row - 1, col))
                if row == 6 and self._board.getGrid()[row - 2][col] is None:
                    moves.append(Move(row, col, row - 2, col, "p"))
            if col < 7:
                enemyPiece = self._board.getGrid()[row - 1][col + 1]
                if enemyPiece is not None:
                    enemyPiece: Piece
                    if enemyPiece.getColor() is not self._activeColor:
                        moves.append(Move(row, col, row - 1, col + 1, "p"))
                        if row == 1:
                            self._promotionSquare.append((row - 1, col + 1))
            if col > 0:
                enemyPiece = self._board.getGrid()[row - 1][col - 1]
                if enemyPiece is not None:
                    enemyPiece: Piece
                    if enemyPiece.getColor() is not self._activeColor:
                        moves.append(Move(row, col, row - 1, col - 1, "p"))
                        if row == 1:
                            self._promotionSquare.append((row - 1, col - 1))
        else:
            if self._board.getGrid()[row + 1][col] is None:
                moves.append(Move(row, col, row + 1, col, "p"))
                if row == 6:
                    self._promotionSquare.append((row + 1, col))
                if row == 1 and self._board.getGrid()[row + 2][col] is None:
                    moves.append(Move(row, col, row + 2, col, "p"))
            if col < 7:
                enemyPiece = self._board.getGrid()[row + 1][col + 1]
                if enemyPiece is not None:
                    enemyPiece: Piece
                    if enemyPiece.getColor() is not self._activeColor:
                        moves.append(Move(row, col, row + 1, col + 1, "p"))
                        if row == 6:
                            self._promotionSquare.append((row + 1, col + 1))
            if col > 0:
                enemyPiece = self._board.getGrid()[row + 1][col - 1]
                if enemyPiece is not None:
                    enemyPiece: Piece
                    if enemyPiece.getColor() is not self._activeColor:
                        moves.append(Move(row, col, row + 1, col - 1, "p"))
                        if row == 6:
                            self._promotionSquare.append((row + 1, col - 1))
        return moves

    def calculateRookMoves(self, row: int, col: int):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))  # up down right left
        return self.calculateRayMoves(row, col, directions, "r")

    def calculateKnightMoves(self, row: int, col: int):
        moves = []
        potentialSquares = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        for square in potentialSquares:
            targetRow = row + square[0]
            targetCol = col + square[1]
            if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                targetPiece = self._board.getGrid()[targetRow][targetCol]
                if targetPiece is None:
                    moves.append(Move(row, col, targetRow, targetCol, "n"))
                else:
                    targetPiece: Piece
                    if targetPiece.getColor() != self._activeColor:
                        moves.append(Move(row, col, targetRow, targetCol, "n"))
        return moves

    def calculateBishopMoves(self, row: int, col: int):
        directions = ((-1, 1), (1, 1), (-1, -1), (1, -1))  # up-right down-right up-left down-left
        return self.calculateRayMoves(row, col, directions, "b")

    def calculateQueenMoves(self, row: int, col: int):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        return self.calculateRayMoves(row, col, directions, "q")

    def calculateRayMoves(self, row, col, directions, pieceType):
        moves = []
        for direction in directions:
            for times in range(1, 8):
                targetRow = row + direction[0] * times
                targetCol = col + direction[1] * times
                if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                    targetPiece = self._board.getGrid()[targetRow][targetCol]
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

    def calculateKingMoves(self, row: int, col: int):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        for direction in directions:
            targetRow = row + direction[0]
            targetCol = col + direction[1]
            if (targetRow, targetCol) not in self._attackedSquares:
                pass

    pieceTypeToFunction = {
        "p": calculatePawnMoves,
        "r": calculateRookMoves,
        "n": calculateKnightMoves,
        "b": calculateBishopMoves,
        "q": calculateQueenMoves,
        "k": calculateKingMoves
    }
