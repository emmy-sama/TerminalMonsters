from bearlibterminal import terminal


# Number of inputs can be an integer of 1-7 and will return an integer of 0-6 based on the key pressed by player,
# Setting enter and or backspace to true makes those valid inputs along with any integer inputs set.
def get_input(number_of_inputs=0, is_enter_used=False, is_backspace_used=False):
    while True:
        if number_of_inputs == 0 and not is_enter_used and not is_backspace_used:
            break
        button = terminal.read()
        if button == terminal.TK_1 and number_of_inputs > 0:
            return 0
        elif button == terminal.TK_2 and number_of_inputs > 1:
            return 1
        elif button == terminal.TK_3 and number_of_inputs > 2:
            return 2
        elif button == terminal.TK_4 and number_of_inputs > 3:
            return 3
        elif button == terminal.TK_5 and number_of_inputs > 4:
            return 4
        elif button == terminal.TK_6 and number_of_inputs > 5:
            return 5
        elif button == terminal.TK_7 and number_of_inputs > 6:
            return 6
        elif button == terminal.TK_ENTER and is_enter_used:
            return terminal.TK_ENTER
        elif button == terminal.TK_BACKSPACE and is_backspace_used:
            return terminal.TK_BACKSPACE
