from BattleSystem import *
from Classes import *

print("Close me to close program")
terminal.open()
terminal.set("window: size=88x25")
terminal.set("0xE001: data/BackSprites.png, size=333x333, align=center")
terminal.set("0xE305: data/FrontSprites.png, size=333x333, align=center")
terminal.set("0xF8FF: data/Background.png")
terminal.set("0xF8FD: data/Background2.png")
terminal.set("0xF8FC: data/BlankBackground.png")
terminal.set("0xF8FB: data/Random.png, align=center")
terminal.set("0x2640: data/Female_symbol.png, align=center")
terminal.set("0x2642: data/Male_symbol.png, align=center")
terminal.set("font: data/pokemon.ttf, size=16")

rival = "Gary"


def print_exp(lvl, txt=None):
    for mons in player.team:
        mons.level_up(lvl)
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    if txt is None:
        terminal.printf(20, 6, f"You take time to level your pokemon to level {lvl}.")
    else:
        terminal.printf(20, 6, txt)
    terminal.refresh()
    time.sleep(2)


def print_txt(txt):
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(10, 6, txt)
    terminal.refresh()
    time.sleep(2)

def poke_center():
    for mons in player.team:
        mons.chp = mons.hp


def catch_pokemon(lvl):
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(22, 6, "What type of route would you like to go to?")
    terminal.printf(9, 9, "1 Normal")
    terminal.printf(37, 9, "2 Forest")
    terminal.printf(69, 9, "3 Cave")
    terminal.printf(9, 18, "4 Water")
    terminal.printf(37, 18, "5 City")
    terminal.printf(69, 18, "6 Night")
    terminal.refresh()
    while True:
        button = terminal.read()
        if button == terminal.TK_1:
            route = "Normal"
            break
        elif button == terminal.TK_2:
            route = "Forest"
            break
        elif button == terminal.TK_3:
            route = "Cave"
            break
        elif button == terminal.TK_4:
            route = "Water"
            break
        elif button == terminal.TK_5:
            route = "City"
            break
        elif button == terminal.TK_6:
            route = "Night"
            break
        else:
            pass
    choice = None
    mon_1 = random.choice(encounters.get(route).get(lvl))
    for p in pokedex:
        if p.get("Species") == mon_1:
            mon_1 = p
    mon_2 = random.choice(encounters.get(route).get(lvl))
    for p in pokedex:
        if p.get("Species") == mon_2:
            mon_2 = p
    mon_3 = random.choice(encounters.get(route).get(lvl))
    for p in pokedex:
        if p.get("Species") == mon_3:
            mon_3 = p
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(22, 6, "What pokemon would you like to try and catch?")
    terminal.printf(9, 18, f"1 {mon_1.get("Species")}")
    terminal.put(14, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1.get("dex_number")) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1.get("dex_number")) + 58117)]), 16))
    terminal.printf(37, 18, f"2 {mon_2.get("Species")}")
    terminal.put(42, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2.get("dex_number")) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2.get("dex_number")) + 58117)]), 16))
    terminal.printf(69, 18, f"3 {mon_3.get("Species")}")
    terminal.put(74, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3.get("dex_number")) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3.get("dex_number")) + 58117)]), 16))
    terminal.printf(37, 21, "4 Pass")
    terminal.refresh()
    while True:
        button = terminal.read()
        if button == terminal.TK_1:
            choice = mon_1
            break
        elif button == terminal.TK_2:
            choice = mon_2
            break
        elif button == terminal.TK_3:
            choice = mon_3
            break
        elif button == terminal.TK_4:
            break
        else:
            pass
    if len(player.team) == 6 and choice is not None:
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(13, 1, f"Would you like to replace one of your pokemon with {choice.get("Species")}")
        terminal.printf(4, 14, f"1 {player.team[0]}")
        terminal.put(14, 9, int(player.team[0].front_sprite, 16))
        terminal.printf(32, 14, f"2 {player.team[1]}")
        terminal.put(42, 9, int(player.team[1].front_sprite, 16))
        terminal.printf(59, 14, f"3 {player.team[2]}")
        terminal.put(69, 9, int(player.team[2].front_sprite, 16))
        terminal.printf(4, 24, f"4 {player.team[3]}")
        terminal.put(14, 19, int(player.team[3].front_sprite, 16))
        terminal.printf(32, 24, f"5 {player.team[4]}")
        terminal.put(42, 19, int(player.team[4].front_sprite, 16))
        terminal.printf(59, 24, f"6 {player.team[5]}")
        terminal.put(69, 19, int(player.team[5].front_sprite, 16))
        terminal.printf(32, 3, f"7 give up {choice.get("Species")}")
        terminal.refresh()
        while True:
            button = terminal.read()
            if button == terminal.TK_1:
                input = 0
            elif button == terminal.TK_2:
                input = 1
            elif button == terminal.TK_3:
                input = 2
            elif button == terminal.TK_4:
                input = 3
            elif button == terminal.TK_5:
                input = 4
            elif button == terminal.TK_6:
                input = 5
            elif button == terminal.TK_7:
                input = 6
            else:
                input = None
            if input is None:
                pass
            elif input <= len(player.team) - 1:
                player.team.pop(input)
                player.team.insert(input, Pokemon(choice.get("Species"), player))
                break
            elif input == len(player.team):
                break
    elif choice is not None:
        player.team.append(Pokemon(choice.get("Species"), player))


