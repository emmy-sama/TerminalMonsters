from BattleSystem import *
from Classes import *


ash = Player("Ash", "they/them", 0, [])
weedle = Pokemon("Weedle", ash, 25)
pikachu = Pokemon("Pikachu", ash, 25)
poliwhirl = Pokemon("Poliwhirl", ash, 25)
ash.team.append(weedle)
ash.team.append(pikachu)
ash.team.append(poliwhirl)

garry = Player("Garry", "they/them", 0, [])
onix = Pokemon("Onix", garry, 25)
charmander = Pokemon("Charmander", garry, 25)
slowbro = Pokemon("Slowbro", garry, 25)
garry.team.append(onix)
garry.team.append(charmander)
garry.team.append(slowbro)

terminal.open()
terminal.set("window: size=112x25")
terminal.set("0xE000: data/Gen1MonoS.png, size=256x256, resize=333x333")
terminal.set("0xF8FE: data/HPbars.png")
terminal.set("0xF8FD: data/TextBoxR.png")
terminal.set("0xF8FF: data/TextBoxL.png")
terminal.set("0xF8FC: data/Field.png, resize=500x1000")
terminal.set("0x2640: data/Female_symbol.png, align=center")
terminal.set("0x2642: data/Male_symbol.png, align=center")
terminal.set("font: data/pokemon.ttf, size=16")
terminal.put(10, 0, 0xF8FC)
terminal.layer(1)
ash_v_gary = Battle(ash, garry)
ash_v_gary.battle()
