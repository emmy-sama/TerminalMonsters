import json


def get_pokedex():
    with open("Data/Pokedex.json") as pokedex_json:
        return json.load(pokedex_json)


def get_natures():
    with open("Data/natures.json") as natures_json:
        return json.load(natures_json)


def get_moves():
    with open("Data/Moves.json") as moves_json:
        return json.load(moves_json)


def get_learn_sets():
    with open("Data/LearnSets.json") as learn_sets_json:
        return json.load(learn_sets_json)


def get_type_effectiveness():
    with open("Data/TypeEffectiveness.json") as effectiveness_json:
        return json.load(effectiveness_json)


def get_encounter_tables():
    with open("Data/Encounter_Table.json") as encounter_table_json:
        return json.load(encounter_table_json)


def get_league_data(league):
    with open(f"Data/{league}_League.json") as league_data:
        return json.load(league_data)