terminal.put(0, 0, 0xF8FC)
terminal.printf(29, 7, "What is your name?: ")
player_name = terminal.read_str(49
                                , 7, "", 12)[1]
player = Player(player_name, [])
terminal.clear()
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
while True:
    button = terminal.read()
    if button == terminal.TK_1:
        player_starter = Pokemon("Bulbasaur", player, 5)
        break
    elif button == terminal.TK_2:
        player_starter = Pokemon("Charmander", player, 5)
        break
    elif button == terminal.TK_3:
        player_starter = Pokemon("Squirtle", player, 5)
        break
    elif button == terminal.TK_4:
        random_starter = pokedex[random.randint(0, 388)].get("Species")
        player_starter = Pokemon(random_starter, player, 5)
        break
    else:
        pass
terminal.clear()
player.starter_type = player_starter.type_one
player.team.append(player_starter)

# Rival 1
catch_pokemon("lvl9")
print_exp(9)
poke_center()
print_txt(f"You stumble into your rival {rival} and they challenge you to a battle!")
terminal.clear()

rival_1 = Player(f"{rival}", [])
rival_1.team = [Pokemon("Rattata", rival_1, 7), Pokemon("Treecko", rival_1, 9)]

rival1_battle = Battle(player, rival_1)
rival1_battle.battle()

# Gym 1
catch_pokemon("lvl14")
print_exp(14)
poke_center()
print_txt(f"You enter the Rustboro City gym and challenge its leader Roxanne!")
terminal.clear()

roxanne = Player("Roxanne", [])
roxanne.team = [Pokemon("Geodude", roxanne, 12), Pokemon("Geodude", roxanne, 12),
                Pokemon("Nosepass", roxanne, 14)]

gym1_battle = Battle(player, roxanne)
gym1_battle.battle()

# Gym 2
catch_pokemon("lvl20")
catch_pokemon("lvl20")
print_exp(20)
poke_center()
print_txt(f"You enter the Dewford Town gym and challenge its leader Brawly!")
terminal.clear()

brawly = Player("Brawly", [])
brawly.team = [Pokemon("Machop", brawly, 17), Pokemon("Meditite", brawly, 17),
               Pokemon("Makuhita", brawly, 20)]

gym2_battle = Battle(player, brawly)
gym2_battle.battle()

# Gym 3

catch_pokemon("lvl26")
catch_pokemon("lvl26")
print_exp(26)
poke_center()
print_txt(f"You enter the Mauville City gym and challenge its leader Wattson!")
terminal.clear()

wattson = Player("Wattson", [])
wattson.team = [Pokemon("Voltorb", wattson, 22), Pokemon("Electrike", wattson, 22),
                Pokemon("Magneton", wattson, 24), Pokemon("Manectric", wattson, 26)]

gym3_battle = Battle(player, wattson)
gym3_battle.battle()

# Gym 4

catch_pokemon("lvl30")
catch_pokemon("lvl30")
print_exp(30)
poke_center()
print_txt(f"You enter the Lavaridge Town gym and challenge its leader Flannery!")
terminal.clear()

flannery = Player("Flannery", [])
flannery.team = [Pokemon("Numel", flannery, 25), Pokemon("Slugma", flannery, 25),
                 Pokemon("Camerupt", flannery, 27), Pokemon("Torkoal", flannery, 30)]

gym4_battle = Battle(player, flannery)
gym4_battle.battle()

# Rival 2
catch_pokemon("lvl36")
print_exp(36)
poke_center()
print_txt(f"You stumble into your rival {rival} and they challenge you to a battle!")
terminal.clear()

