from Classes import *
import math
import random

weather = "clear"
reflect = False
light_screen = False


def battle(player, opponent):
    turn = 0
    player_active = player.team[0]
    opponent_active = opponent.team[0]
    while True:
        turn += 1
        print(f"Turn: {turn}")
        print(f"Your HP: {player_active.chp}/{player_active.hp}")
        print(f"Opponent's HP: {opponent_active.chp}/{opponent_active.hp}")
        finished = None
        p_move = None
        ai_move = None
        ai_move = moves.get((random.choice(opponent_active.moves)))
        while not finished:
            player_action = int(input("What will you do? 1.Fight 2.Check/Swap Pokemon 3.Open Bag: "))
            if player_action == 3:
                print("Will add items later")
            if player_action == 2:
                while not finished:
                    for pokes in player.team:
                        print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    print("7.Back")
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    if x == 7:
                        break
                    while not finished:
                        player.team[x - 1].check_poke_advanced()
                        y = int(input("1.Swap 2.Check Moves 3.Back: "))
                        if y == 3:
                            break
                        if y == 2:
                            while not finished:
                                player.team[x - 1].check_poke_moves()
                                z = int(input("1.Swap 2.Back"))
                                if z == 1:
                                    player_active = player.team[x - 1]
                                    print(f"{player.name} sent out {player_active.species}")
                                    finished = True
                                if z == 2:
                                    break
                        if y == 1:
                            player_active = player.team[x - 1]
                            print(f"{player.name} sent out {player_active.species}")
                            finished = True
                            break
            if player_action == 1:
                for m in player_active.moves:
                    print(f"{player_active.moves.index(m) + 1}.{m}")
                print("5.Back")
                x = int(input("Please Select a move: "))
                if x == 5:
                    pass
                else:
                    p_move = moves.get(player_active.moves[int(x) - 1])
                    finished = True
        if p_move is not None and ai_move is not None:
            if player_active.speed > opponent_active.speed:
                first_trainer = player_active
                first_move = p_move
                second_trainer = opponent_active
                second_move = ai_move
            elif opponent_active.speed < player_active.speed:
                first_trainer = opponent_active
                first_move = ai_move
                second_trainer = player_active
                second_move = p_move
            else:
                speed_tie = random.randint(0, 1)
                if speed_tie == 0:
                    first_trainer = player_active
                    first_move = p_move
                    second_trainer = opponent_active
                    second_move = ai_move
                else:
                    first_trainer = opponent_active
                    first_move = ai_move
                    second_trainer = player_active
                    second_move = p_move
            if first_trainer.chp > 0:
                action(first_trainer, second_trainer, first_move)
            if player_active.chp <= 0:
                player.team.remove(player_active)
                if not player.team:
                    print(f"{opponent.name} Wins!")
                    break
                player_active = None
                while player_active is None:
                    for pokes in player.team:
                        print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    while True:
                        player.team[x - 1].check_poke_advanced()
                        y = int(input("1.Swap 2.Check Moves 3.Back: "))
                        if y == 3:
                            break
                        if y == 2:
                            while True:
                                player.team[x - 1].check_poke_moves()
                                z = int(input("1.Swap 2.Back"))
                                if z == 1:
                                    player_active = player.team[x - 1]
                                    print(f"{player.name} sent out {player_active.species}")
                                    break
                                if z == 2:
                                    break
                        if y == 1:
                            player_active = player.team[x - 1]
                            print(f"{player.name} sent out {player_active.species}")
                            break
            if opponent_active.chp <= 0:
                opponent.team.remove(opponent_active)
                if not opponent.team:
                    print(f"{player.name} Wins!")
                    break
                opponent_active = None
                opponent_active = random.choice(opponent.team)
            if second_trainer.chp > 0:
                action(second_trainer, first_trainer, second_move)
            if player_active.chp <= 0:
                player.team.remove(player_active)
                if not player.team:
                    print(f"{opponent.name} Wins!")
                    break
                player_active = None
                while player_active is None:
                    for pokes in player.team:
                        print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    player.team[x - 1].check_poke_advanced()
                    y = int(input("1.Swap 2.Check Moves 3.Back: "))
                    if y == 3:
                        pass
                    if y == 2:
                        while True:
                            player.team[x - 1].check_poke_moves()
                            z = int(input("1.Swap 2.Back"))
                            if z == 1:
                                player_active = player.team[x - 1]
                                print(f"{player.name} sent out {player_active.species}")
                                break
                            if z == 2:
                                break
                    if y == 1:
                        player_active = player.team[x - 1]
                        print(f"{player.name} sent out {player_active.species}")
                        break
            if opponent_active.chp <= 0:
                opponent.team.remove(opponent_active)
                if not opponent.team:
                    print(f"{player.name} Wins!")
                    break
                opponent_active = None
                opponent_active = random.choice(opponent.team)
        elif p_move is None and ai_move is None:
            pass
        elif p_move is None:
            if opponent_active.chp > 0:
                action(opponent_active, player_active, ai_move)
            if player_active.chp <= 0:
                player.team.remove(player_active)
                if not player.team:
                    print(f"{opponent.name} Wins!")
                    break
                player_active = None
                while player_active is None:
                    for pokes in player.team:
                        print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    while True:
                        player.team[x - 1].check_poke_advanced()
                        y = int(input("1.Swap 2.Check Moves 3.Back: "))
                        if y == 3:
                            break
                        if y == 2:
                            while True:
                                player.team[x - 1].check_poke_moves()
                                z = int(input("1.Swap 2.Back"))
                                if z == 1:
                                    player_active = player.team[x - 1]
                                    print(f"{player.name} sent out {player_active.species}")
                                    break
                                if z == 2:
                                    break
                        if y == 1:
                            player_active = player.team[x - 1]
                            print(f"{player.name} sent out {player_active.species}")
                            break
            if opponent_active.chp <= 0:
                opponent.team.remove(opponent_active)
                if not opponent.team:
                    print(f"{player.name} Wins!")
                    break
                opponent_active = None
                opponent_active = random.choice(opponent.team)
        else:
            if player_active.chp > 0:
                action(player_active, opponent_active, p_move)
            if player_active.chp <= 0:
                player.team.remove(player_active)
                if not player.team:
                    print(f"{opponent.name} Wins!")
                    break
                player_active = None
                while player_active is None:
                    for pokes in player.team:
                        print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    while True:
                        player.team[x - 1].check_poke_advanced()
                        y = int(input("1.Swap 2.Check Moves 3.Back: "))
                        if y == 3:
                            break
                        if y == 2:
                            while True:
                                player.team[x - 1].check_poke_moves()
                                z = int(input("1.Swap 2.Back"))
                                if z == 1:
                                    player_active = player.team[x - 1]
                                    print(f"{player.name} sent out {player_active.species}")
                                    break
                                if z == 2:
                                    break
                        if y == 1:
                            player_active = player.team[x - 1]
                            print(f"{player.name} sent out {player_active.species}")
                            break
            if opponent_active.chp <= 0:
                opponent.team.remove(opponent_active)
                if not opponent.team:
                    print(f"{player.name} Wins!")
                    break
                opponent_active = None
                opponent_active = random.choice(opponent.team)


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
        defender.chp -= dmg


ash = Player("Ash", "they/them", 0, [])
ashbulb1 = Pokemon(0, ash)
ashbulb2 = Pokemon(0, ash)
ashbulb3 = Pokemon(0, ash)
ash.team.append(ashbulb1)
ash.team.append(ashbulb2)
ash.team.append(ashbulb3)

garry = Player("Garry", "they/them", 0, [])
garrybulb1 = Pokemon(0, garry)
garrybulb2 = Pokemon(0, garry)
garrybulb3 = Pokemon(0, garry)
garry.team.append(garrybulb1)
garry.team.append(garrybulb2)
garry.team.append(garrybulb3)

battle(ash, garry)
