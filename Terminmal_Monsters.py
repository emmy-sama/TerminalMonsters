from Game_modes.Main import Main
from Game_modes.Testing_Battle import testing_battle
from Helpers import setup_bearlib, get_input, print_txt

print("Close me to close program")
setup_bearlib()

# Game modes
test = 0
hoenn = 1
seal = 2

while True:
    print_txt("What game mode would you like to play"
              "\n(1) Testing Battle"
              "\n(2) Hoenn"
              "\n(3) Seal", 0)
    game_mode = get_input(3)
    if game_mode == test:
        testing_battle()
    elif game_mode == hoenn:
        Main().game_play()
    elif game_mode == seal:
        print_txt("Not yet implemented.")
        pass

