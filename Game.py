import Engine

if __name__ == '__main__':
    # Setup
    controller = Engine.GameController()
    controller.initializeBoard()
    looping = True
    turn = 0
    moveString = ""
    # Main loop
    while looping:
        moves = controller.calculateValidMoves
        if controller.activeColor:
            moveString = input("White Move: ")  # CHANGE THIS FOR DISCORD
        else:
            moveString = input("Black Move: ")
            turn += 1
    move = controller.turnIntoMove(moveString)
