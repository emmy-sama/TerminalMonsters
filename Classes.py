from BattleSystem import *
import random
import math
import json
with open("Data/Pokedex.json") as pokedex_json:
    pokedex = json.load(pokedex_json)
with open("Data/natures.json") as natures_json:
    natures = json.load(natures_json)
with open("Data/Moves.json") as moves_json:
    moves = json.load(moves_json)
with open("Data/TypeEffectiveness.json") as effectiveness_json:
    types = json.load(effectiveness_json)
with open("Data/LearnSets.json") as learn_sets_json:
    learn_sets = json.load(learn_sets_json)


class Player:
    def __init__(self, name, pronouns, starter, team):
        self.name = name
        self.pronouns = pronouns
        self.starter = starter
        self.team = team


class Pokemon:
    def __init__(self, species, owner, level=5):
        self.owner = owner
        self.level = level
        for p in pokedex:
            if p["Species"] == species:
                self.species = p.get("Species")
                self.index = pokedex.index(p)
                break
        self.type_one = pokedex[self.index].get("types")[0]
        if len(pokedex[self.index].get("types")) == 2:
            self.type_two = pokedex[self.index].get("types")[1]
        else:
            self.type_two = None
        self.ability = random.choice(pokedex[self.index].get("Abilities"))
        self.get_gender(pokedex[self.index].get("Gender Ratio"))
        self.catch_rate = pokedex[self.index].get("Catch rate")
        self.height = pokedex[self.index].get("Height")
        self.weight = pokedex[self.index].get("Weight")
        self.nature = natures[random.randint(0, 24)]
        self.calc_stats()
        self.total_exp = pow(self.level, 3)
        self.exp_needed = pow(self.level + 1, 3)
        self.evolvl = pokedex[self.index].get("EvoLvl", None)
        self.evo = pokedex[self.index].get("Evo", None)
        self.moves = self.get_move_set()
        self.chp = self.hp
        self.burned = False
        self.temp_stats = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0, "accuracy": 0, "evasion": 0}

    def get_gender(self, percent):
        rnum = random.uniform(0.0, 1.0)
        if rnum <= percent:
            self.gender = "Male"
        else:
            self.gender = "Female"

    def get_move_set(self):
        ms = []
        ls = learn_sets.get(str(self.species).lower())
        for level in ls.get("level"):
            if int(level) <= self.level:
                if len(ms) >= 4:
                    ms.insert(0, ls.get("level").get(level).title())
                else:
                    ms.append(ls.get("level").get(level).title())
        return ms


    def calc_stats(self):
        self.hp = math.floor(0.01 * ((2 * pokedex[self.index].get("bHP")) * self.level)) + self.level + 10
        self.attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bAttack")) * self.level)) + 5)
                                 * self.nature.get("Attack", 1))
        self.defense = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bDefense")) * self.level)) + 5)
                                  * self.nature.get("Defense", 1))
        self.sp_attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Attack")) * self.level)) + 5)
                                    * self.nature.get("Sp.Attack", 1))
        self.sp_defense = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Defense")) * self.level)) + 5)
                                     * self.nature.get("Sp.Defense", 1))
        self.speed = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSpeed")) * self.level)) + 5)
                                * self.nature.get("Speed", 1))

    def reset_temp(self):
        self.temp_stats = self.temp_stats.fromkeys(self.temp_stats.keys(), 0)

    def evolve(self):
        self.index = self.evo
        self.species = pokedex[self.index].get("Species")
        self.type_one = pokedex[self.index].get("Typeone")
        self.type_two = pokedex[self.index].get("Typetwo")
        self.ability = random.choice(pokedex[self.index].get("Abilities"))
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
        print(f"{self.species} {self.gender} Level: {self.level} Hp: {self.chp}/{self.hp} Ability: {self.ability} \n"
              f"{self.nature.get("Name")} Attack: {self.attack} Defense: {self.defense} Sp.Attack: {self.sp_attack} "
              f"Sp.Defense: {self.sp_defense} Speed: {self.speed}")

    def check_poke_moves(self):
        for m in self.moves:
            for move in moves:
                if m == move.get("name"):
                    print(f"{move.get("name")}:", f"{move.get("type")} Type,", f"{move.get("category")},",
                          f"Power: {move.get("power")}", f"Accuracy: {move.get("accuracy")}", f"PP: {move.get("pp")}")
                    break


ash = Player("Ash", "they/them", 0, [])
Testmon = Pokemon("Testmon", ash)
pika = Pokemon("Pikachu", ash)
ash.team.append(Testmon)
ash.team.append(pika)

garry = Player("Garry", "they/them", 0, [])
Squirtle = Pokemon("Squirtle", garry)
Charmander = Pokemon("Charmander", garry)
garry.team.append(Squirtle)
garry.team.append(Charmander)

ash_v_gary = Battle(ash, garry, moves, types)
ash_v_gary.battle()
