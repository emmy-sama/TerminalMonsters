from BattleSystem import *
from Classes import *


ash = Player("Ash", "they/them", 0, [])
Testmon = Pokemon("Testmon", ash, 5)
pika = Pokemon("Pikachu", ash)
ash.team.append(Testmon)
ash.team.append(pika)

garry = Player("Garry", "they/them", 0, [])
Testmon2 = Pokemon("Testmon2", garry)
Charmander = Pokemon("Charmander", garry)
garry.team.append(Testmon2)
garry.team.append(Charmander)

ash_v_gary = Battle(ash, garry)
ash_v_gary.battle()
