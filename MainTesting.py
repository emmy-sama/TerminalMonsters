from BattleSystem import *
from Classes import *


ash = Player("Ash", [])
weedle = Pokemon("Feraligatr", ash, 30)
pikachu = Pokemon("Pikachu", ash, 5)
poliwhirl = Pokemon("Poliwhirl", ash, 5)
ash.team.append(weedle)
ash.team.append(pikachu)
ash.team.append(poliwhirl)

garry = Ai("Garry", [])
onix = Pokemon("Testmon2", garry, 5)
charmander = Pokemon("Testmon2", garry, 5)
slowbro = Pokemon("Slowbro", garry, 5)
garry.team.append(onix)
garry.team.append(charmander)
garry.team.append(slowbro)

terminal.open()
terminal.set("window: size=88x25")
terminal.set("0xE001: data/pngs/BackSprites.png, size=333x333, align=center")
terminal.set("0xE305: data/pngs/FrontSprites.png, size=333x333, align=center")
terminal.set("0xF8FF: data/pngs/Background.png")
terminal.set("0xF8FD: data/pngs/Background2.png")
terminal.set("0xF8F4: data/pngs/Pokeball.png, align=bottom-right")
terminal.set("0xF8F3: data/pngs/Pokeball_Half_Open.png, align=bottom-right")
terminal.set("0xF8F2: data/pngs/Pokeball_Open.png, align=bottom-right")
terminal.set("0x2640: data/pngs/Female_symbol.png, align=center")
terminal.set("0x2642: data/pngs/Male_symbol.png, align=center")
terminal.set("font: data/pokemon.ttf, size=16")
ash_v_gary = Battle(ash, ash.team[0], garry)
ash_v_gary.battle()
