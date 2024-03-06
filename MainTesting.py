from BattleSystem import *
from Classes import *


ash = Player("Ash", "they/them", 0, [])
weedle = Pokemon("Testmon", ash, 25)
pikachu = Pokemon("Pikachu", ash, 25)
poliwhirl = Pokemon("Poliwhirl", ash, 25)
ash.team.append(weedle)
ash.team.append(pikachu)
ash.team.append(poliwhirl)

garry = Player("Garry", "they/them", 0, [])
onix = Pokemon("Testmon2", garry, 25)
charmander = Pokemon("Charmander", garry, 25)
slowbro = Pokemon("Slowbro", garry, 25)
garry.team.append(onix)
garry.team.append(charmander)
garry.team.append(slowbro)

terminal.open()
terminal.set("window: size=88x25")
terminal.set("0xE000: data/Gen1-3bit.png, size=256x256, resize=333x333, align=center")
terminal.set("0xF8FF: data/Background.png")
terminal.set("0xF8FD: data/Background2.png")
terminal.set("0x2640: data/Female_symbol.png, align=center")
terminal.set("0x2642: data/Male_symbol.png, align=center")
terminal.set("font: data/pokemon.ttf, size=16")
ash_v_gary = Battle(ash, garry)
ash_v_gary.battle()
