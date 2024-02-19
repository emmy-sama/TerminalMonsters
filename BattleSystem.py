from Classes import *
import math
import random

weather = "clear"
reflect = False
light_screen = False


def battle(player, opponent):
    while player.team != [] and opponent.team != []:
        print(opponent.team[0].hp)
        print(f"moves: 0.{(player.team[0]).moves[0]} 1.{(player.team[0]).moves[1]} "
              f"       2.{(player.team[0]).moves[2]} 3.{(player.team[0]).moves[3]}")
        pmove = moves.get((player.team[0]).moves[int(input("Please Select a move(The number next to move): "))])
        if pmove.get("DoesDmg"):
            dmg = dmg_calc(player.team[0], opponent.team[0], pmove)
            opponent.team[0].hp -= dmg
            print(dmg)


def dmg_calc(attacker, defender, move):
    dmg_type = move.get("DmgType")
    move_type = move.get("Type")
    if dmg_type == "Physical":
        atk = attacker.attack
        dfn = defender.defense
    else:
        atk = attacker.sp_attack
        dfn = defender.sp_defense
    crit = False
    if move.get("CanCrit"):
        if random.uniform(0, 1) <= 0.0625:
            crit = True
    print(crit)
    total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("Dmg")) / dfn) / 50)
    print(total)
    if attacker.burn and dmg_type == "Physical":
        total = math.floor(total * 0.5)
    print(total)
    if reflect and dmg_type == "Physical" and not crit:
        total = math.floor(total * 0.5)
    print(total)
    if light_screen and dmg_type == "Special" and not crit:
        total = math.floor(total * 0.5)
    print(total)
    if weather != "clear" and move_type == "Fire" or move_type == "Water":
        if weather == "rain":
            if move_type == "Water":
                total = math.floor(total * 1.5)
            if move_type == "Fire":
                total = math.floor(total * 0.5)
        if weather == "sun":
            if move_type == "Fire":
                total = math.floor(total * 1.5)
            if move_type == "Water":
                total = math.floor(total * 0.5)
    print(total)
    # For Flash Fire
    total += 2
    print(total)
    # For StockPile
    if crit:
        total = math.floor(total * 2)
    print(total)
    # Double Dmg Moves
    # Charge
    if move_type == attacker.type_one or move_type == attacker.type_two:
        total = math.floor(total * 1.5)
    print(total)
    total = math.floor(total * type_effectiveness.get(move_type).get(defender.type_one, 1))
    print(total)
    if defender.type_two is not None:
        total = math.floor(total * type_effectiveness.get(move_type).get(defender.type_two, 1))
    print(total)
    total = math.floor((total * random.randint(85, 100)) / 100)
    print(total)
    return total


ash = Player("ash", "they/them", 0, [])
bulb = Pokemon(0, ash)
ash.team.append(bulb)

ash1 = Player("ash", "they/them", 0, [])
bulb1 = Pokemon(0, ash1)
ash1.team.append(bulb1)

print(bulb.get_stats(), bulb1.get_stats())
print(bulb.nature, bulb1.nature)
battle(ash, ash1)
