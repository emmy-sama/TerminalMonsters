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
            self.player_active.flinched = False
            self.opponent_active.flinched = False
            self.player_active.damaged_this_turn = False
            self.opponent_active.damaged_this_turn = False
            print(f"Turn: {self.turn}")
            print(f"{self.player_active.species}'s HP: {self.player_active.chp}/{self.player_active.hp}")
            print(f"{self.opponent_active.species}'s HP: {self.opponent_active.chp}/{self.opponent_active.hp}")
            if self.opponent_active.semi_invulnerable is None and self.opponent_active.charged is False:
                if self.opponent_active.recharge:
                    self.ai_move = None
                    self.opponent_active.recharge = False
                    print(f"{self.opponent.name}'s {self.opponent_active.species} must recharge!")
                else:
                    self.ai_move = self.ai_turn()
            if self.player_active.semi_invulnerable is None and self.player_active.charged is False:
                if self.player_active.recharge:
                    self.p_move = None
                    self.player_active.recharge = False
                    print(f"{self.player.name}'s {self.player_active.species} must recharge!")
                else:
                    self.p_move = None
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
        if attacker.flinching:
            attacker.flinching = False
            attacker.charged = False
            print(f"{attacker.owner.name}'s {attacker.species} flinched!")
            return
        if "Semi-invulnerable" in move.get("flags") and attacker.semi_invulnerable is None:
            if move.get("name") == "Bounce":
                attacker.semi_invulnerable = "bounce"
                print(f"{attacker.owner.name}'s {attacker.species} sprang up!")
                return
            if move.get("name") == "Dig":
                attacker.semi_invulnerable = "dig"
                print(f"{attacker.owner.name}'s {attacker.species} dug a hole!")
                return
            if move.get("name") == "Dive":
                attacker.semi_invulnerable = "dive"
                print(f"{attacker.owner.name}'s {attacker.species} hide underwater!")
                return
            if move.get("name") == "Fly":
                attacker.semi_invulnerable = "fly"
                print(f"{attacker.owner.name}'s {attacker.species} flew up high!")
                return
        elif "Semi-invulnerable" in move.get("flags"):
            attacker.semi_invulnerable = None
        if "Charge" in move.get("flags") and attacker.charged is False:
            if move.get("name") == "Skull Bash":
                print(f"{attacker.owner.name}'s {attacker.species} lowered it's head!")
                attacker.charged = True
                attacker.temp_stats["defense"] += 1
                print(f"{attacker.species}'s defense rose!")
                return
            elif move.get("name") == "Solar Beam":
                if self.weather == "sun":
                    print(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                else:
                    print(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                    attacker.charged = True
                    return
            elif move.get("name") == "Razor Wind":
                print(f"{attacker.owner.name}'s {attacker.species} whipped up a whirlwind!")
                attacker.charged = True
                return
            elif move.get("name") == "Sky Attack":
                print(f"{attacker.owner.name}'s {attacker.species} is glowing!")
                attacker.charged = True
                return
        elif "Charge" in move.get("flags"):
            attacker.charged = False
        print(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
        if defender is None and "Requires Target" in move.get("flags"):
            print("But it failed")
            return
        if defender.semi_invulnerable is not None:
            if (defender.semi_invulnerable == "bounce" or defender.semi_invulnerable == "fly" and
                    "Bypass Fly" not in move.get("flags")):
                print(f"{attacker.species} Missed!")
                return
            elif defender.semi_invulnerable == "dig" and "Bypass Dig" not in move.get("flags"):
                print(f"{attacker.species} Missed!")
                return
            elif defender.semi_invulnerable == "dive" and "Bypass Dive" not in move.get("flags"):
                print(f"{attacker.species} Missed!")
                return
        if "OHKO" in move.get("flags"):
            if attacker.level < defender.level:
                print(f"{attacker.species} Missed!")
                return
            else:
                hit_check = random.randint(1, 100)
                accuracy = math.floor(30 + (attacker.level - defender.level))
                if hit_check <= accuracy:
                    defender.chp = 0
                    print("It's a one-hit KO!")
                    return
                else:
                    print(f"{attacker.species} Missed!")
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
            # Do Beat Up, Bide, Brick Break, Counter, Covet, Double Kick, Dragon Rage, Dream Eater, Endeavor, Eruption,
            # Fake Out, False Swipe, Flail, Focus Punch, Frustration, Hidden Power, Knock Off, Low Kick, Magnitude,
            # Mirror Coat, Night Shade, Outrage, Petal Dance, Pursuit, Rage, Rapid Spin, Return,Secret Power,
            # Seismic Toss, Snore, Struggle, Thief, Thrash, Tri Attack, Twineedle, Uproar, Water Spout, Fire Spin,
            # Sand Tomb, Thunder, Whirlpool, Bind, Clamp, Psywave, Doom Desire, Wrap, Bonemerang, Future Sight,
            # High Jump Kick, Ice Ball, Present, Rollout, Sonic Boom, Super Fang, Triple Kick, Fury Cutter, Jump Kick
            if "Multi-Hit" in move.get("flags"):
                hits = (random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5], k=1))[0]
                for hit in range(0, hits):
                    dmg = self.dmg_calc(attacker, defender, move)
                    defender.chp -= dmg
                    defender.damaged_this_turn = True
                    if defender.chp <= 0 or attacker.chp <= 0:
                        print(f"It hit {hit + 1} time(s)")
                        break
                if defender.chp > 0 and attacker.chp > 0:
                    print(f"It hit {hits} time(s)")
            else:
                dmg = self.dmg_calc(attacker, defender, move)
                defender.chp -= dmg
                defender.damaged_this_turn = True
            if "Secondary" in move.get("flags"):
                if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
                    self.change_stats(attacker, defender, move)
                if "Flinch" in move.get("flags"):
                    roll = random.uniform(0, 1)
                    if roll <= move.get("chance"):
                        defender.flinching = True
                if "Confuses" in move.get("flags"):
                    roll = random.uniform(0, 1)
                    if roll <= move.get("chance"):
                        defender.confused = True
                if "Status" in move.get("flags") and defender.status is None:
                    roll = random.uniform(0, 1)
                    if roll <= move.get("chance"):
                        if (move.get("status") == "burned"
                                and defender.type_one != "Fire" and defender.type_two != "Fire"):
                            defender.status = "burned"
                            print(f"{defender.owner.name}'s {defender.species} was burned!")
                        elif (move.get("status") == "frozen"
                              and defender.type_one != "Ice" and defender.type_two != "Ice"):
                            defender.status = "frozen"
                            print(f"{defender.owner.name}'s {defender.species} was frozen!")
                        elif move.get("status") == "paralyzed":
                            defender.status = "paralyzed"
                            print(f"{defender.owner.name}'s {defender.species} was paralyzed!")
                        elif (move.get("status") == "poisoned" and defender.type_one != "Poison"
                              and defender.type_two != "Poison" and defender.type_one != "Steel"
                              and defender.type_two != "Steel"):
                            defender.status = "poisoned"
                            print(f"{defender.owner.name}'s {defender.species} was poisoned!")
                        elif (move.get("status") == "badly poisoned" and defender.type_one != "Poison"
                              and defender.type_two != "Poison" and defender.type_one != "Steel"
                              and defender.type_two != "Steel"):
                            defender.status = "badly poisoned"
                            print(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
                        elif move.get("status") == "sleeping":
                            defender.status = "sleeping"
                            print(f"{defender.owner.name}'s {defender.species} is fast asleep")
                if "Leech" in move.get("flags"):
                    if math.floor(dmg * 0.5) == 0:
                        attacker.chp += 1
                        if attacker.chp > attacker.hp:
                            attacker.chp = attacker.hp
                    else:
                        attacker.chp += math.floor(dmg * 0.5)
                        if attacker.chp > attacker.hp:
                            attacker.chp = attacker.hp
                if "Recoil" in move.get("flags"):
                    attacker.chp -= math.floor(dmg * move.get("amount"))
                    print(f"{attacker.owner.name}'s {attacker.species} is hit with recoil!")
                if "Recharge" in move.get("flags"):
                    attacker.recharge = True

    def non_dmg_move(self, attacker, defender, move):
        # Do Aromatherapy, Assist, Baton Pass, Block, Camouflage, Conversion, Conversion 2, Curse, Destiny Bond, Detect,
        # Endure, Grudge, Hail, Haze, Heal Bell, Imprison, Ingrain, Light Screen, Magic Coat, Mean Look, Memento,
        # Metronome, Mimic, Mirror Move, Mist, Moonlight, Morning Sun, Mud Sport, Nightmare, Pain Split, Perish Song,
        # Protect, Psych Up, Rain Dance, Recycle, Reflect, Refresh, Rest, Role Play, Safeguard, Sandstorm, Sketch,
        # Skill Swap, Sleep Talk, Snatch, Spider Web, Spikes, Substitute, Sunny Day, Synthesis,
        # Teleport, Transform, Water Sport, Wish, Yawn, Attract, Encore, Foresight, Lock-On, Mind Reader, Odor Sleuth,
        # Spite, Taunt, Torment, Trick, Whirlwind, Disable, Leech Seed, Nature Power
        if move.get("name") == "Minimize":
            attacker.minimized = True
        if move.get("name") == "Focus Energy":
            attacker.getting_pumped = True
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            self.change_stats(attacker, defender, move)
        if "Confuses" in move.get("flags"):
            defender.confused = True
            print(f"{defender.owner.name}'s {defender.species} became confused!")
        if "Status" in move.get("flags") and defender.status is None:
            if (move.get("status") == "burned"
                    and defender.type_one != "Fire" and defender.type_two != "Fire"):
                defender.status = "burned"
                print(f"{defender.owner.name}'s {defender.species} was burned!")
            elif (move.get("status") == "frozen"
                  and defender.type_one != "Ice" and defender.type_two != "Ice"):
                defender.status = "frozen"
                print(f"{defender.owner.name}'s {defender.species} was frozen!")
            elif move.get("status") == "paralyzed":
                defender.status = "paralyzed"
                print(f"{defender.owner.name}'s {defender.species} was paralyzed!")
            elif (move.get("status") == "poisoned" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                defender.status = "poisoned"
                print(f"{defender.owner.name}'s {defender.species} was poisoned!")
            elif (move.get("status") == "badly poisoned" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                defender.status = "badly poisoned"
                print(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
            elif move.get("status") == "sleeping":
                defender.status = "sleeping"
                print(f"{defender.owner.name}'s {defender.species} is fast asleep")
        if "Lowers Attacker chp by hp" in move.get("flags"):
            if attacker.chp - math.floor(attacker.hp * move.get("hp changes")) <= 0:
                print("But it failed")
                return
            else:
                attacker.chp -= math.floor(attacker.hp * move.get("hp changes"))
        if "Raises Attacker chp by hp" in move.get("flags"):
            if move.get("name") == "Swallow":
                if attacker.stockpile <= 0:
                    print("But it failed")
                    return
                else:
                    hp_change = [0.25, 0.50, 1]
                    attacker.chp += math.floor(attacker.hp * hp_change[attacker.stockpile - 1])
                    attacker.stockpile = 0
            else:
                attacker.chp += math.floor(attacker.hp * move.get("hp changes"))
            if attacker.chp > attacker.hp:
                attacker.chp = attacker.hp
        if move.get("name") == "Charge":
            attacker.charge = True
            return
        if move.get("name") == "Stockpile":
            if attacker.stockpile >= 3:
                print("But it failed")
                return
            else:
                attacker.stockpile += 1
                print(f"{attacker.owner.name}'s {attacker.species} stockpiled {attacker.stockpile}!")

    def change_stats(self, attacker, defender, move):
        rng = random.uniform(0, 1)
        if rng <= move.get("chance"):
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
                for key in list(move.get("stat changes").keys()):
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

    def dmg_calc(self, attacker, defender, move):
        if "Cant Crit" in move.get("flags"):
            crit = False
        else:
            crit = self.crit_check(attacker, move)
        if move.get("name") == "Weather Ball" and self.weather != "clear":
            if self.weather == "sun":
                dmg_type = "Special"
                move_type = "Fire"
            elif self.weather == "rain":
                dmg_type = "Special"
                move_type = "Water"
            elif self.weather == "hail":
                dmg_type = "Special"
                move_type = "Ice"
            elif self.weather == "sand":
                dmg_type = "Physical"
                move_type = "Rock"
            else:
                dmg_type = move.get("category")
                move_type = move.get("type")
        else:
            dmg_type = move.get("category")
            move_type = move.get("type")
        if dmg_type == "Physical":
            if crit:
                atk = attacker.attack
                dfn = defender.defense
            else:
                atk = math.floor(attacker.attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("attack")))
                dfn = math.floor(defender.defense * self.temp_stat_table_norm.get(defender.temp_stats.get("defense")))
            if "Explode" in move.get("flags"):
                dfn = math.floor(dfn * 0.5)
        else:
            if crit:
                atk = attacker.sp_attack
                dfn = defender.sp_defense
            else:
                atk = math.floor(attacker.sp_attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
                dfn = math.floor(defender.sp_defense * self.temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
        if not move.get("name") != "Solar Beam" and self.weather != "sun" and self.weather != "clear":
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
        else:
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("power")) / dfn) / 50)
        if attacker.status == "burned" and dmg_type == "Physical":
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
        if move.get("name") == "Spit Up":
            if attacker.stockpile <= 0:
                print("But it failed")
                return 0
            else:
                total = math.floor(total * attacker.stockpile)
                attacker.stockpile = 0
        if crit:
            total = math.floor(total * 2)
        if defender.semi_invulnerable is not None and "Double Damage" in move.get("flags"):
            total = math.floor(total * 2)
        if defender.minimized and "Double Minimized" in move.get("flags"):
            total = math.floor(total * 2)
        if (move.get("name") == "Facade" and
                attacker.status == "burned" or attacker.status == "paralyzed" or attacker.status == "poisoned"):
            total = math.floor(total * 2)
        if move.get("name") == "Smelling Salts" and defender.status == "paralyzed":
            total = math.floor(total * 2)
            defender.status = None
        if move.get("name") == "Revenge" and attacker.damaged_this_turn:
            total = math.floor(total * 2)
        if move.get("name") == "Weather Ball" and self.weather != "clear":
            total = math.floor(total * 2)
        if attacker.charge and move_type == "Electric":
            total = math.floor(total * 2)
            attacker.charge = False
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
        if move.get("name") != "Spit Up":
            total = math.floor((total * random.randint(85, 100)) / 100)
        if total == 0:
            total = 1
        return total

    def crit_check(self, attacker, move):
        crit_roll = random.uniform(0, 1)
        if "High Crit" in move.get("flags") and attacker.getting_pumped:
            if crit_roll <= 0.3333:
                print("A critical hit")
                return True
            return False
        elif attacker.getting_pumped:
            if crit_roll <= 0.2500:
                print("A critical hit")
                return True
            return False
        elif "High Crit" in move.get("flags"):
            if crit_roll <= 0.1250:
                print("A critical hit")
                return True
            return False
        else:
            if crit_roll <= 0.0625:
                print("A critical hit")
                return True
            return False

    def alive_check(self):
        if self.player_active is None or self.player_active.chp <= 0:
            self.player.team.remove(self.player_active)
            if not self.player.team:
                print(f"{self.opponent.name} Wins!")
                return True
            self.player_active = None
            while self.player_active is None:
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
                                self.player_active = self.player.team[x - 1]
                                print(f"{self.player.name} sent out {self.player_active.species}")
                                break
                            if z == 2:
                                break
                    if y == 1:
                        self.player_active = self.player.team[x - 1]
                        print(f"{self.player.name} sent out {self.player_active.species}")
                        break
        if self.opponent_active.chp <= 0 or self.opponent_active is None:
            self.opponent.team.remove(self.opponent_active)
            if not self.opponent.team:
                print(f"{self.player.name} Wins!")
                return True
            self.opponent_active = None
            self.opponent_active = random.choice(self.opponent.team)
            print(f"{self.opponent.name} sent out {self.opponent_active.species}")
