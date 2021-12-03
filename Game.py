import Engine

if __name__ == '__main__':
    # Setup
    controller = Engine.GameController()
    controller.board.initializeBoard()
    looping = True
    turn = 0
    moveString = ""
    # Main loop
    while looping:
        if controller.activeColor:
            moveString = input("White Move: ")  # CHANGE THIS FOR DISCORD
        else:
            moveString = input("Black Move: ")
            turn += 1
        validMoves = controller.calculateValidMoves(controller.calculateAllMoves())
        move = controller.turnIntoMove(moveString)
        controller.activeColor = not controller.activeColor