rival_2 = Player(f"{rival}", [])
rival_2.team = [Pokemon("Raticate", rival_2, 36), Pokemon("Swellow", rival_2, 35),
                Pokemon("Numel", rival_2, 34), Pokemon("Wailmer", rival_2, 35),
                Pokemon("Sceptile", rival_2, 36)]

rival2_battle = Battle(player, rival_2)
rival2_battle.battle()

# Gym 5

catch_pokemon("lvl40")
print_exp(40)
poke_center()
print_txt(f"You enter the Petalburg City gym and challenge its leader Norman!")
terminal.clear()

norman = Player("Norman", [])
norman.team = [Pokemon("Spinda", norman, 36), Pokemon("Vigoroth", norman, 36),
               Pokemon("Linoone", norman, 38), Pokemon("Slaking", norman, 40)]

gym5_battle = Battle(player, norman)
gym5_battle.battle()

# Gym 6
catch_pokemon("lvl46")
catch_pokemon("lvl46")
print_exp(46)
poke_center()
print_txt(f"You enter the Fortree City gym and challenge its leader Winona!")
terminal.clear()

winona = Player("Winona", [])
winona.team = [Pokemon("Swablu", winona, 42), Pokemon("Tropius", winona, 42),
               Pokemon("Pelipper", winona, 43), Pokemon("Skarmory", winona, 44),
               Pokemon("Altaria", winona, 46)]

gym6_battle = Battle(player, winona)
gym6_battle.battle()

# Gym 7 Replace eventually
catch_pokemon("lvl52")
catch_pokemon("lvl52")
print_exp(52)
poke_center()
print_txt(f"You enter the Mossdeep City gym and challenge its leader's Tate & Liza!")
terminal.clear()

tate_liza = Player("Tate&Liza", [])
tate_liza.team = [Pokemon("Claydol", tate_liza, 51), Pokemon("Xatu", tate_liza, 51),
                  Pokemon("Lunatone", tate_liza, 52), Pokemon("Solrock", tate_liza, 52)]

gym7_battle = Battle(player, tate_liza)
gym7_battle.battle()

# Gym 8
catch_pokemon("lvl58")
catch_pokemon("lvl58")
print_exp(58)
poke_center()
print_txt(f"You enter the Sootopolis City and challenge its leader's Juan!")
terminal.clear()

juan = Player("Juan", [])
juan.team = [Pokemon("Luvdisc", juan, 53), Pokemon("Whiscash", juan, 53),
             Pokemon("Sealeo", juan, 55), Pokemon("Crawdaunt", juan, 55),
             Pokemon("Kingdra", juan, 58)]

gym8_battle = Battle(player, juan)
gym8_battle.battle()

# Rival 3
catch_pokemon("lvl58")
catch_pokemon("lvl58")
print_exp(64)
poke_center()
print_txt(f"You stumble into your rival {rival} and they challenge you to a battle!")
terminal.clear()

rival_3 = Player(f"{rival}", [])
rival_3.team = [Pokemon("Gengar", rival_2, 64), Pokemon("Alakazam", rival_2, 64),
                Pokemon("Arcanine", rival_2, 64), Pokemon("Wailord", rival_2, 64),
                Pokemon("Sceptile", rival_2, 64), Pokemon("Dragonite", rival_2, 64)]

rival3_battle = Battle(player, rival_3)
rival3_battle.battle()

# Elite4 1
print_exp(70)
poke_center()
print_txt(f"You enter the Elite 4 you challenge member Sidney first!")
terminal.clear()

sidney = Player("Sidney", [])
sidney.team = [Pokemon("Mightyena", sidney, 67), Pokemon("Shiftry", sidney, 69),
               Pokemon("Cacturne", sidney, 67), Pokemon("Crawdaunt", sidney, 69),
               Pokemon("Absol", sidney, 70)]

elite4_1_battle = Battle(player, sidney)
elite4_1_battle.battle()

# Elite4 2
print_exp(72, "The battle has brought your pokemon to level 72.")
poke_center()
print_txt(f"Next you challenge Member Phoebe!")
terminal.clear()

phoebe = Player("Phoebe", [])
phoebe.team = [Pokemon("Dusclops", phoebe, 69), Pokemon("Banette", phoebe, 70),
               Pokemon("Sableye", phoebe, 71), Pokemon("Banette", phoebe, 70),
               Pokemon("Dusclops", phoebe, 72)]

