import engine
import discord
import colorsys
import random

class Game:

    def __init__(self, p1: discord.Member, p2: discord.Member, time, inc):
        h,s,l = random.random(), 0.75 + random.random() / 4, 0.4 + random.random() / 5.0
        rgb = colorsys.hls_to_rgb(h,l,s)
        self._hexColor = int(rgb[0]*255) * 65536 + int(rgb[1]*255) * 256 + int(rgb[2]*255)
        self._turnNum = 1
        self._controller = engine.GameController()
        self._lastMove = "No moves have been made yet."
        self.player1 = p1
        self.player2 = p2
        self.processTurn()
        self.moveTimes = {
            p1.id: time,
            p2.id: time
        }
        self.timeIncrement = inc

    def processTurn(self):
        self._controller.calculateMoves()
        self._controller.calculateSpecialMoves()
        self._controller.calculateValidMoves()
        if len(self._controller.getMoves()) == 0:
            mate = self._controller.inCheck()
            if mate:
                if not self._controller.getActiveColor():
                    return self.player1
                else:
                    return self.player2
            else:
                return "stalemate"

    def attemptMove(self, moveString):
        try:
            self._lastMove = self._controller.processMove(moveString)
            if not self._controller.getActiveColor():
                self._turnNum += 1
            self._controller.setActiveColor(not self._controller.getActiveColor())
        except engine.AmbiguousMoveError:
            return "Please input a move that indicates the starting position."
        except engine.InvalidMoveError:
            return "Please input a valid move."
        except engine.IncorrectMoveStringLengthError:
            return "Please use either the 3 character notation or the 5 character notation"
        except engine.SpecifyPromotionError:
            return "Please specify the type of piece you would like to promote your pawn to."
        except engine.ImpossiblePromotionError:
            return "You cannot promote to a king or pawn."

    def getActivePlayer(self):
        if self._controller.getActiveColor():
            return self.player1
        else:
            return self.player2

    def getNotActivePlayer(self):
        if self._controller.getActiveColor():
            return self.player2
        else:
            return self.player1

    def getBoardString(self):
        return str(self._controller.getBoard())

    def getHexColor(self):
        return self._hexColor

    def getTurnNum(self):
        return self._turnNum

    def getLastMove(self):
        return self._lastMove