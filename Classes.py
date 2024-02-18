from Pokemons import pokedex
import random

def gender(percent):
    rnum = random.uniform(0.0, 1.0)
    if rnum <= percent:
        return "Male"
    else:
        return "Female"
class Player:
    def __init__(self, name, pronouns, starter, team):
        self.name = name
        self.pronouns = pronouns
        self.starter = starter
        self.team = team


class Pokemon:
    def __init__(self, species, owner, level=1):
        self.owner = owner
        self.level = level
        self.species = pokedex[species].get("Species")
        self.type_one = pokedex[species].get("Typeone")
        self.type_two = pokedex[species].get("Typetwo")
        # Make pick one
        self.ability = pokedex[species].get("Abilities")
        self.gender = gender(pokedex[species].get("Gender Ratio"))
        self.catch_rate = pokedex[species].get("Catch rate")
        self.height = pokedex[species].get("Height")
        self.weight = pokedex[species].get("Weight")
        self.hp = pokedex[species].get("bHP")
        self.attack = pokedex[species].get("bAttack")
        self.defense = pokedex[species].get("bDefense")
        self.sp_attack = pokedex[species].get("bSp.Attack")
        self.sp_defense = pokedex[species].get("bSp.Defense")
        self.speed = pokedex[species].get("bSpeed")


bulb = Pokemon(0, "player")


print(bulb.gender)

