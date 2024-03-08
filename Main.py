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

player_pokemon_count = 1


def catch_pokemon():
    choice = None
    mon_1 = random.randint(0, 388)
    mon_1_species = pokedex[mon_1].get("Species")
    mon_1_dex = pokedex[mon_1].get("dex_number")
    mon_2 = random.randint(0, 388)
    mon_2_species = pokedex[mon_2].get("Species")
    mon_2_dex = pokedex[mon_2].get("dex_number")
    mon_3 = random.randint(0, 388)
    mon_3_species = pokedex[mon_3].get("Species")
    mon_3_dex = pokedex[mon_3].get("dex_number")
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(22, 6, "What pokemon would you like to try and catch?")
    terminal.printf(9, 18, f"1 {mon_1_species}")
    terminal.put(14, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1_dex) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_1_dex) + 58117)]), 16))
    terminal.printf(37, 18, f"2 {mon_2_species}")
    terminal.put(42, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2_dex) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_2_dex) + 58117)]), 16))
    terminal.printf(69, 18, f"3 {mon_3_species}")
    terminal.put(74, 12, int(random.choice([hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3_dex) + 58116),
                                          hex(list(map(lambda x: x // 2, range(1, 774))).index(mon_3_dex) + 58117)]), 16))
    terminal.printf(37, 21, "4 Pass")
    terminal.refresh()
    while True:
        button = terminal.read()
        if button == terminal.TK_1:
            choice = [mon_1_species, mon_1_dex]
            break
        elif button == terminal.TK_2:
            choice = [mon_2_species, mon_2_dex]
            break
        elif button == terminal.TK_3:
            choice = [mon_3_species, mon_3_dex]
            break
        elif button == terminal.TK_4:
            break
        else:
            pass
    if len(player.team) == 6 and choice is not None:
        terminal.clear()
        terminal.put(0, 0, 0xF8FC)
        terminal.printf(13, 1, f"Would you like to replace one of your pokemon with {choice[0]}")
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
        terminal.printf(32, 3, f"7 give up {choice[0]}")
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
                player.team.insert(input, Pokemon(choice[0], player))
                break
            elif input == len(player.team):
                break
    elif choice is not None:
        player.team.append(Pokemon(choice[0], player))


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

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(14)
terminal.clear()

# Gym 1
roxanne = Player("Roxanne", [])
geodude_rox = Pokemon("Geodude", roxanne, 12)
geodude_rox2 = Pokemon("Geodude", roxanne, 12)
nosepass_rox = Pokemon("Nosepass", roxanne, 15)
roxanne.team = [geodude_rox, geodude_rox2, nosepass_rox]

gym1_battle = Battle(player, roxanne)
gym1_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(18)
terminal.clear()

# Gym 2
brawly = Player("Brawly", [])
machop_bra = Pokemon("Machop", brawly, 16)
meditite_bra = Pokemon("Meditite", brawly, 16)
makuhita_bra = Pokemon("Makuhita", brawly, 19)
brawly.team = [machop_bra, meditite_bra, makuhita_bra]

gym2_battle = Battle(player, brawly)
gym2_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(23)
terminal.clear()

# Gym 3
wattson = Player("Wattson", [])
voltorb_wat = Pokemon("Voltorb", wattson, 20)
electrike_wat = Pokemon("Electrike", wattson, 20)
magneton_wat = Pokemon("Magneton", wattson, 22)
manectric_wat = Pokemon("Manectric", wattson, 24)
wattson.team = [voltorb_wat, electrike_wat, magneton_wat, manectric_wat]

gym3_battle = Battle(player, wattson)
gym3_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(28)
terminal.clear()

# Gym 4
flannery = Player("Flannery", [])
numel_fla = Pokemon("Numel", flannery, 24)
slugma_fla = Pokemon("Slugma", flannery, 24)
camerupt_fla = Pokemon("Camerupt", flannery, 26)
torkoal_fla = Pokemon("Torkoal", flannery, 29)
flannery.team = [numel_fla, slugma_fla, camerupt_fla, torkoal_fla]

gym4_battle = Battle(player, flannery)
gym4_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(30)
terminal.clear()

# Gym 5
norman = Player("Norman", [])
spinda_nor = Pokemon("Spinda", norman, 27)
vigoroth_nor = Pokemon("Vigoroth", norman, 27)
linoone_nor = Pokemon("Linoone", norman, 29)
slaking_nor = Pokemon("Slaking", norman, 31)
norman.team = [spinda_nor, vigoroth_nor, linoone_nor, slaking_nor]

gym5_battle = Battle(player, norman)
gym5_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(32)
terminal.clear()

# Gym 6
winona = Player("Winona", [])
swablu_win = Pokemon("Swablu", winona, 29)
tropius_win = Pokemon("Tropius", winona, 29)
pelipper_win = Pokemon("Pelipper", winona, 30)
skarmory_win = Pokemon("Skarmory", winona, 31)
altaria_win = Pokemon("Altaria", winona, 33)
winona.team = [swablu_win, tropius_win, pelipper_win, skarmory_win, altaria_win]

gym6_battle = Battle(player, winona)
gym6_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(41)
terminal.clear()

# Gym 7 Replace eventually
tate_liza = Player("Tate&Liza", [])
claydol_tal = Pokemon("Claydol", tate_liza, 41)
xatu_tal = Pokemon("Xatu", tate_liza, 41)
lunatone_tal = Pokemon("Lunatone", tate_liza, 42)
solrock_tal = Pokemon("Solrock", tate_liza, 42)
tate_liza.team = [claydol_tal, xatu_tal, lunatone_tal, solrock_tal]

gym7_battle = Battle(player, tate_liza)
gym7_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(45)
terminal.clear()

# Gym 8
juan = Player("Juan", [])
luvdisc_jua = Pokemon("Luvdisc", juan, 41)
whiscash_jua = Pokemon("Whiscash", juan, 41)
sealeo_jua = Pokemon("Sealeo", juan, 43)
crawdaunt_jua = Pokemon("Crawdaunt", juan, 43)
kingdra_jua = Pokemon("Kingdra", juan, 46)
juan.team = [luvdisc_jua, whiscash_jua, sealeo_jua, crawdaunt_jua, kingdra_jua]

gym8_battle = Battle(player, juan)
gym8_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(48)
terminal.clear()

# Elite4 1
sidney = Player("Sidney", [])
mightyena_sid = Pokemon("Mightyena", sidney, 46)
shiftry_sid = Pokemon("Shiftry", sidney, 48)
cacturne_sid = Pokemon("Cacturne", sidney, 46)
crawdaunt_sid = Pokemon("Crawdaunt", sidney, 48)
absol_sid = Pokemon("Absol", sidney, 49)
sidney.team = [mightyena_sid, shiftry_sid, cacturne_sid, crawdaunt_sid, absol_sid]

elite4_1_battle = Battle(player, sidney)
elite4_1_battle.battle()

for pokemon in player.team:
    pokemon.level_up(50)
terminal.clear()

# Elite4 2
phoebe = Player("Phoebe", [])
dusclops_pho = Pokemon("Dusclops", phoebe, 48)
banette_pho = Pokemon("Banette", phoebe, 49)
sableye_pho = Pokemon("Sableye", phoebe, 50)
banette_pho2 = Pokemon("Banette", phoebe, 49)
dusclops_pho2 = Pokemon("Dusclops", phoebe, 51)
phoebe.team = [dusclops_pho, banette_pho, sableye_pho, banette_pho2, dusclops_pho2]

elite4_2_battle = Battle(player, phoebe)
elite4_2_battle.battle()

for pokemon in player.team:
    pokemon.level_up(52)
terminal.clear()

# Elite4 3
glacia = Player("Glacia", [])
sealeo_gla = Pokemon("Sealeo", glacia, 50)
glalie_gla = Pokemon("Glalie", glacia, 50)
sealeo_gla2 = Pokemon("Sealeo", glacia, 52)
glalie_gla2 = Pokemon("Glalie", glacia, 52)
walrein_gla = Pokemon("Walrein", glacia, 53)
glacia.team = [mightyena_sid, shiftry_sid, cacturne_sid, crawdaunt_sid, absol_sid]

elite4_3_battle = Battle(player, glacia)
elite4_3_battle.battle()

for pokemon in player.team:
    pokemon.level_up(54)
terminal.clear()

# Elite4 4
drake = Player("Drake", [])
shelgon_dra = Pokemon("Shelgon", drake, 52)
altaria_dra = Pokemon("Altaria", drake, 54)
kingdra_dra = Pokemon("Kingdra", drake, 53)
flygon_dra = Pokemon("Flygon", drake, 53)
salamence_dra = Pokemon("Salamence", drake, 55)
drake.team = [shelgon_dra, altaria_dra, kingdra_dra, flygon_dra, salamence_dra]

elite4_4_battle = Battle(player, drake)
elite4_4_battle.battle()

for pokemon in player.team:
    pokemon.level_up(57)
terminal.clear()

# Champion
wallace = Player("Wallace", [])
wailord_wal = Pokemon("Wailord", wallace, 57)
tentacruel_wal = Pokemon("Tentacruel", wallace, 55)
ludicolo_wal = Pokemon("Ludicolo", wallace, 56)
whiscash_wal = Pokemon("Whiscash", wallace, 56)
gyarados_wal = Pokemon("Gyarados", wallace, 56)
milotic_wal = Pokemon("Milotic", wallace, 58)
wallace.team = [wailord_wal, tentacruel_wal, ludicolo_wal, whiscash_wal, gyarados_wal, milotic_wal]

champion_battle = Battle(player, wallace)
champion_battle.battle()

catch_pokemon()
catch_pokemon()
for pokemon in player.team:
    pokemon.level_up(77)
terminal.clear()

# Steven
steven = Player("Steven", [])
skarmory_ste = Pokemon("Skarmory", steven, 77)
claydol_ste = Pokemon("Claydol", steven, 75)
aggron_ste = Pokemon("Aggron", steven, 76)
cradily_ste = Pokemon("Cradily", steven, 76)
armaldo_ste = Pokemon("Armaldo", steven, 76)
metagross_ste = Pokemon("Metagross", steven, 78)
steven.team = [skarmory_ste, claydol_ste, aggron_ste, cradily_ste, armaldo_ste, metagross_ste]

steven_battle = Battle(player, steven)
steven_battle.battle()