elite4_2_battle = Battle(player, phoebe)
elite4_2_battle.battle()

# Elite4 3
print_exp(74, "The battle has brought your pokemon to level 74.")
poke_center()
print_txt(f"Next you challenge Member Glacia!")
terminal.clear()

glacia = Player("Glacia", [])
glacia.team = [Pokemon("Sealeo", glacia, 71), Pokemon("Glalie", glacia, 71),
               Pokemon("Sealeo", glacia, 73), Pokemon("Glalie", glacia, 73),
               Pokemon("Walrein", glacia, 74)]

elite4_3_battle = Battle(player, glacia)
elite4_3_battle.battle()

# Elite4 4
print_exp(76, "The battle has brought your pokemon to level 76.")
poke_center()
print_txt(f"Next you challenge Member Drake!")
terminal.clear()

drake = Player("Drake", [])
drake.team = [Pokemon("Shelgon", drake, 73), Pokemon("Altaria", drake, 75),
              Pokemon("Kingdra", drake, 74), Pokemon("Flygon", drake, 74),
              Pokemon("Salamence", drake, 76)]

elite4_4_battle = Battle(player, drake)
elite4_4_battle.battle()

# Champion
print_exp(78, "The battle has brought your pokemon to level 78.")
poke_center()
print_txt(f"Lastly you challenge the champion Wallace!")
terminal.clear()

wallace = Player("Wallace", [])
wallace.team = [Pokemon("Wailord", wallace, 77), Pokemon("Tentacruel", wallace, 75),
                Pokemon("Ludicolo", wallace, 76), Pokemon("Whiscash", wallace, 76),
                Pokemon("Gyarados", wallace, 76), Pokemon("Milotic", wallace, 78)]

champion_battle = Battle(player, wallace)
champion_battle.battle()

print_txt(f"You have become champion and your journey has come to a end!...")

# Legendary
print_exp(80, "While resting at home you hear news of a pokemon attacking a nearby town and you go to help!")
poke_center()
terminal.clear()

legendary = random.choice(encounters.get("Legendary"))
legendary_trainer = Player("", [Pokemon(legendary, "", 85)])

if len(player.team) == 6:
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(13, 1, f"Would you like to replace one of your pokemon with {legendary}")
    terminal.printf(4, 14, f"1 {player.team[0]}")
    terminal.put(14, 9, int(player.team[0].front_sprite, 16))
    terminal.printf(32, 14, f"2 {player.team[1]}")
    terminal.put(42, 9, int(player.team[1].front_sprite, 16))
    terminal.printf(59, 14, f"3 {player.team[2]}")
    terminal.put(69, 9, int(player.team[2].front_sprite, 16))
    terminal.printf(4, 24, f"4 {player.team[3]}")
    terminal.put(14, 19, int(player.team[3].front_sprite, 16))
    terminal.printf(32, 24, f"5 {player.team[4]}")
    terminal.put(42, 19, int(player.team[4].front_sprite, 16))
    terminal.printf(59, 24, f"6 {player.team[5]}")
    terminal.put(69, 19, int(player.team[5].front_sprite, 16))
    terminal.printf(32, 3, f"7 give up {legendary}")
    terminal.refresh()
    while True:
        button = terminal.read()
        if button == terminal.TK_1:
            input = 0
        elif button == terminal.TK_2:
            input = 1
        elif button == terminal.TK_3:
            input = 2
        elif button == terminal.TK_4:
            input = 3
        elif button == terminal.TK_5:
            input = 4
        elif button == terminal.TK_6:
            input = 5
        elif button == terminal.TK_7:
            input = 6
        else:
            input = None
        if input is None:
            pass
        elif input <= len(player.team) - 1:
            player.team.pop(input)
            player.team.insert(input, Pokemon(legendary, player, 85))
            break
        elif input == len(player.team):
            break
else:
    player.team.append(Pokemon(legendary, player, 85))

# Steven
print_txt(f"After catching {legendary} a man named Steven asks to battle you and you accept!")
poke_center()
terminal.clear()

steven = Player("Steven", [])
steven.team = [Pokemon("Skarmory", steven, 84), Pokemon("Claydol", steven, 82),
               Pokemon("Aggron", steven, 83), Pokemon("Cradily", steven, 83),
               Pokemon("Armaldo", steven, 83), Pokemon("Metagross", steven, 85)]

steven_battle = Battle(player, steven)
steven_battle.battle()

print_txt(f"Thank you for playing you have finished the game as it is now!")
terminal.clear()
