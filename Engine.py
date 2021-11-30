class Piece:

    def __init__(self, color: bool, pieceType: str):
        self.color = color
        self.pieceType = pieceType

    def __repr__(self):
        if self.color:
            return self.pieceType.upper()


class Board:
    startingFenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self):
        self.grid: list = [[None for _ in range(8)] for _ in range(8)]

    def popCell(self, row: int, col: int) -> Piece:
        temp: Piece = self.grid[row][col]
        self.grid[row][col] = None
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
                    self.grid[selectedRow][fillPointer] = newPiece
                    fillPointer += 1
                elif ch.isnumeric():
                    fillPointer += int(ch)
            else:
                fillPointer = 0
                selectedRow += 1

    def prettyPrint(self):
        print("  A B C D E F G H  ")
        rowCount = 8
        for row in self.grid:
            print(rowCount, end=" ")
            piece: Piece
            for piece in row:
                if piece is None:
                    print("0", end=" ")
                else:
                    if piece.color:
                        color = "\033[96m"
                    else:
                        color = "\033[92m"
                    print(f"{color}{piece}\033[0m", end=" ")
            print(" " + str(rowCount))
            rowCount -= 1
        print("  A B C D E F G H  ")


class Move:

    def __init__(self, oR, oC, tR, tC):
        self.originRow = oR
        self.originCol = oC
        self.targetRow = tR
        self.targetCol = tC


class GameController:

    def __init__(self):
        self.board = Board()
        self.board.initializeBoard()
        self.activeColor = True

    def turnIntoMove(self, moveString) -> Move:
        if len(moveString) == 3:
            pass  # IMPLEMENT LATER THIS IS HARD AS SHIT TO IMPLEMENT
        elif len(moveString) == 5:
            pass

    def calculateAllMoves(self):
        pseudoLegalMoves = []
        for rowNum, row in enumerate(self.board.grid):
            for colNum, piece in enumerate(row):
                if piece is not None:
                    piece: Piece
                    if (piece.color and self.activeColor) or (not piece.color and not self.activeColor):
                        if piece.pieceType == "p":
                            pass  # IMPLEMENT LATER THIS IS HARD AS SHIT TO IMPLEMENT
                        elif piece.pieceType == "r":
                            directions = ((-1, 0), (1, 0), (0, 1), (0, -1))  # up down right left
                            for direction in directions:
                                for times in range(8):
                                    targetRow = rowNum + direction[0] * times
                                    targetCol = colNum + direction[1] * times
                                    if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                                        pass
                        elif piece.pieceType == "n":
                            pass
                        elif piece.pieceType == "b":
                            pass
                        elif piece.pieceType == "q":
                            pass
                        elif piece.pieceType == "k":
                            pass
        return pseudoLegalMoves

    def calculateValidMoves(self):
        pass
