import math
import random


class Battle:
    def __init__(self, player, opponent, moves, types):
        self.temp_stat_table_norm = {-6: 2 / 8, -5: 2 / 7, -4: 2 / 6, -3: 2 / 5, -2: 2 / 4, -1: 2 / 3, 0: 2 / 2,
                                     1: 3 / 2, 2: 4 / 2,
                                     3: 5 / 2, 4: 6 / 2, 5: 7 / 2, 6: 8 / 2}
        self.temp_stat_table_acc_eva = {-6: 33 / 100, -5: 36 / 100, -4: 43 / 100, -3: 50 / 100, -2: 60 / 100,
                                        -1: 75 / 100, 0: 100 / 100, 1: 133 / 100, 2: 166 / 100, 3: 200 / 100,
                                        4: 250 / 100, 5: 266 / 100, 6: 300 / 100}
        self.turn = 0
        self.moves = moves
        self.types = types
        self.player = player
        self.player_active = player.team[0]
        self.opponent = opponent
        self.opponent_active = opponent.team[0]
        self.weather = "clear"
        self.reflect = False
        self.light_screen = False
        self.p_move = None
        self.ai_move = None

    def battle(self):
        while True:
            self.turn += 1
            print(f"Turn: {self.turn}")
            print(f"{self.player_active.species}'s HP: {self.player_active.chp}/{self.player_active.hp}")
            print(f"{self.opponent_active.species}'s HP: {self.opponent_active.chp}/{self.opponent_active.hp}")
            self.p_move = None
            self.ai_move = self.ai_turn()
            self.player_turn()
            if self.p_move is not None and self.ai_move is not None:
                order = self.speed_check()
                self.action(order[0], order[2], order[1])
                if order[0].chp <= 0:
                    if order[0] == self.player_active:
                        self.player.team.remove(self.player_active)
                        self.player_active = None
                    if order[0] == self.opponent_active:
                        self.opponent.team.remove(self.opponent_active)
                        self.opponent_active = None
                if order[2].chp > 0:
                    self.action(order[2], order[0], order[3])
                if self.alive_check():
                    return
            elif self.p_move is None and self.ai_move is None:
                pass
            elif self.p_move is None:
                if self.opponent_active.chp > 0:
                    self.action(self.opponent_active, self.player_active, self.ai_move)
                self.alive_check()
            elif self.ai_move is None:
                if self.player_active.chp > 0:
                    self.action(self.player_active, self.opponent_active, self.p_move)
                if self.alive_check():
                    return

    def ai_turn(self):
        ai_random = random.choice(self.opponent_active.moves)
        for move in self.moves:
            if move.get("name") == ai_random:
                return move

    def player_turn(self):
        while True:
            player_action = int(input("What will you do? 1.Fight 2.Check/Swap Pokemon 3.Open Bag: "))
            if player_action == 3:
                print("Will add items later")
            if player_action == 2:
                while True:
                    for pokes in self.player.team:
                        print(f"{self.player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                    print("7.Back")
                    x = int(input("Please Select a pokemon to view details of or swap in: "))
                    if x == 7:
                        break
                    while True:
                        self.player.team[x - 1].check_poke_advanced()
                        y = int(input("1.Swap 2.Check Moves 3.Back: "))
                        if y == 3:
                            break
                        if y == 2:
                            while True:
                                self.player.team[x - 1].check_poke_moves()
                                z = int(input("1.Swap 2.Back: "))
                                if z == 1:
                                    self.player_active.reset_temp()
                                    self.player_active = self.player.team[x - 1]
                                    print(f"{self.player.name} sent out {self.player_active.species}")
                                    return
                                if z == 2:
                                    break
                        if y == 1:
                            self.player_active.reset_temp()
                            self.player_active = self.player.team[x - 1]
                            print(f"{self.player.name} sent out {self.player_active.species}")
                            return
            if player_action == 1:
                for m in self.player_active.moves:
                    print(f"{self.player_active.moves.index(m) + 1}.{m}")
                print("5.Back")
                x = int(input("Please Select a move: "))
                if x == 5:
                    pass
                else:
                    for move in self.moves:
                        if move.get("name") == self.player_active.moves[int(x) - 1]:
                            self.p_move = move
                            return

    def speed_check(self):
        player_speed = math.floor(self.player_active.speed *
                                  self.temp_stat_table_norm.get(self.player_active.temp_stats.get("speed")))
        opponent_speed = math.floor(self.opponent_active.speed *
                                    self.temp_stat_table_norm.get(self.opponent_active.temp_stats.get("speed")))
        if player_speed > opponent_speed:
            return [self.player_active, self.p_move, self.opponent_active, self.ai_move]
        elif opponent_speed > player_speed:
            return [self.opponent_active, self.ai_move, self.player_active, self.p_move]
        else:
            speed_tie = random.randint(0, 1)
            if speed_tie == 0:
                return [self.player_active, self.p_move, self.opponent_active, self.ai_move]
            else:
                return [self.opponent_active, self.ai_move, self.player_active, self.p_move]

    def action(self, attacker, defender, move):
        print(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
        if defender is None and "Requires Target" in move.get("flags"):
            print("But it failed")
            return
        if move.get("accuracy") != 0:
            hit_check = random.randint(1, 100)
            accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
            if accuracy_stage > 6:
                accuracy_stage = 6
            elif accuracy_stage < -6:
                accuracy_stage = -6
            accuracy = move.get("accuracy") * self.temp_stat_table_acc_eva.get(accuracy_stage)
            if hit_check > accuracy:
                print(f"{attacker.species} Missed!")
                return
        if move.get("category") == "Non-Damaging":
            self.non_dmg_move(attacker, defender, move)
        else:
            dmg = self.dmg_calc(attacker, defender, move)
            defender.chp -= dmg

    def dmg_calc(self, attacker, defender, move):
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
                atk = math.floor(attacker.attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("attack")))
                dfn = math.floor(defender.defense * self.temp_stat_table_norm.get(defender.temp_stats.get("defense")))
        else:
            if crit:
                atk = attacker.sp_attack
                dfn = defender.sp_defense
            else:
                atk = math.floor(attacker.sp_attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
                dfn = math.floor(defender.sp_defense * self.temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
        total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("power")) / dfn) / 50)
        if attacker.burned and dmg_type == "Physical":
            total = math.floor(total * 0.5)
        if self.reflect and dmg_type == "Physical" and not crit:
            total = math.floor(total * 0.5)
        if self.light_screen and dmg_type == "Special" and not crit:
            total = math.floor(total * 0.5)
        if self.weather != "clear" and move_type == "Fire" or move_type == "Water":
            if self.weather == "rain":
                if move_type == "Water":
                    total = math.floor(total * 1.5)
                if move_type == "Fire":
                    total = math.floor(total * 0.5)
            if self.weather == "sun":
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
        for item in self.types:
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

    def non_dmg_move(self, attacker, defender, move):
        # Do Aromatherapy, Assist, Baton Pass, Block
        if "Lowers Attacker chp by hp" in move.get("flags"):
            if attacker.chp - math.floor(attacker.hp * move.get("hp changes")) <= 0:
                print("But it failed")
                return
            else:
                attacker.chp -= math.floor(attacker.hp * move.get("hp changes"))
        if "Changes Attacker Stats" in move.get("flags"):
            for key in list(move.get("stat changes").keys()):
                attacker.temp_stats[key] += move.get("stat changes").get(key)
                if move.get("stat changes").get(key) > 1:
                    print(f"{attacker.species}'s {key} rose sharply!")
                elif move.get("stat changes").get(key) == 1:
                    print(f"{attacker.species}'s {key} rose!")
                if move.get("stat changes").get(key) == -1:
                    print(f"{attacker.species}'s {key} fell!")
                elif move.get("stat changes").get(key) < -1:
                    print(f"{attacker.species}'s {key} harshly fell!")
                if attacker.temp_stats[key] >= 6:
                    attacker.temp_stats[key] = 6
                    print(f"{attacker.species}'s {key} wont go any higher!")
                elif attacker.temp_stats[key] <= -6:
                    attacker.temp_stats[key] = -6
                    print(f"{attacker.species}'s {key} wont go any lower!")
                print(attacker.temp_stats)
        if "Changes Defender Stats" in move.get("flags"):
            key = list(move.get("stat changes").keys())[0]
            defender.temp_stats[key] += move.get("stat changes").get(key)
            if move.get("stat changes").get(key) > 1:
                print(f"{defender.species}'s {key} rose sharply!")
            elif move.get("stat changes").get(key) == 1:
                print(f"{defender.species}'s {key} rose!")
            if move.get("stat changes").get(key) == -1:
                print(f"{defender.species}'s {key} fell!")
            elif move.get("stat changes").get(key) < -1:
                print(f"{defender.species}'s {key} harshly fell!")
            if defender.temp_stats[key] >= 6:
                defender.temp_stats[key] = 6
                print(f"{defender.species}'s {key} wont go any higher!")
            elif defender.temp_stats[key] <= -6:
                defender.temp_stats[key] = -6
                print(f"{defender.species}'s {key} wont go any lower!")
            print(defender.temp_stats)



    def alive_check(self):
        if self.player_active.chp <= 0 or self.player_active is None:
            self.player.team.remove(self.player_active)
            if not self.player.team:
                print(f"{self.opponent.name} Wins!")
                return True
            player_active = None
            while player_active is None:
                for pokes in self.player.team:
                    print(f"{self.player.team.index(pokes) + 1}.", end=""), pokes.check_poke_basic()
                x = int(input("Please Select a pokemon to view details of or swap in: "))
                while True:
                    self.player.team[x - 1].check_poke_advanced()
                    y = int(input("1.Swap 2.Check Moves 3.Back: "))
                    if y == 3:
                        break
                    if y == 2:
                        while True:
                            self.player.team[x - 1].check_poke_moves(self.moves)
                            z = int(input("1.Swap 2.Back"))
                            if z == 1:
                                player_active = self.player.team[x - 1]
                                print(f"{self.player.name} sent out {player_active.species}")
                                break
                            if z == 2:
                                break
                    if y == 1:
                        player_active = self.player.team[x - 1]
                        print(f"{self.player.name} sent out {player_active.species}")
                        break
        if self.opponent_active.chp <= 0 or self.opponent_active is None:
            self.opponent.team.remove(self.opponent_active)
            if not self.opponent.team:
                print(f"{self.player.name} Wins!")
                return True
            self.opponent_active = None
            self.opponent_active = random.choice(self.opponent.team)
            print(f"{self.opponent.name} sent out {self.opponent_active.species}")
