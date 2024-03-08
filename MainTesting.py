from BattleSystem import *
from Classes import *


ash = Player("Ash", [], 0)
weedle = Pokemon("Testmon", ash, 5)
pikachu = Pokemon("Pikachu", ash, 5)
poliwhirl = Pokemon("Poliwhirl", ash, 5)
ash.team.append(weedle)
ash.team.append(pikachu)
ash.team.append(poliwhirl)

garry = Player("Garry", [], 0)
onix = Pokemon("Testmon2", garry, 5)
charmander = Pokemon("Charmander", garry, 5)
slowbro = Pokemon("Slowbro", garry, 5)
garry.team.append(onix)
garry.team.append(charmander)
garry.team.append(slowbro)

terminal.open()
terminal.set("window: size=88x25")
terminal.set("0xE001: data/BackSprites.png, size=333x333, align=center")
terminal.set("0xE305: data/FrontSprites.png, size=333x333, align=center")
terminal.set("0xF8FF: data/Background.png")
terminal.set("0xF8FD: data/Background2.png")
terminal.set("0x2640: data/Female_symbol.png, align=center")
terminal.set("0x2642: data/Male_symbol.png, align=center")
terminal.set("font: data/pokemon.ttf, size=16")
ash_v_gary = Battle(ash, garry)
ash_v_gary.battle()
