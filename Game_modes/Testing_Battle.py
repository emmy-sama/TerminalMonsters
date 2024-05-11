from Battle_Engine.Battle_System_Main import Battle
from Classes import Pokemon, Player, Ai


def testing_battle():
    ash = Player()
    ash.team = [Pokemon("Testmon", ash, 5), Pokemon("Wobbuffet", ash, 5),
                Pokemon("Poliwhirl", ash, 5),]

    garry = Ai("Garry", [])
    garry.team = [Pokemon("Testmon2", ash, 5), Pokemon("Testmon2", ash, 5),
                  Pokemon("Slowbro", ash, 5), ]

    ash_v_gary = Battle(ash, ash.team[0], garry)
    ash_v_gary.main()
