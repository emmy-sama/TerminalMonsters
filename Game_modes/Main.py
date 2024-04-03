from Battle_Engine.BattleSystem import *
from Classes import Ai, Player, Pokemon
from Helpers import get_input, print_txt
from Data_Builders import get_league_data, get_encounter_tables

pokedex = get_pokedex()


class Main:
    def __init__(self):
        self.player = Player()
        self.starter_type = None
        self.encounter_tables = get_encounter_tables()

    def game_play(self):
        print_txt("What is your rival's name?: ", 0)
        rival = terminal.read_str(29, 20, "", 12)[1]
        terminal.clear()
        self.choose_starter()
        league_data = get_league_data("Hoenn")
        for trainer_battle in league_data:
            if trainer_battle.get("encounter_name") == "Legendary":
                print_txt(f"You have become champion and your journey has come to a end!...")
                self.print_exp(trainer_battle.get("level_up_amount"))
                self.poke_center()
                terminal.clear()
                legendary = random.choice(self.encounter_tables.get("Legendary"))
                legendary_trainer = Ai("", [Pokemon(legendary, "", 75)])
                Battle(self.player, self.select_lead(), legendary_trainer).battle()
                self.catch_legendary(legendary)
            else:
                for encounter in range(0, trainer_battle.get("amount_of_encounters")):
                    self.catch_pokemon(trainer_battle.get("encounter_lvl"))
                self.print_exp(trainer_battle.get("level_up_amount"))
                self.poke_center()
                print_txt(trainer_battle.get("text").format(name=rival))
                terminal.clear()
                opponenet = Ai(trainer_battle.get("encounter_name").format(name=rival), [])
                opponenet.team = [Pokemon(pokemon.get("species"), opponenet, custom_data=pokemon)
                                  for pokemon in trainer_battle.get("team")]
                Battle(self.player, self.select_lead(), opponenet).battle()
        print_txt(f"Thank you for playing you have finished the game as it is now!")
        terminal.clear()

    def choose_starter(self):
        terminal.printf(29, 7, "What starter would you like?")
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(10, 16, "1 Bulbasaur")
        terminal.put(14, 12, 0xE305)
        terminal.printf(27, 16, "2 Charmander")
        terminal.put(31, 12, 0xE30B)
        terminal.printf(48, 16, "3 Squirtle")
        terminal.put(52, 12, 0xE311)
        terminal.printf(69, 16, "4 Random")
        terminal.put(73, 12, 0xF8FB)
        terminal.refresh()
        i = get_input(4)
        if i == 0:
            player_starter = Pokemon("Bulbasaur", self.player, 5)
        elif i == 1:
            player_starter = Pokemon("Charmander", self.player, 5)
        elif i == 2:
            player_starter = Pokemon("Squirtle", self.player, 5)
        else:
            random_starter = random.choice(list(pokedex.keys()))
            player_starter = Pokemon(random_starter, self.player, 5)
        terminal.clear()
        self.starter_type = player_starter.type_one
        self.player.team.append(player_starter)

    def print_exp(self, lvl, txt=None):
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        if txt is None:
            terminal.printf(20, 6, f"You take time to level your pokemon to level {lvl}.")
        else:
            terminal.printf(20, 6, txt)
        terminal.refresh()
        time.sleep(2)
        terminal.clear()
        for mons in self.player.team:
            mons.level_up(lvl)

    def print_player_pokemon(self):
        x = 4
        x2 = 14
        y = 14
        y2 = 9
        i = 0
        for mon in self.player.team:
            i += 1
            terminal.printf(x, y, f"{i} {mon}")
            terminal.put(x2, y2, int(mon.front_sprite, 16))
            x += 28
            x2 += 28
            if x > 60:
                x = 4
                x2 = 14
                y = 24
                y2 = 19

    def poke_center(self):
        for mons in self.player.team:
            mons.chp = mons.hp
            mons.status = ""

    def catch_pokemon(self, lvl):
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(22, 1, "What type of route would you like to go to?")
        terminal.printf(9, 5, "1 Normal")
        terminal.put(13, 10, 0xF8FA)
        terminal.printf(37, 5, "2 Forest")
        terminal.put(41, 10, 0xF8F9)
        terminal.printf(69, 5, "3 Cave")
        terminal.put(73, 10, 0xF8F8)
        terminal.printf(9, 15, "4 Water")
        terminal.put(13, 20, 0xF8F7)
        terminal.printf(37, 15, "5 City")
        terminal.put(41, 20, 0xF8F6)
        terminal.printf(69, 15, "6 Night")
        terminal.put(73, 20, 0xF8F5)
        terminal.refresh()
        route = get_input(6)
        if route == 0:
            route = "Normal"
        elif route == 1:
            route = "Forest"
        elif route == 2:
            route = "Cave"
        elif route == 3:
            route = "Water"
        elif route == 4:
            route = "City"
        elif route == 5:
            route = "Night"
        mon_1 = pokedex.get(random.choice(self.encounter_tables.get(route).get(lvl)))
        mon_2 = pokedex.get(random.choice(self.encounter_tables.get(route).get(lvl)))
        mon_3 = pokedex.get(random.choice(self.encounter_tables.get(route).get(lvl)))
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(22, 6, "What pokemon would you like to try and catch?")
        terminal.printf(9, 18, f"1 {mon_1.get("Species")}")
        terminal.put(14, 12, int(random.choice(
            [hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1.get("dex_number")) + 58116),
             hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1.get("dex_number")) + 58117)]), 16))
        terminal.printf(37, 18, f"2 {mon_2.get("Species")}")
        terminal.put(42, 12, int(random.choice(
            [hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2.get("dex_number")) + 58116),
             hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2.get("dex_number")) + 58117)]), 16))
        terminal.printf(69, 18, f"3 {mon_3.get("Species")}")
        terminal.put(74, 12, int(random.choice(
            [hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3.get("dex_number")) + 58116),
             hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3.get("dex_number")) + 58117)]), 16))
        terminal.printf(37, 21, "4 Pass")
        terminal.refresh()
        i = get_input(4)
        if i == 0:
            choice = mon_1
        elif i == 1:
            choice = mon_2
        elif i == 2:
            choice = mon_3
        else:
            choice = None
        if len(self.player.team) == 6 and choice is not None:
            terminal.clear()
            terminal.put(0, 0, 0xF8FC)
            terminal.printf(13, 1, f"Would you like to replace one of your pokemon with {choice.get("Species")}")
            terminal.printf(32, 3, f"7 give up {choice.get("Species")}")
            self.print_player_pokemon()
            terminal.refresh()
            i = get_input(7)
            if i == 6:
                pass
            else:
                self.player.team.pop(i)
                self.player.team.insert(i, Pokemon(choice.get("Species"), self.player))
        elif choice is not None:
            self.player.team.append(Pokemon(choice.get("Species"), self.player))

    def select_lead(self):
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(22, 1, "What pokemon would you like to lead?")
        self.print_player_pokemon()
        terminal.refresh()
        slot = get_input(len(self.player.team))
        terminal.clear()
        return self.player.team[slot]

    def catch_legendary(self, legendary):
        if len(self.player.team) == 6:
            terminal.clear()
            terminal.put(0, 0, 0xF8FC)
            terminal.printf(13, 1, f"Would you like to replace one of your pokemon with {legendary.species}")
            terminal.printf(32, 3, f"7 give up {legendary.specics}")
            self.print_player_pokemon()
            terminal.refresh()
            i = get_input(7)
            if i == 6:
                pass
            else:
                self.player.team.pop(i)
                self.player.team.insert(i, Pokemon(legendary, self.player, 77))
        else:
            self.player.team.append(Pokemon(legendary, self.player, 77))
