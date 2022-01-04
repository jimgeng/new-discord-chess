import copy


class Piece:
    """
    Piece class has two attributes:
     - Color: Boolean
     - Piece Type: String
    """

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
    # A fenstring is a custom notation that can represent the entire board with a simple string.
    # This is the fenstring for the starting board position
    startingFenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    def __init__(self):
        self._grid: list = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self):
        boardStr = "    A   B   C   D   E   F   G   H\n  ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗\n"
        for i, row in enumerate(self._grid):
            boardStr += f"{8-i} ║"
            piece: Piece
            for j, piece in enumerate(row):
                if piece is None:
                    if (i + j) % 2 == 0:
                        boardStr += "   ║"
                    else:
                        boardStr += "░░░║"
                else:
                    # boardStr += f" {piece} ║"
                    boardStr += f" {piece} ║"
            boardStr += "\n"
            if i < 7:
                boardStr += "  ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣\n"
        boardStr += "  ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝"
        return boardStr

    def popCell(self, row: int, col: int) -> Piece:
        """Returns and removes element from the specified position on the board"""
        temp: Piece = self._grid[row][col]
        self._grid[row][col] = None
        return temp

    def editCell(self, row, col, piece):
        """Overwrites the specified cell with the specified piece."""
        self._grid[row][col] = piece

    def initializeBoard(self):
        """
        Fills the board for the start of the game with the pieces
        in the starting position by using the starting fenstring.
        """
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
        """
        Prints out the board with pretty colors for the pieces if the terminal
        is modern enough, and also shows the coordinates.
        """
        # print("  A B C D E F G H  ")
        # rowCount = 8
        # for row in self._grid:
        #     print(rowCount, end=" ")
        #     piece: Piece
        #     for piece in row:
        #         if piece is None:
        #             print("0", end=" ")
        #         else:
        #             if piece.getColor():
        #                 color = "\033[96m"
        #             else:
        #                 color = "\033[92m"
        #             print(f"{color}{piece}\033[0m", end=" ")
        #     print(str(rowCount))
        #     rowCount -= 1
        # print("  A B C D E F G H  ")
        print(self)

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


class SpecifyPromotionError(MoveErrors):
    """The player must specify which type to promote to."""


class ImpossiblePromotionError(MoveErrors):
    """If the player tries to promote to a pawn or king"""


class Move:
    """
    The move class has various attributes to determine the starting
    and ending positions of a move, it also holds info about the
    type of piece that it wants to move.

    A special integer called move id is calculated through using the four
    positional integers. This is used to compare if two moves are the same.
    """

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

    def getMoveID(self):
        return self._moveID

    def getTargetRowAndCol(self):
        return self._targetRow, self._targetCol

    def getPieceType(self):
        return self._pieceType

    def __eq__(self, other):
        """To check if the moves are equal, the move id of the two moves is compared"""
        other: Move
        if self._moveID == other.getMoveID():
            return True
        else:
            return False

    def __repr__(self):
        """
        the string representation of the move is the piece type followed by the starting position
        and then the target position, both shown in chess notation.
        """
        originString = chr(self._originCol + 97) + str(8 - self._originRow)
        targetString = chr(self._targetCol + 97) + str(8 - self._targetRow)
        return f"{self._pieceType}{originString}{targetString}"


