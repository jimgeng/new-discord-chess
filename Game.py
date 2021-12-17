import Engine

if __name__ == '__main__':
    # Setup
    controller = Engine.GameController()
    looping = True
    turn = 0
    moveString = ""
    # Main loop
    while looping:
        print(controller._enPassantSquare)
        controller.calculateMoves()
        controller.calculateSpecialMoves()
        controller.calculateValidMoves()
        controller.getBoard().prettyPrint()
        print(controller.getMoves())
        if len(controller.getMoves()) == 0:
            break
        while True:
            if controller.getActiveColor():
                moveString = input("White Move: ")  # CHANGE THIS FOR DISCORD
            else:
                moveString = input("Black Move: ")
                turn += 1
            try:
                controller.processMove(moveString)
                break
            except Engine.AmbiguousMoveError:
                print("Please input a move that indicates the starting position.")
            except Engine.InvalidMoveError:
                print("Please input a valid move.")
            except ValueError:
                print("Please input a valid move.")
            except Engine.IncorrectMoveStringLengthError:
                print("Please use either the 3 character notation or the 5 character notation")
        controller.setActiveColor(not controller.getActiveColor())
    mate = controller.inCheck()
    if mate:
        if not controller.getActiveColor():
            # When it checks to see who won, technically it is on blacks turn that he loses
            # So white wins if it is currently black playing. That is why the "not" exists
            print("White has won with checkmate.")
        else:
            print("Black has won with checkmate.")
    else:
        print("The game has ended in a stalemate.")
