import math
import random
import json

weather = "clear"
reflect = False
light_screen = False
temp_stat_table_norm = {-6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3, 0: 2/2, 1: 3/2, 2: 4/2, 3: 5/2, 4: 6/2,
                        5: 7/2, 6: 8/2}
temp_stat_table_acc_eva = {-6: 33/100, -5: 36/100, -4: 43/100,	-3: 50/100,	-2: 60/100, -1: 75/100, 0: 100/100,
                           1: 133/100, 2: 166/100, 3: 200/100, 4: 250/100, 5: 266/100, 6: 300/100}


def battle(player, opponent, moves):
    turn = 0
    player_active = player.team[0]
    opponent_active = opponent.team[0]
    with open("Data/TypeEffectiveness.json") as effectiveness_json:
        types = json.load(effectiveness_json)
    while True:
        turn += 1
        print(f"Turn: {turn}")
        print(f"Your HP: {player_active.chp}/{player_active.hp}")
        print(f"Opponent's HP: {opponent_active.chp}/{opponent_active.hp}")
        finished = None
        p_move = None
        ai_move = None
        ai_random = random.choice(opponent_active.moves)
        for move in moves:
            if move.get("name") == ai_random:
                ai_move = move
                break
        player_choice = player_turn(player, player_active, moves)
        if isinstance(player_choice, dict):
            p_move = player_choice
        else:
            player_active = player_choice
        player_speed = math.floor(player_active.speed * temp_stat_table_norm.get(player_active.temp_stats.get("speed")))
        opponent_speed = math.floor(opponent_active.speed * temp_stat_table_norm.get(opponent_active.temp_stats.get("speed")))
        if p_move is not None and ai_move is not None:
            if player_speed > opponent_speed:
                first_trainer = player_active
                first_move = p_move
                second_trainer = opponent_active
                second_move = ai_move
            elif opponent_speed < player_speed:
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
                action(first_trainer, second_trainer, first_move, types)
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
                                player.team[x - 1].check_poke_moves(moves)
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
                action(second_trainer, first_trainer, second_move, types)
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
                            player.team[x - 1].check_poke_moves(moves)
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
                action(opponent_active, player_active, ai_move, types)
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
                                player.team[x - 1].check_poke_moves(moves)
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
        elif ai_move is None:
            if player_active.chp > 0:
                action(player_active, opponent_active, p_move, types)
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
                                player.team[x - 1].check_poke_moves(moves)
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


def player_turn(player, player_active, moves):
    while True:
        player_action = int(input("What will you do? 1.Fight 2.Check/Swap Pokemon 3.Open Bag: "))
        if player_action == 3:
            print("Will add items later")
        if player_action == 2:
            while True:
                for pokes in player.team:
                    print(f"{player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                print("7.Back")
                x = int(input("Please Select a pokemon to view details of or swap in: "))
                if x == 7:
                    break
                while True:
                    player.team[x - 1].check_poke_advanced()
                    y = int(input("1.Swap 2.Check Moves 3.Back: "))
                    if y == 3:
                        break
                    if y == 2:
                        while True:
                            player.team[x - 1].check_poke_moves(moves)
                            z = int(input("1.Swap 2.Back: "))
                            if z == 1:
                                player_active.reset_temp()
                                player_active = player.team[x - 1]
                                print(f"{player.name} sent out {player_active.species}")
                                return player_active
                            if z == 2:
                                break
                    if y == 1:
                        player_active.reset_temp()
                        player_active = player.team[x - 1]
                        print(f"{player.name} sent out {player_active.species}")
                        return player_active
        if player_action == 1:
            for m in player_active.moves:
                print(f"{player_active.moves.index(m) + 1}.{m}")
            print("5.Back")
            x = int(input("Please Select a move: "))
            if x == 5:
                pass
            else:
                for move in moves:
                    if move.get("name") == player_active.moves[int(x) - 1]:
                        p_move = move
                        return p_move


def action(attacker, defender, move, types):
    print(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
    hit_check = random.randint(1, 100)
    accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
    if accuracy_stage > 6:
        accuracy_stage = 6
    elif accuracy_stage < -6:
        accuracy_stage = -6
    accuracy = move.get("accuracy") * temp_stat_table_acc_eva.get(accuracy_stage)
    if hit_check > accuracy:
        print(f"{attacker.species} Missed!")
        return
    if move.get("category") != "Non-Damaging":
        dmg = dmg_calc(attacker, defender, move, types)
        defender.chp -= dmg


def dmg_calc(attacker, defender, move, types):
    crit = False
    if random.uniform(0, 1) <= 0.0625:
        crit = True
        print("A critical hit")
    dmg_type = move.get("category")
    move_type = move.get("type")
    if dmg_type == "Physical":
        if crit:
            atk = attacker.attack
            dfn = defender.defense
        else:
            atk = math.floor(attacker.attack * temp_stat_table_norm.get(attacker.temp_stats.get("attack")))
            dfn = math.floor(defender.defense * temp_stat_table_norm.get(defender.temp_stats.get("defense")))
    else:
        if crit:
            atk = attacker.sp_attack
            dfn = defender.sp_defense
        else:
            atk = math.floor(attacker.sp_attack * temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
            dfn = math.floor(defender.sp_defense * temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
    total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("power")) / dfn) / 50)
    if attacker.burned and dmg_type == "Physical":
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
    for item in types:
        if item["name"] == move_type:
            effectiveness = item.get(defender.type_one, 1)
            if defender.type_two is not None:
                effectiveness = effectiveness * item.get(defender.type_two, 1)
            break
    if effectiveness >= 2:
        print("It's super effective")
    if effectiveness <= 0.5:
        print("It's not very effective...")
    total = math.floor(total * effectiveness)
    # Check dmg range values
    for n in range(85, 101):
        print(math.floor(total * (n / 100)))
    total = math.floor((total * random.randint(85, 100)) / 100)
    if total == 0:
        total = 1
    return total
