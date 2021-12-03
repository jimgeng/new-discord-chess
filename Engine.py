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

    def __init__(self):
        self._grid: list = [[None for _ in range(8)] for _ in range(8)]

    def popCell(self, row: int, col: int) -> Piece:
        temp: Piece = self._grid[row][col]
        self._grid[row][col] = None
        return temp

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
            print(" " + str(rowCount))
            rowCount -= 1
        print("  A B C D E F G H  ")

    def getGrid(self):
        return self._grid


class Move:

    def __init__(self, oR, oC, tR, tC, id):
        self._originRow = oR
        self._originCol = oC
        self._targetRow = tR
        self._targetCol = tC
        self._moveID = id

    def __eq__(self, other):
        other: Move
        if self._moveID == other.getMoveID():
            return True
        else:
            return False

    def getMoveID(self):
        return self._moveID


class GameController:

    def __init__(self):
        self.board = Board()
        self.board.initializeBoard()
        self.activeColor = True

    def turnIntoMove(self, moveString) -> Move:
        if len(moveString) == 3:
            pass  # IMPLEMENT LATER THIS IS HARD AS SHIT TO IMPLEMENT
        elif len(moveString) == 5:
            originCol = ord(moveString[1]) - 97
            originRow = 8 - int(moveString[2])
            targetCol = ord(moveString[3]) - 97
            targetRow = 8 - int(moveString[4])
            moveID = originRow * 512 + originCol * 64 + targetRow * 8 + targetCol
            return Move(originRow, originCol, targetRow, targetCol, moveID)

    def calculateAllMoves(self):
        pseudoLegalMoves = []
        for rowNum, row in enumerate(self.board.getGrid()):
            for colNum, piece in enumerate(row):
                if piece is not None:
                    piece: Piece
                    if (piece.getColor() and self.activeColor) or (not piece.getColor() and not self.activeColor):
                        pseudoLegalMoves.extend(self.pieceTypeToFunction[piece.getType()](rowNum, colNum))
        return pseudoLegalMoves

    def calculateValidMoves(self, moves):
        return moves

    def calculatePawnMoves(self, row, col):
        pass

    def calculateRookMoves(self, row, col):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))  # up down right left
        return self.calculateRayMoves(row, col, directions)

    def calculateKnightMoves(self, row, col):
        moves = []
        potentialSquares = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        for square in potentialSquares:
            targetRow = row + square[0]
            targetCol = col + square[1]
            if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                targetPiece = self.board.getGrid()[targetRow][targetCol]
                if targetPiece is None:
                    moveID = row * 512 + col * 64 + targetRow * 8 + targetCol
                    moves.append(Move(row, col, targetRow, targetCol, moveID))
                else:
                    targetPiece: Piece
                    if targetPiece.getColor() != self.activeColor:
                        moveID = row * 512 + col * 64 + targetRow * 8 + targetCol
                        moves.append(Move(row, col, targetRow, targetCol, moveID))

    def calculateBishopMoves(self, row, col):
        directions = ((-1, 1), (1, 1), (-1, -1), (1, -1))  # up-right down-right up-left down-left
        return self.calculateRayMoves(row, col, directions)

    def calculateQueenMoves(self, row, col):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        return self.calculateRayMoves(row, col, directions)

    def calculateRayMoves(self, row, col, directions):
        moves = []
        for direction in directions:
            for times in range(8):
                targetRow = row + direction[0] * times
                targetCol = col + direction[1] * times
                if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                    targetPiece = self.board.getGrid()[targetRow][targetCol]
                    if targetPiece is None:
                        moveID = row * 512 + col * 64 + targetRow * 8 + targetCol
                        moves.append(Move(row, col, targetRow, targetCol, moveID))
                    else:
                        targetPiece: Piece
                        if targetPiece.getColor() != self.activeColor:
                            moveID = row * 512 + col * 64 + targetRow * 8 + targetCol
                            moves.append(Move(row, col, targetRow, targetCol, moveID))
                        break
                else:
                    break
        return moves

    def calculateKingMoves(self, row, col):
        pass

    pieceTypeToFunction = {
        "p": calculatePawnMoves,
        "r": calculateRookMoves,
        "n": calculateKnightMoves,
        "b": calculateBishopMoves,
        "q": calculateQueenMoves,
        "k": calculateKingMoves
    }
