import math
import random
import time
from bearlibterminal import terminal
from Data_Builders import pokedex, natures, learn_sets


class Pokemon:
    def __init__(self, species, owner, level=5, custom_data=None):
        self.owner = owner
        dex_entry = pokedex.get(species)
        self.species = species
        self.dex_number = dex_entry.get("dex_number")
        if custom_data:
            self.level = custom_data.get("level")
            self.ability = self.ability_og = custom_data.get("ability")
            self.held_item = custom_data.get("held_item")
            self.nature = natures[random.randint(0, 24)]
            self.hidden_type = custom_data.get("hidden_type", self.get_hidden_type())
            # move set
        else:
            self.level = level
            self.ability = self.ability_og = random.choice(dex_entry.get("Abilities"))
            self.held_item = ""
            self.nature = natures[random.randint(0, 24)]
            self.hidden_type = self.get_hidden_type()
        self.gender = self.get_gender(dex_entry.get("Gender Ratio"))
        self.front_sprite = random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 58116),
                                           hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 58117)])
        self.back_sprite = random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 57344),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 57345)])
        self.type_one = dex_entry.get("types")[0]
        self.type_one_og = self.type_one
        if len(dex_entry.get("types")) == 2:
            self.type_two = dex_entry.get("types")[1]
            self.type_two_og = self.type_two
        else:
            self.type_two = None
            self.type_two_og = None
        self.catch_rate = dex_entry.get("Catch rate")
        self.height = dex_entry.get("Height")
        self.weight = dex_entry.get("Weight")
        self.bHp = dex_entry.get("bHP")
        self.bAttack = dex_entry.get("bAttack")
        self.bDefense = dex_entry.get("bDefense")
        self.bSp_attack = dex_entry.get("bSp.Attack")
        self.bSp_defense = dex_entry.get("bSp.Defense")
        self.bSpeed = dex_entry.get("bSpeed")
        self.calc_stats()
        self.evolvl = dex_entry.get("evo_level", None)
        self.stone = dex_entry.get("Stone", None)
        self.evo = dex_entry.get("evos", None)
        self.moves = self.get_move_set()
        self.status = ""
        self.tox_turns = 0
        self.sleep_turns = 0
        self.confused = False
        self.flinching = False
        self.temp_stats = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0, "accuracy": 0,
                           "evasion": 0}
        self.charge = False
        self.loafing = False
        self.stockpile = 0
        self.semi_invulnerable = None
        self.minimized = False
        self.damaged_this_turn = False
        self.getting_pumped = False
        self.recharge = False
        self.charged = False
        self.first_turn = True
        self.acted = False
        self.flash_fired = False
        self.bide = 0
        self.outraging = 0
        self.rage = False
        self.bide_dmg = 0
        self.uproar = 0
        self.bonded = False
        self.rooted = False
        self.reflecting = False
        self.trapping = [0, ""]
        self.rolling = 0
        self.rolling_hit = False
        self.fury_cutter = 0
        self.fury_cutter_hit = False
        self.blocking = False
        self.water_sport = False
        self.mud_sport = False
        self.cursed = False
        self.protecting = False
        self.protecting_chance = 1
        self.enduring = False
        self.dmg_last_type_taken = None
        self.dmg_last_taken = 0
        self.info = (f"{self.gender} {self.nature.get("Name")} Attack: {self.attack} Defense: {self.defense} "
                     f"Sp.Attack: {self.sp_attack} Sp.Defense: {self.sp_defense} Speed: {self.speed}")

    def __str__(self):
        return f"Lv{self.level} {self.species}{self.gender} : {self.chp}/{self.hp} {self.status}"

    def get_gender(self, percent):
        rnum = random.uniform(0.0, 1.0)
        if rnum <= percent:
            return "♂"
        else:
            return "♀"

    def get_move_set(self):
        ms = []
        ls = learn_sets.get(str(self.species).lower())
        for level in ls.get("level"):
            if int(level) <= self.level and ls.get("level").get(level).title() not in ms:
                if len(ms) >= 4:
                    ms.pop(0)
                    ms.insert(0, ls.get("level").get(level).title())
                else:
                    ms.append(ls.get("level").get(level).title())
        return ms

    def get_hidden_type(self):
        options = [["Fighting", "Physical"], ["Flying", "Physical"], ["Poison", "Physical"], ["Ground", "Physical"],
                   ["Rock", "Physical"], ["Bug", "Physical"], ["Ghost", "Physical"], ["Steel", "Physical"],
                   ["Fire", "Special"], ["Water", "Special"], ["Grass", "Special"], ["Electric", "Special"],
                   ["Psychic", "Special"], ["Ice", "Special"], ["Dragon", "Special"], ["Dark", "Special"]]
        return random.choices(options, weights=[7.8125, 6.25, 6.25, 6.25, 6.25, 7.8125, 6.25, 6.25, 6.25, 6.25, 7.8125,
                                                6.25, 6.25, 6.25, 6.25, 1.5625], k=1)[0]

    def calc_stats(self):
        self.hp = math.floor(0.01 * ((2 * self.bHp) * self.level)) + self.level + 10
        self.chp = self.hp
        self.attack = math.floor((math.floor(0.01 * ((2 * self.bAttack) * self.level)) + 5)
                                 * self.nature.get("Attack", 1))
        self.defense = math.floor((math.floor(0.01 * ((2 * self.bDefense) * self.level)) + 5)
                                  * self.nature.get("Defense", 1))
        self.sp_attack = math.floor((math.floor(0.01 * ((2 * self.bSp_attack) * self.level)) + 5)
                                    * self.nature.get("Sp.Attack", 1))
        self.sp_defense = math.floor((math.floor(0.01 * ((2 * self.bSp_defense) * self.level)) + 5)
                                     * self.nature.get("Sp.Defense", 1))
        self.speed = math.floor((math.floor(0.01 * ((2 * self.bSpeed) * self.level)) + 5)
                                * self.nature.get("Speed", 1))

    def reset_temp(self):
        # Stat Changes
        self.temp_stats = self.temp_stats.fromkeys(self.temp_stats.keys(), 0)
        self.getting_pumped = False
        self.ability = self.ability_og
        self.type_one = self.type_one_og
        self.type_two = self.type_two_og
        # Status
        self.tox_turns = 0
        self.confused = False
        self.cursed = False
        self.flinching = False
        # Moves
        self.fury_cutter = 0
        self.fury_cutter_hit = False
        self.rolling = 0
        self.rolling_hit = False
        self.blocking = False
        self.water_sport = False
        self.mud_sport = False
        self.protecting = False
        self.enduring = False
        self.protecting_chance = 1
        self.bonded = False
        self.rooted = False
        self.reflecting = False
        # Abilities
        self.flash_fired = False
        # Battle Effects
        self.first_turn = True
        self.acted = False
        self.damaged_this_turn = False
        self.dmg_last_type_taken = None
        self.dmg_last_taken = 0

    def learn_move(self):
        move = learn_sets.get(self.species.lower()).get("level").get(str(self.level))
        if move is not None and move not in self.moves:
            terminal.clear()
            if len(self.moves) == 4:
                terminal.put(0, 0, 0xF8FC)
                terminal.printf(20, 6, f"{self.species} wants to learn {move}, replace a move?")
                terminal.printf(20, 7, f"1 {self.moves[0]}")
                terminal.printf(20, 8, f"2 {self.moves[1]}")
                terminal.printf(20, 9, f"3 {self.moves[2]}")
                terminal.printf(20, 10, f"4 {self.moves[3]}")
                terminal.printf(20, 11, "5 Keep old moves")
                terminal.refresh()
                while True:
                    button = terminal.read()
                    if button == terminal.TK_1:
                        self.moves.pop(0)
                        self.moves.insert(0, move)
                        terminal.clear()
                        terminal.put(0, 0, 0xF8FC)
                        terminal.printf(20, 6, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_2:
                        self.moves.pop(1)
                        self.moves.insert(1, move)
                        terminal.clear()
                        terminal.put(0, 0, 0xF8FC)
                        terminal.printf(20, 6, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_3:
                        self.moves.pop(2)
                        self.moves.insert(2, move)
                        terminal.clear()
                        terminal.put(0, 0, 0xF8FC)
                        terminal.printf(20, 6, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    if button == terminal.TK_4:
                        self.moves.pop(3)
                        self.moves.insert(3, move)
                        terminal.clear()
                        terminal.put(0, 0, 0xF8FC)
                        terminal.printf(20, 6, f"{self.species} learned {move}")
                        terminal.refresh()
                        break
                    elif button == terminal.TK_5:
                        terminal.clear()
                        terminal.put(0, 0, 0xF8FC)
                        terminal.printf(20, 6, f"{self.species} kept its old moves")
                        terminal.refresh()
                        break
                time.sleep(1.5)
            else:
                self.moves.append(move)
                terminal.clear()
                terminal.put(0, 0, 0xF8FC)
                terminal.printf(20, 6, f"{self.species} learned {move}")
                terminal.refresh()
                time.sleep(1.5)

    def evolve(self, species):
        dex_entry = pokedex.get(species)
        self.species = dex_entry.get("Species")
        self.dex_number = dex_entry.get("dex_number")
        self.front_sprite = random.choice(
            [hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 58116),
             hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 58117)])
        self.back_sprite = random.choice(
            [hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 57344),
             hex(list(map(lambda x: x // 2, range(1, 774))).index(self.dex_number) + 57345)])
        self.type_one = dex_entry.get("types")[0]
        self.type_one_og = self.type_one
        if len(dex_entry.get("types")) == 2:
            self.type_two = dex_entry.get("types")[1]
            self.type_two_og = self.type_two
        else:
            self.type_two = None
            self.type_two_og = None
        self.ability = random.choice(dex_entry.get("Abilities"))
        self.ability_og = self.ability
        self.height = dex_entry.get("Height")
        self.weight = dex_entry.get("Weight")
        self.evolvl = dex_entry.get("evo_level", None)
        self.stone = dex_entry.get("Stone", None)
        self.evo = dex_entry.get("evos", None)
        self.bHp = dex_entry.get("bHP")
        self.bAttack = dex_entry.get("bAttack")
        self.bDefense = dex_entry.get("bDefense")
        self.bSp_attack = dex_entry.get("bSp.Attack")
        self.bSp_defense = dex_entry.get("bSp.Defense")
        self.bSpeed = dex_entry.get("bSpeed")
        self.calc_stats()
        self.info = (f"{self.gender} {self.nature.get("Name")} Attack: {self.attack} Defense: {self.defense} "
                     f"Sp.Attack: {self.sp_attack} Sp.Defense: {self.sp_defense} Speed: {self.speed}")

    def level_up(self, level):
        while self.level != level:
            self.level += 1
            self.calc_stats()
            self.learn_move()
            self.info = (f"{self.gender} {self.nature.get("Name")} Attack: {self.attack} Defense: {self.defense} "
                         f"Sp.Attack: {self.sp_attack} Sp.Defense: {self.sp_defense} Speed: {self.speed}")
            if self.evolvl is not None:
                if self.level >= self.evolvl:
                    terminal.clear()
                    terminal.put(0, 0, 0xF8FC)
                    terminal.printf(20, 6, f"{self.species} wants to evolve, should it?")
                    terminal.printf(20, 7, "(Enter) Yes")
                    terminal.printf(20, 8, "(BackSpace) No")
                    terminal.refresh()
                    while True:
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            if self.species == "Tyrogue":
                                self.evolve(self.evo[random.randint(0, 2)])
                            elif self.species == "Wurmple":
                                self.evolve(self.evo[random.randint(0, 1)])
                            # elif self.species == "Nincada":
                            else:
                                self.evolve(self.evo[0])
                            self.learn_move()
                            time.sleep(1.5)
                            break
                        elif button == terminal.TK_BACKSPACE:
                            break
