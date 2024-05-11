import json


# Convert data files into dictionary variables
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
    encounter_tables = json.load(encounter_table_json)
