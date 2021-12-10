import Engine

if __name__ == '__main__':
    # Setup
    controller = Engine.GameController()
    looping = True
    turn = 0
    moveString = ""
    # Main loop
    while looping:
        controller._promotionSquare = []
        validMoves = controller.calculateValidMoves(controller.calculateAllMoves())
        controller.getBoard().prettyPrint()
        print(validMoves)
        while True:
            if controller.getActiveColor():
                moveString = input("White Move: ")  # CHANGE THIS FOR DISCORD
            else:
                moveString = input("Black Move: ")
                turn += 1
            try:
                move = controller.processMove(moveString, validMoves)
                break
            except Engine.AmbiguousMoveError:
                print("Please input a move that indicates the starting position.")
            except Engine.InvalidMoveError:
                print("Please input a valid move.")




        controller.setActiveColor(not controller.getActiveColor())