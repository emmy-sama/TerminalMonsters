from Helpers import setup_bearlib, get_input, print_txt
from Game_modes import testing_battle, Main
import json

with open("Data/Pokedex.json") as pokedex_json:
    pokedex = json.load(pokedex_json)
with open("Data/natures.json") as natures_json:
    natures = json.load(natures_json)
with open("Data/Moves.json") as moves_json:
    moves = json.load(moves_json)
with open("Data/LearnSets.json") as learn_sets_json:
    learn_sets = json.load(learn_sets_json)
with open("Data/TypeEffectiveness.json") as effectiveness_json:
    types = json.load(effectiveness_json)
with open("Data/Encounter_Table.json") as encounter_table_json:
    encounters = json.load(encounter_table_json)

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

