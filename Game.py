import Engine

if __name__ == '__main__':
    # Setup
    controller = Engine.GameController()
    looping = True
    turn = 0
    moveString = ""
    # Main loop
    while looping:
        controller.getBoard().prettyPrint()
        controller.calculateMoves()
        controller.calculateValidMoves()
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
        controller.setActiveColor(not controller.getActiveColor())
