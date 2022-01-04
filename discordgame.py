import engine
import discord
import colorsys
import random

class Game:

    def __init__(self, p1: discord.Member, p2: discord.Member):
        h,s,l = random.random(), 0.75 + random.random() / 4, 0.4 + random.random() / 5.0
        rgb = colorsys.hls_to_rgb(h,l,s)
        self.hexcolor = int(rgb[0]*255) * 65536 + int(rgb[1]*255) * 256 + int(rgb[2]*255)
        self.turnNum = 1
        self.player1 = p1
        self.player2 = p2
        self.controller = engine.GameController()
        self.processTurn()
        self.lastMove = "No moves have been made yet."


    def processTurn(self):
        self.controller.calculateMoves()
        self.controller.calculateSpecialMoves()
        self.controller.calculateValidMoves()
        if len(self.controller.getMoves()) == 0:
            mate = self.controller.inCheck()
            if mate:
                if not self.controller.getActiveColor():
                    return self.player1
                else:
                    return self.player2
            else:
                return "stalemate"

    def move(self, moveString):
        try:
            self.lastMove = self.controller.processMove(moveString)
            if not self.controller.getActiveColor():
                self.turnNum += 1
            self.controller.setActiveColor(not self.controller.getActiveColor())
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
        if self.controller.getActiveColor():
            return self.player1
        else:
            return self.player2

    def getBoardString(self):
        return str(self.controller.getBoard())
