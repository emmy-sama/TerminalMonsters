import random
import math
import json
from bearlibterminal import terminal
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


class Player:
    def __init__(self, name, team, starter_type=None):
        self.name = name
        self.starter_type = starter_type
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
        self.front_sprite = pokedex[self.index].get("Front Sprite")
        self.back_sprite = pokedex[self.index].get("Back Sprite")
        self.ability = random.choice(pokedex[self.index].get("Abilities"))
        self.get_gender(pokedex[self.index].get("Gender Ratio"))
        self.catch_rate = pokedex[self.index].get("Catch rate")
        self.height = pokedex[self.index].get("Height")
        self.weight = pokedex[self.index].get("Weight")
        self.nature = natures[random.randint(0, 24)]
        self.hidden_type = self.get_hidden_type()
        self.hp = math.floor(0.01 * ((2 * pokedex[self.index].get("bHP")) * self.level)) + self.level + 10
        self.attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bAttack")) * self.level)) + 5)
                                 * self.nature.get("Attack", 1))
        self.defense = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bDefense")) * self.level)) + 5)
                                  * self.nature.get("Defense", 1))
        self.sp_attack = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Attack")) * self.level)) + 5)
                                    * self.nature.get("Sp.Attack", 1))
        self.sp_defense = math.floor(
            (math.floor(0.01 * ((2 * pokedex[self.index].get("bSp.Defense")) * self.level)) + 5)
            * self.nature.get("Sp.Defense", 1))
        self.speed = math.floor((math.floor(0.01 * ((2 * pokedex[self.index].get("bSpeed")) * self.level)) + 5)
                                * self.nature.get("Speed", 1))
        self.evolvl = pokedex[self.index].get("EvoLvl", None)
        self.evo = pokedex[self.index].get("Evo", None)
        self.moves = self.get_move_set()
        self.chp = self.hp
        self.status = ""
        self.confused = False
        self.flinching = False
        self.temp_stats = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0, "accuracy": 0,
                           "evasion": 0}
        self.charge = False
        self.stockpile = 0
        self.semi_invulnerable = None
        self.minimized = False
        self.damaged_this_turn = False
        self.getting_pumped = False
        self.recharge = False
        self.charged = False
        self.first_turn = True
        self.acted = False
        self.bide = 0
        self.outraging = 0
        self.rage = False
        self.bide_dmg = 0
        self.uproar = 0
        self.trapping = [0, ""]
        self.rolling = 0
        self.rolling_hit = False
        self.fury_cutter = 0
        self.fury_cutter_hit = False
        self.dmg_last_type_taken = None
        self.dmg_last_taken = 0
        self.info = (f"{self.gender} {self.nature.get("Name")} Attack: {self.attack} Defense: {self.defense} "
                     f"Sp.Attack: {self.sp_attack} Sp.Defense: {self.sp_defense} Speed: {self.speed}")

    def __str__(self):
        return f"Lv{self.level} {self.species}{self.gender} : {self.chp}/{self.hp} {self.status}"

    def get_gender(self, percent):
        rnum = random.uniform(0.0, 1.0)
        if rnum <= percent:
            self.gender = "♂"
        else:
            self.gender = "♀"

    def get_move_set(self):
        ms = []
        ls = learn_sets.get(str(self.species).lower())
        for level in ls.get("level"):
            if int(level) <= self.level:
                if len(ms) >= 4:
                    ms.pop(0)
                    ms.insert(0, ls.get("level").get(level).title())
                else:
                    ms.append(ls.get("level").get(level).title())
        return ms

    def get_hidden_type(self):
        options = [["Fighting", "Physical"], ["Flying", "Physical"], ["Poison", "Physical"], ["Ground", "Physical"],
                   ["Rock", "Physical"], ["Bug", "Physical"], ["Ghost", "Physical"], ["Steel", "Physical"],
                   ["Fire", "Special"], ["Water", "Special"] ,["Grass", "Special"], ["Electric", "Special"],
                   ["Psychic", "Special"] ,["Ice", "Special"] ,["Dragon", "Special"] ,["Dark", "Special"]]
        return random.choices(options, weights=[7.8125, 6.25, 6.25, 6.25, 6.25, 7.8125, 6.25, 6.25, 6.25, 6.25, 7.8125,
                                                6.25, 6.25, 6.25, 6.25, 1.5625], k=1)[0]

    def calc_stats(self):
        self.chp += (math.floor(0.01 * ((2 * pokedex[self.index].get("bHP")) * self.level)) + self.level + 10) - self.hp
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
        self.fury_cutter = 0
        self.rolling = 0

    def learn_move(self):
        move = learn_sets.get(self.species.lower()).get("level").get(str(self.level))
        if move is not None:
            terminal.clear()
            if len(self.moves) == 4:
                terminal.printf(10, 10, f"{self.species} wants to learn {move}, replace a move?")
                terminal.printf(10, 11, f"1 {self.moves[0]}")
                terminal.printf(10, 12, f"2 {self.moves[1]}")
                terminal.printf(10, 13, f"3 {self.moves[2]}")
                terminal.printf(10, 14, f"4 {self.moves[3]}")
                terminal.printf(10, 15, "5 Keep old moves")
                terminal.refresh()
                while True:
                    button = terminal.read()
                    if button == terminal.TK_1:
                        self.moves.pop(0)
                        self.moves.insert(0, move)
                        terminal.clear()
                        terminal.printf(10, 10, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_2:
                        self.moves.pop(1)
                        self.moves.insert(1, move)
                        terminal.clear()
                        terminal.printf(10, 10, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_3:
                        self.moves.pop(2)
                        self.moves.insert(2, move)
                        terminal.clear()
                        terminal.printf(10, 10, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_4:
                        self.moves.pop(3)
                        self.moves.insert(3, move)
                        terminal.clear()
                        terminal.printf(10, 10, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    elif button == terminal.TK_5:
                        terminal.clear()
                        terminal.printf(10, 10, f"{self.species} kept its old moves")
                        terminal.refresh()
                        break
            else:
                self.moves.append(move)
                terminal.clear()
                terminal.printf(10, 10, f"{self.species} learned {move}")
                terminal.refresh()


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

    def level_up(self, level):
        while self.level != level:
            self.level += 1
            self.calc_stats()
            self.learn_move()
            if self.evolvl is not None:
                if self.level >= self.evolvl:
                    self.evolve()
                    self.learn_move()
