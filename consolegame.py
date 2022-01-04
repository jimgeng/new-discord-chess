import engine

if __name__ == '__main__':
    # Setup
    controller = engine.GameController()
    turn = 0
    moveString = ""
    # Main loop
    while True:
        # Calculate all moves that the player can make
        controller.calculateMoves()
        # Calculate the special moves that the players can make (En Passant, Castle, Promotion)
        controller.calculateSpecialMoves()
        # Filters out any invalid moves in the current player's generated move set.
        controller.calculateValidMoves()
        # Prints out the board for the user to see
        controller.getBoard().prettyPrint()
        # If there are no moves left, someone has won or it is a stalemate
        if len(controller.getMoves()) == 0:
            break

        # Input loop
        while True:
            if controller.getActiveColor():
                moveString = input("White Move: ")
            else:
                moveString = input("Black Move: ")
                turn += 1
            # Error handling for various invalid inputs.
            try:
                controller.processMove(moveString) # This attempts to make the move.
                break
            except engine.AmbiguousMoveError:
                print("Please input a move that indicates the starting position.")
            except engine.InvalidMoveError:
                print("Please input a valid move.")
            except engine.IncorrectMoveStringLengthError:
                print("Please use either the 3 character notation or the 5 character notation")
            except engine.SpecifyPromotionError:
                print("Please specify the type of piece you would like to promote your pawn to.")
            except engine.ImpossiblePromotionError:
                print("You cannot promote to a king or pawn.")
        # Change color after the inputted move has been made
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
