from Classes import *
import math
import random

weather = "clear"
reflect = False
light_screen = False


def battle(player, opponent):
    turn = 0
    while True:
        turn += 1
        print(f"Turn:{turn}")
        print(f"Your HP: {player.team[0].hp}")
        print(f"Opponent's HP: {opponent.team[0].hp}")
        for m in player.team[0].moves:
            print(f"{player.team[0].moves.index(m) + 1}.{m}")
        p_move = moves.get((player.team[0]).moves[int(input("Please Select a move(The number next to move): ")) - 1])
        ai_move = moves.get((random.choice(opponent.team[0].moves)))
        if player.team[0].speed > opponent.team[0].speed:
            first_trainer = player.team[0]
            first_move = p_move
            second_trainer = opponent.team[0]
            second_move = ai_move
        elif opponent.team[0].speed < player.team[0].speed:
            first_trainer = opponent.team[0]
            first_move = ai_move
            second_trainer = player.team[0]
            second_move = p_move
        else:
            speed_tie = random.randint(0, 1)
            if speed_tie == 0:
                first_trainer = player.team[0]
                first_move = p_move
                second_trainer = opponent.team[0]
                second_move = ai_move
            else:
                first_trainer = opponent.team[0]
                first_move = ai_move
                second_trainer = player.team[0]
                second_move = p_move
        action(first_trainer, second_trainer, first_move)
        if player.team[0].hp <= 0:
            player.team.pop(0)
            if not player.team:
                break
        if opponent.team[0].hp <= 0:
            opponent.team.pop(0)
            if not opponent.team:
                break
        action(second_trainer, first_trainer, second_move)
    if not opponent.team:
        print(f"{player.name} Wins!")
    else:
        print(f"{opponent.name} Wins!")


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
            print("A critical hit")
    total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("Dmg")) / dfn) / 50)
    if attacker.burn and dmg_type == "Physical":
        total = math.floor(total * 0.5)
    if reflect and dmg_type == "Physical" and not crit:
        total = math.floor(total * 0.5)
    if light_screen and dmg_type == "Special" and not crit:
        total = math.floor(total * 0.5)
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
    # For Flash Fire
    total += 2
    # For StockPile
    if crit:
        total = math.floor(total * 2)
    # Double Dmg Moves
    # Charge
    if move_type == attacker.type_one or move_type == attacker.type_two:
        total = math.floor(total * 1.5)
    effectiveness = type_effectiveness.get(move_type).get(defender.type_one, 1)
    if defender.type_two is not None:
        effectiveness = effectiveness * type_effectiveness.get(move_type).get(defender.type_two, 1)
    if effectiveness >= 2:
        print("it's super effective")
    if effectiveness <= 0.5:
        print("it's not very effective...")
    total = math.floor(total * effectiveness)
    # Check dmg range values
    # for n in range(85, 101):
        # print(math.floor(total * (n / 100)))
    total = math.floor((total * random.randint(85, 100)) / 100)
    return total


def action(attacker, defender, move):
    print(f"{attacker.owner.name}'s {attacker.species} used {move.get("Name")}")
    hit_check = random.randint(1, 100)
    if hit_check > move.get("Acc"):
        print(f"{attacker.species} Missed!")
        return
    if move.get("DoesDmg"):
        dmg = dmg_calc(attacker, defender, move)
        defender.hp -= dmg


ash = Player("Ash", "they/them", 0, [])
bulb = Pokemon(0, ash)
ash.team.append(bulb)

garry = Player("Garry", "they/them", 0, [])
bulb1 = Pokemon(0, garry)
garry.team.append(bulb1)

print(bulb.get_stats(), bulb1.get_stats())
print(bulb.nature, bulb1.nature)
battle(ash, garry)
