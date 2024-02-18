from Pokemons import pokedex
import random
import math


def gender(percent):
    rnum = random.uniform(0.0, 1.0)
    if rnum <= percent:
        return "Male"
    else:
        return "Female"


def ability_assign(index):
    return random.choice(pokedex[index].get("Abilities"))


class Player:
    def __init__(self, name, pronouns, starter, team):
        self.name = name
        self.pronouns = pronouns
        self.starter = starter
        self.team = team


class Pokemon:
    def calc_stats(self):
        self.hp = math.floor(0.01 * ((2 * pokedex[self.index].get("bHP")) * self.level)) + self.level + 10
        self.attack = math.floor(0.01 * ((2 * pokedex[self.index].get("bAttack")) * self.level)) + 5
        self.defense = math.floor(0.01 * ((2 * pokedex[self.index].get("bDefense")) * self.level)) + 5
        self.sp_attack = math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Attack")) * self.level)) + 5
        self.sp_defense = math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Defense")) * self.level)) + 5
        self.speed = math.floor(0.01 * ((2 * pokedex[self.index].get("bSpeed")) * self.level)) + 5

    def __init__(self, index, owner, level=1):
        self.owner = owner
        self.level = level
        self.index = index
        self.species = pokedex[index].get("Species")
        self.type_one = pokedex[index].get("Typeone")
        self.type_two = pokedex[index].get("Typetwo")
        self.ability = ability_assign(index)
        self.gender = gender(pokedex[index].get("Gender Ratio"))
        self.catch_rate = pokedex[index].get("Catch rate")
        self.height = pokedex[index].get("Height")
        self.weight = pokedex[index].get("Weight")
        self.calc_stats()

    def get_stats(self):
        print(self.hp, self.attack, self.defense, self.sp_attack, self.sp_defense, self.speed)


bulb = Pokemon(0, "player")


print(bulb.gender)
print(bulb.ability)
bulb.get_stats()