class EnPassantMove(Move):
    """
    EnPassantMove is a move class subclass with an additional enemy location to store
    where the enemy pawn to be taken is doing the en passant.
    """

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
        # Chess board is initalized as self._board
        self._board = Board()
        # Fill it
        self._board.initializeBoard()
        # White goes first
        self._activeColor = True
        # The moves list that stores all the possible moves a player can make
        self._moves = []

        # These are information attributes to be used through the move calculating and move making process
        self._attackedSquares = set()
        self._enPassantSquare = tuple()
        self._tempEnPassantSquare = tuple()
        self._promotionType = None
        self._promotionSquares = []
        # These king position
        self._whiteKingPos = (7, 4)
        self._tempWhiteKingPos = tuple()
        self._whiteCastleAvailability = [True, True]
        self._whiteCanCastleThisTurn = [False, False]
        self._blackKingPos = (0, 4)
        self._tempBlackKingPos = tuple()
        self._blackCastleAvailability = [True, True]
        self._blackCanCastleThisTurn = [False, False]

    def getActiveColor(self):
        return self._activeColor

    def setActiveColor(self, color):
        self._activeColor = color

    def getBoard(self):
        return self._board

    def getMoves(self):
        return self._moves

    def processMove(self, moveString):
        finalizedMove = None  # single move to be made for most cases
        finalizedMoves = []  # move list for things castling
        moveString = moveString.lower()
        returnedString =""
        # when castling happens, theres 2 moves that happen simultaneously
        # the rook moves to a position 1 square away from the king, and then the king hops over the rook.
        if moveString == "0-0":
            if self._activeColor:
                if self._whiteCanCastleThisTurn[0]:
                    # predefined values because there can be only one type of white king side castle.
                    finalizedMoves.append(Move(7, 7, 7, 5, "r"))
                    finalizedMoves.append(Move(7, 4, 7, 6, "k"))
                else:
                    raise InvalidMoveError
            else:
                if self._blackCanCastleThisTurn[0]:
                    finalizedMoves.append(Move(0, 7, 0, 5, "r"))
                    finalizedMoves.append(Move(0, 4, 0, 6, "k"))
                else:
                    raise InvalidMoveError
            returnedString = "0-0"
        elif moveString == "0-0-0":
            # queenside castling
            if self._activeColor:
                if self._whiteCanCastleThisTurn[1]:
                    finalizedMoves.append(Move(7, 0, 7, 3, "r"))
                    finalizedMoves.append(Move(7, 4, 7, 2, "k"))
            else:
                if self._blackCanCastleThisTurn[1]:
                    finalizedMoves.append(Move(0, 0, 0, 3, "r"))
                    finalizedMoves.append(Move(0, 4, 0, 2, "k"))
            returnedString = "0-0-0"
        elif len(moveString) == 2:
            try:
                targetRow = 8 - int(moveString[1])
                targetCol = ord(moveString[0].lower()) - 97
                targetType = "p"
            except ValueError:
                raise InvalidMoveError
            if (self._activeColor and targetRow == 0) or (not self._activeColor and targetRow == 7):
                raise SpecifyPromotionError
            move: Move
            possibleMove = [move for move in self._moves if
                            move.getTargetRowAndCol() == (targetRow, targetCol) and move.getPieceType() == targetType]
            if len(possibleMove) == 1:
                # only make the move if there is one option
                finalizedMove = possibleMove[0]
            elif len(possibleMove) > 1:
                raise AmbiguousMoveError
            else:
                raise InvalidMoveError
        elif len(moveString) == 3:
            # This is a move entered without the starting position
            # The program searches through all available moves to see if there are any moves
            # that match the end target location of the move the user specified.
            # If there is more than one match a AmbiguousMoveError is raised.
            try:
                targetRow = 8 - int(moveString[2])
                targetCol = ord(moveString[1].lower()) - 97
                targetType = moveString[0]
            except ValueError:
                raise InvalidMoveError
            # if it is a pawn move onto the final row, then the user must specify a type of piece to promote to.
            if targetType == "p" and (
                    (self._activeColor and targetRow == 0) or (not self._activeColor and targetRow == 7)):
                raise SpecifyPromotionError
            move: Move
            # the loop to see if any of them match the users move
            possibleMove = [move for move in self._moves if
                            move.getTargetRowAndCol() == (targetRow, targetCol) and move.getPieceType() == targetType]
            if len(possibleMove) == 1:
                # only make the move if there is one option
                finalizedMove = possibleMove[0]
            elif len(possibleMove) > 1:
                raise AmbiguousMoveError
            else:
                raise InvalidMoveError
        elif len(moveString) == 4:
            # pawn promotion
            if moveString[0] != "p":
                # if it isn't a pawn then the user has entered something invalid.
                raise InvalidMoveError
            try:
                targetRow = 8 - int(moveString[2])
                targetCol = ord(moveString[1].lower()) - 97
                self._promotionType = moveString[3]
            except ValueError:
                raise InvalidMoveError
            if self._promotionType == "p" or self._promotionType == "k":
                # the user cannot promote from a pawn to a pawn or king.
                raise ImpossiblePromotionError
            if (self._activeColor and targetRow != 0) or (not self._activeColor and targetRow != 7):
                raise InvalidMoveError
            move: Move
            for move in self._moves:
                if move.getTargetRowAndCol() == (targetRow, targetCol) and move.getPieceType() == "p":
                    finalizedMove = move
                    break
            else:
                raise InvalidMoveError
        elif len(moveString) == 5:
            # can be used normally, but mainly used to distinguish between ambiguous 3 character moves.
            targetRow = 8 - int(moveString[4])
            targetCol = ord(moveString[3].lower()) - 97
            originRow = 8 - int(moveString[2])
            originCol = ord(moveString[1].lower()) - 97
            targetType = moveString[0]
            # since all parameters are specified, the program doesn't need to look at
            # if any of the calculated moves match the target position
            # it just needs to see if the move the user specified is in the list of available moves.
            possibleMove = Move(originRow, originCol, targetRow, targetCol, targetType)
            if possibleMove in self._moves:
                finalizedMove = possibleMove
            else:
                raise InvalidMoveError
        else:
            raise IncorrectMoveStringLengthError
        # finally, make the move/moves
        if finalizedMove is not None:
            self.makeMove(finalizedMove)
            returnedString = str(finalizedMove.__repr__())
        if len(finalizedMoves) != 0:
            for move in finalizedMoves:
                self.makeMove(move)
        return returnedString


    def makeMove(self, move, customBoard=None):
        """
        takes a move and makes it on the main board if a custom temporary board
        has not been provided
        """
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        # custom move instructions for en passant
        if isinstance(move, EnPassantMove):
            pawn = board.popCell(move.getOriginRow(), move.getOriginCol())
            board.editCell(move.getTargetRow(), move.getTargetCol(), pawn)
            board.popCell(move.getEnemyRow(), move.getEnemyCol())
        else:
            piece = board.popCell(move.getOriginRow(), move.getOriginCol())
            board.editCell(move.getTargetRow(), move.getTargetCol(), piece)
            # special conditions pertaining to
            # rooks (castling), pawns (en passant), and kings (castling and checks)
            if piece.getType() == "r":
                if customBoard is None:
                    if piece.getColor():
                        if move.getOriginRow() == 7 and move.getOriginCol() == 7:
                            self._whiteCastleAvailability[0] = False
                        if move.getOriginRow() == 7 and move.getOriginCol() == 0:
                            self._whiteCastleAvailability[1] = False
                    else:
                        if move.getOriginRow() == 0 and move.getOriginCol() == 7:
                            self._blackCastleAvailability[0] = False
                        if move.getOriginRow() == 0 and move.getOriginCol() == 0:
                            self._blackCastleAvailability[1] = False
            if piece.getType() == "p":
                if customBoard is None:
                    if move.getTargetRow() - move.getOriginRow() == 2:
                        self._enPassantSquare = (move.getTargetRow(), move.getTargetCol(), False)
                    elif move.getTargetRow() - move.getOriginRow() == -2:
                        self._enPassantSquare = (move.getTargetRow(), move.getTargetCol(), True)
                    if piece.getColor() and move.getTargetRow() == 0:
                        board.editCell(move.getTargetRow(), move.getTargetCol(), Piece(True, self._promotionType))
                    elif not piece.getColor() and move.getTargetRow() == 7:
                        board.editCell(move.getTargetRow(), move.getTargetCol(), Piece(False, self._promotionType))

                else:
                    if move.getTargetRow() - move.getOriginRow() == 2:
                        self._tempEnPassantSquare = (move.getTargetRow(), move.getTargetCol(), False)
                    elif move.getTargetRow() - move.getOriginRow() == -2:
                        self._tempEnPassantSquare = (move.getTargetRow(), move.getTargetCol(), True)
            elif piece.getType() == "k":
                if customBoard is None:
                    if piece.getColor():
                        self._whiteKingPos = (move.getTargetRow(), move.getTargetCol())
                        self._whiteCastleAvailability = [False, False]
                    else:
                        self._blackKingPos = (move.getTargetRow(), move.getTargetCol())
                        self._blackCastleAvailability = [False, False]
                else:
                    if piece.getColor():
                        self._tempWhiteKingPos = (move.getTargetRow(), move.getTargetCol())
                    else:
                        self._tempBlackKingPos = (move.getTargetRow(), move.getTargetCol())

    def calculateMoves(self):
        """Calculates ALL moves for every piece that belongs to the current player on the board."""
        # clear necessary attributes
        self._whiteCanCastleThisTurn = [False, False]
        self._blackCanCastleThisTurn = [False, False]
        self._promotionSquares = []
        self._moves = []
        # calculates the moves for every piece that belongs to the current player on the board
        for rowNum, row in enumerate(self._board.getGrid()):
            for colNum, piece in enumerate(row):
                piece: Piece
                # use the move function according the piece type
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
        """Calculates special moves that the current player can make"""
        # En Passant
        if self._enPassantSquare != ():
            if self._enPassantSquare[2] == self._activeColor:
                self._enPassantSquare = ()
            else:
                # for columns 2-8 check the left square
                if self._enPassantSquare[1] > 0:
                    leftPiece = self._board.getGrid()[self._enPassantSquare[0]][self._enPassantSquare[1] - 1]
                    leftPiece: Piece
                    # add the en passant move if it is valid.
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
            kingInCheck = [
                Move(self._whiteKingPos[0], self._whiteKingPos[1], self._whiteKingPos[0], self._whiteKingPos[1], "k")]
            self.calculateValidMoves(kingInCheck)
            if len(kingInCheck) == 1:
                if self._whiteCastleAvailability[0]:
                    # white king side castle
                    kingSubMoves = []
                    # check if the squares the king has to move through are attacked
                    for i in range(1, 3):
                        if self._board.getGrid()[self._whiteKingPos[0]][self._whiteKingPos[1] + i] is None:
                            kingSubMoves.append(
                                Move(self._whiteKingPos[0], self._whiteKingPos[1], self._whiteKingPos[0],
                                     self._whiteKingPos[1] + i, "k"))
                        else:
                            break
                    self.calculateValidMoves(kingSubMoves)
                    # if they are all valid then make the castling move valid.
                    if len(kingSubMoves) == 2:
                        self._whiteCanCastleThisTurn[0] = True
                if self._whiteCastleAvailability[1]:
                    # white queen side castle
                    kingSubMoves = []
                    for i in range(-1, -4, -1):
                        if self._board.getGrid()[self._whiteKingPos[0]][self._whiteKingPos[1] + i] is None:
                            kingSubMoves.append(
                                Move(self._whiteKingPos[0], self._whiteKingPos[1], self._whiteKingPos[0],
                                     self._whiteKingPos[1] + i, "k"))
                        else:
                            break
                    self.calculateValidMoves(kingSubMoves)
                    if len(kingSubMoves) == 3:
                        self._whiteCanCastleThisTurn[1] = True
        else:
            kingInCheck = [
                Move(self._blackKingPos[0], self._blackKingPos[1], self._blackKingPos[0], self._blackKingPos[1], "k")]
            self.calculateValidMoves(kingInCheck)
            if len(kingInCheck) == 1:
                if self._blackCastleAvailability[0]:
                    # black king side castle
                    kingSubMoves = []
                    for i in range(1, 3):
                        if self._board.getGrid()[self._blackKingPos[0]][self._blackKingPos[1] + i] is None:
                            kingSubMoves.append(
                                Move(self._blackKingPos[0], self._blackKingPos[1], self._blackKingPos[0],
                                     self._blackKingPos[1] + i, "k"))
                        else:
                            break
                    self.calculateValidMoves(kingSubMoves)
                    if len(kingSubMoves) == 2:
                        self._blackCanCastleThisTurn[0] = True
                if self._blackCastleAvailability[1]:
                    # black queen side castle
                    kingSubMoves = []
                    for i in range(-1, -4, -1):
                        if self._board.getGrid()[self._blackKingPos[0]][self._blackKingPos[1] + i] is None:
                            kingSubMoves.append(
                                Move(self._blackKingPos[0], self._blackKingPos[1], self._blackKingPos[0],
                                     self._blackKingPos[1] + i, "k"))
                        else:
                            break
                    self.calculateValidMoves(kingSubMoves)
                    if len(kingSubMoves) == 3:
                        self._blackCanCastleThisTurn[1] = True

    def calculateValidMoves(self, moveList=None):
        """Filters out any invalid moves that exists in the current moves list."""
        if moveList is None:
            moves = self._moves
        else:
            moves = moveList
        move: Move
        # loops through each of the moves, makes the move, and then checks to see if your king can be captured.
        for move in list(moves):
            self._tempEnPassantSquare = self._enPassantSquare
            self._tempBlackKingPos = self._blackKingPos
            self._tempWhiteKingPos = self._whiteKingPos
            tempBoard = copy.deepcopy(self._board)
            self.makeMove(move, tempBoard)
            if self.calculateEnemyMoves(tempBoard):
                moves.remove(move)

    def calculateEnemyMoves(self, tempBoard):
        """
        Checks if your king can be captured under the current board circumstances.
        A custom board can be provided, and is used to check valid moves.
        It is similar to the calculate moves function but does it for the enemy.
        """
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
                        # if the king can be captured, return True.
                        if self._activeColor:
                            if enemyMove.getTargetRowAndCol() == self._tempWhiteKingPos:
                                return True
                        else:
                            if enemyMove.getTargetRowAndCol() == self._tempBlackKingPos:
                                return True

    def inCheck(self):
        """
        Used to check at the end of the game if there is a king in check or not
        to determine checkmate or stalemate
        """
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

    # These are the move calculations for each of the different types of pieces.
    # Custom boards can be used in each one in order to check for valid moves.

    def calculatePawnMoves(self, row, col, customBoard=None, customPromoList=None):
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
            # white pawn
            if board.getGrid()[row - 1][col] is None:
                # normal move
                moves.append(Move(row, col, row - 1, col, "p"))
                if row == 1:
                    promotionSquareList.append((row - 1, col))
                if row == 6 and board.getGrid()[row - 2][col] is None:
                    moves.append(Move(row, col, row - 2, col, "p"))
                    # self._enPassantSquare = (row - 2, col, True)
            if col < 7:
                # capture to the right
                enemyPiece = board.getGrid()[row - 1][col + 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row - 1, col + 1, "p"))
                    if row == 1:
                        promotionSquareList.append((row - 1, col + 1))
            if col > 0:
                # capture to the left
                enemyPiece = board.getGrid()[row - 1][col - 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row - 1, col - 1, "p"))
                    if row == 1:
                        promotionSquareList.append((row - 1, col - 1))
        else:
            # black pawn
            if board.getGrid()[row + 1][col] is None:
                # normal movement
                moves.append(Move(row, col, row + 1, col, "p"))
                if row == 6:
                    promotionSquareList.append((row + 1, col))
                if row == 1 and board.getGrid()[row + 2][col] is None:
                    moves.append(Move(row, col, row + 2, col, "p"))
                    # self._enPassantSquare = (row + 2, col, False)
            if col < 7:
                # capture to the right
                enemyPiece = board.getGrid()[row + 1][col + 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row + 1, col + 1, "p"))
                    if row == 6:
                        promotionSquareList.append((row + 1, col + 1))
            if col > 0:
                # capture to the left
                enemyPiece = board.getGrid()[row + 1][col - 1]
                enemyPiece: Piece
                if enemyPiece is not None and enemyPiece.getColor() is not self._activeColor:
                    moves.append(Move(row, col, row + 1, col - 1, "p"))
                    if row == 6:
                        promotionSquareList.append((row + 1, col - 1))
        return moves

    # rook bishop and queen moves are all calculated through one general function called calculate ray moves
    # only the directions it checks in has to be specified.

    def calculateRookMoves(self, row, col, customBoard=None):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))  # up down right left
        return self.calculateRayMoves(row, col, directions, "r", customBoard)

    def calculateKnightMoves(self, row, col, customBoard=None):
        """The knight just has a 8 specific offset distances it can travel to."""
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        potentialSquares = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        for square in potentialSquares:
            targetRow = row + square[0]
            targetCol = col + square[1]
            # various checks to make sure the move doesn't move onto another allied piece or off the board.
            if 0 <= targetRow < 8 and 0 <= targetCol < 8:
                targetPiece = board.getGrid()[targetRow][targetCol]
                if targetPiece is None:
                    moves.append(Move(row, col, targetRow, targetCol, "n"))
                else:
                    targetPiece: Piece
                    if targetPiece.getColor() != self._activeColor:
                        moves.append(Move(row, col, targetRow, targetCol, "n"))
        return moves

    def calculateBishopMoves(self, row, col, customBoard=None):
        directions = ((-1, 1), (1, 1), (-1, -1), (1, -1))  # up-right down-right up-left down-left
        return self.calculateRayMoves(row, col, directions, "b", customBoard)

    def calculateQueenMoves(self, row, col, customBoard=None):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1))
        return self.calculateRayMoves(row, col, directions, "q", customBoard)

    def calculateRayMoves(self, row, col, directions, pieceType, customBoard):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        # for each of the directions either go until its off the board or until a enemy or allied piece is hit
        # if it is a enemy piece hit also add the enemy piece's location as a possible move.
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

    def calculateKingMoves(self, row, col, customBoard=None):
        if customBoard is None:
            board = self._board
        else:
            board = customBoard
        moves = []
        # king move is similar to queen move except it isn't a sliding piece so these offsets are static.s
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
        return moves
