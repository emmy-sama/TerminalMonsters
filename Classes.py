from Pokemons import *
import random
import math


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
    def ability_assign(self, index):
        self.ability = random.choice(pokedex[index].get("Abilities"))

    def calc_stats(self):
        self.hp = math.floor(0.01 * ((2 * pokedex[self.index].get("bHP")) * self.level)) + self.level + 10
        self.attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bAttack")) * self.level)) + 5)
                                 * natures[self.nature].get("Attack", 1))
        self.defense = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bDefense")) * self.level)) + 5)
                                  * natures[self.nature].get("Defense", 1))
        self.sp_attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Attack")) * self.level)) + 5)
                                    * natures[self.nature].get("Sp.Attack", 1))
        self.sp_defense = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Defense")) * self.level)) + 5)
                                     * natures[self.nature].get("Sp.Defense", 1))
        self.speed = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSpeed")) * self.level)) + 5)
                                * natures[self.nature].get("Speed", 1))

    def __init__(self, index, owner, level=5):
        self.owner = owner
        self.level = level
        self.index = index
        self.species = pokedex[index].get("Species")
        self.type_one = pokedex[index].get("Typeone")
        self.type_two = pokedex[index].get("Typetwo")
        self.ability_assign(index)
        self.gender = gender(pokedex[index].get("Gender Ratio"))
        self.catch_rate = pokedex[index].get("Catch rate")
        self.height = pokedex[index].get("Height")
        self.weight = pokedex[index].get("Weight")
        self.nature = random.randint(0, 24)
        self.calc_stats()
        self.total_exp = pow(self.level, 3)
        self.exp_needed = pow(self.level + 1, 3)
        self.evolvl = pokedex[index].get("EvoLvl", None)
        self.evo = pokedex[index].get("Evo", None)
        self.chp = self.hp
        self.burn = False
        self.moves = ["Tackle"]

    def evolve(self):
        self.index = self.evo
        self.species = pokedex[self.index].get("Species")
        self.type_one = pokedex[self.index].get("Typeone")
        self.type_two = pokedex[self.index].get("Typetwo")
        self.ability_assign(self.index)
        self.height = pokedex[self.index].get("Height")
        self.weight = pokedex[self.index].get("Weight")
        self.calc_stats()
        self.evolvl = pokedex[self.index].get("EvoLvl", None)
        self.evo = pokedex[self.index].get("Evo", None)

    def getexp(self, amount):
        self.total_exp += amount
        while self.total_exp >= self.exp_needed:
            self.level += 1
            self.calc_stats()
            self.exp_needed = pow(self.level + 1, 3)
            if self.level >= self.evolvl:
                self.evolve()

    def check_poke_basic(self):
        print(self.species, self.gender, f"Level: {self.level}", f"Hp: {self.chp}/{self.hp}")

    def check_poke_advanced(self):
        print(self.species, self.gender, f"Level: {self.level}", f"Hp: {self.chp}/{self.hp}",
              f" Ability: {self.ability}", "\n", f"Attack: {self.attack}", f"Defense: {self.defense}",
              f"Sp.Attack: {self.sp_attack}", f"Sp.Defense: {self.sp_defense}", f"Speed: {self.speed}",)

    def check_poke_moves(self):
        for m in self.moves:
            print(f"{moves.get(m).get("Name")}:", f"{moves.get(m).get("Type")} Type,", f"{moves.get(m).get("DmgType")} Damage,",
                  f"Power: {moves.get(m).get("Dmg")}", f"Accuracy: {moves.get(m).get("Acc")}", f"PP: {moves.get(m).get("PP")}"
            )



