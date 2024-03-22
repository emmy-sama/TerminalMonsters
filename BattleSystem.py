from Classes import *
from bearlibterminal import terminal
import time


def dmg_range(total):
    for n in range(85, 101):
        print(math.floor(total * (n / 100)))


def print_txt(txt, delay=1.5):
    if len(txt) > 126:
        txt = txt[0:42] + "\n" + txt[42:84] + "\n" + txt[84:126] + "\n" + txt[126:]
    elif len(txt) > 84:
        txt = txt[0:42] + "\n" + txt[42:84] + "\n" + txt[84:]
    elif len(txt) > 42:
        txt = txt[0:42] + "\n" + txt[42:]
    terminal.clear_area(1, 20, 42, 4)
    terminal.printf(1, 20, txt)
    terminal.refresh()
    time.sleep(delay)


def can_attack(trainer_mon):
    if (trainer_mon.semi_invulnerable is None and trainer_mon.charged is False and trainer_mon.bide == 0 and
            trainer_mon.outraging == 0 and trainer_mon.uproar == 0 and trainer_mon.rolling == 0):
        return True
    
    
def crit_check(attacker, move):
    crit_roll = random.uniform(0, 1)
    if "High Crit" in move.get("flags") and attacker.getting_pumped:
        if crit_roll <= 0.3333:
            print_txt("[color=red]A critical hit[/color]")
            return True
        return False
    elif attacker.getting_pumped:
        if crit_roll <= 0.2500:
            print_txt("[color=red]A critical hit[/color]")
            return True
        return False
    elif "High Crit" in move.get("flags"):
        if crit_roll <= 0.1250:
            print_txt("[color=red]A critical hit[/color]")
            return True
        return False
    else:
        if crit_roll <= 0.0625:
            print_txt("[color=red]A critical hit[/color]")
            return True
        return False
    

def change_stats(attacker, defender, move):
    if move == "Rage":
        defender.temp_stats["attack"] += 1
        if defender.temp_stats["attack"] > 6:
            defender.temp_stats["attack"] = 6
        return
    rng = random.uniform(0, 1)
    if rng <= move.get("chance"):
        if "Changes Attacker Stats" in move.get("flags"):
            for key in list(move.get("stat changes").keys()):
                attacker.temp_stats[key] += move.get("stat changes").get(key)
                if move.get("stat changes").get(key) > 1:
                    print_txt(f"{attacker.species}'s {key} rose sharply!")
                elif move.get("stat changes").get(key) == 1:
                    print_txt(f"{attacker.species}'s {key} rose!")
                if move.get("stat changes").get(key) == -1:
                    print_txt(f"{attacker.species}'s {key} fell!")
                elif move.get("stat changes").get(key) < -1:
                    print_txt(f"{attacker.species}'s {key} harshly fell!")
                if attacker.temp_stats[key] >= 6:
                    attacker.temp_stats[key] = 6
                    print_txt(f"{attacker.species}'s {key} wont go any higher!")
                elif attacker.temp_stats[key] <= -6:
                    attacker.temp_stats[key] = -6
                    print_txt(f"{attacker.species}'s {key} wont go any lower!")
        if "Changes Defender Stats" in move.get("flags"):
            for key in list(move.get("stat changes").keys()):
                if defender.owner.mist > 0 > move.get("stat changes").get(key):
                    print_txt(f"{defender.species} was protected by the mist")
                    continue
                defender.temp_stats[key] += move.get("stat changes").get(key)
                if move.get("stat changes").get(key) > 1:
                    print_txt(f"{defender.species}'s {key} rose sharply!")
                elif move.get("stat changes").get(key) == 1:
                    print_txt(f"{defender.species}'s {key} rose!")
                if move.get("stat changes").get(key) == -1:
                    print_txt(f"{defender.species}'s {key} fell!")
                elif move.get("stat changes").get(key) < -1:
                    print_txt(f"{defender.species}'s {key} harshly fell!")
                if defender.temp_stats[key] >= 6:
                    defender.temp_stats[key] = 6
                    print_txt(f"{defender.species}'s {key} wont go any higher!")
                elif defender.temp_stats[key] <= -6:
                    defender.temp_stats[key] = -6
                    print_txt(f"{defender.species}'s {key} wont go any lower!")


class Battle:
    def __init__(self, player, ai):
        self.temp_stat_table_norm = {-6: 2 / 8, -5: 2 / 7, -4: 2 / 6, -3: 2 / 5, -2: 2 / 4, -1: 2 / 3, 0: 2 / 2,
                                     1: 3 / 2, 2: 4 / 2,
                                     3: 5 / 2, 4: 6 / 2, 5: 7 / 2, 6: 8 / 2}
        self.temp_stat_table_acc_eva = {-6: 33 / 100, -5: 36 / 100, -4: 43 / 100, -3: 50 / 100, -2: 60 / 100,
                                        -1: 75 / 100, 0: 100 / 100, 1: 133 / 100, 2: 166 / 100, 3: 200 / 100,
                                        4: 250 / 100, 5: 266 / 100, 6: 300 / 100}
        self.moves = moves
        self.types = types
        self.player = player
        self.player.active = player.team[0]
        self.ai = ai
        self.ai.active = ai.team[0]
        self.player.opponent = self.ai
        self.ai.opponent = self.ai
        self.weather = "clear"
        self.p_move = None
        self.p_move_last = None
        self.ai_move = None
        self.ai_move_last = None

    def print_ui(self):
        terminal.layer(0)
        terminal.put(0, 0, 0xF8FF)
        terminal.layer(1)
        if self.player.active is not None and self.ai.active is not None:
            terminal.put(68, 5, int(self.ai.active.front_sprite, 16))
        if self.player.active is not None and self.ai.active is not None:
            terminal.put(23, 14, int(self.player.active.back_sprite, 16))
        if self.player.active is not None and self.ai.active is not None:
            self.hp_bars()
        terminal.refresh()

    def battle(self):
        while True:
            self.clean_up()
            self.print_ui()
            if can_attack(self.ai.active):
                if self.ai.active.recharge:
                    self.ai_move = None
                    self.ai.active.recharge = False
                    print_txt(f"{self.ai.name}'s {self.ai.active.species} must recharge!")
                else:
                    self.ai_move = self.ai_turn()
            if can_attack(self.player.active):
                if self.player.active.recharge:
                    self.p_move = None
                    self.player.active.recharge = False
                    print_txt(f"{self.player.name}'s {self.player.active.species} must recharge!")
                else:
                    self.p_move = None
                    self.player_turn()
                    terminal.clear_area(45, 20, 42, 4)
            if self.p_move is not None and self.p_move.get("name") == "Focus Punch":
                print_txt(f"{self.player.name}'s {self.player.active.species} is tightening its focus!")
            if self.ai_move is not None and self.ai_move.get("name") == "Focus Punch":
                print_txt(f"{self.ai.name}'s {self.ai.active.species} is tightening its focus!")
            if self.p_move is not None and self.ai_move is not None:
                order = self.speed_check()
                if order[0].active is not None:
                    self.action(order[0].active, order[2].active, order[1])
                if order[2].active is not None:
                    self.action(order[2].active, order[0].active, order[3])
            elif self.ai_move is not None and self.ai.active is not None:
                self.action(self.ai.active, self.player.active, self.ai_move)
            elif self.p_move is not None and self.player.active is not None:
                self.action(self.player.active, self.ai.active, self.p_move)
            self.turn_end()

    def ai_turn(self):
        ai_random = random.choice(self.ai.active.moves)
        return self.moves.get(ai_random)

    def player_turn(self):
        while True:
            terminal.clear_area(45, 20, 60, 4)
            terminal.printf(45, 20, "1 Fight\n2 Pokemon")
            print_txt("What will you do?", 0)
            button = terminal.read()
            if button == terminal.TK_1:
                if self.print_moves(self.player.team.index(self.player.active)):
                    break
            elif button == terminal.TK_2:
                if self.player_swap(False):
                    break

    def print_moves(self, slot, swap=False):
        terminal.clear_area(45, 20, 42, 4)
        y = 19
        for num in range(0, 4):
            y += 1
            if num <= len(self.player.team[slot].moves) - 1:
                move = self.moves.get(self.player.team[slot].moves[num])
                terminal.printf(45, y, f"{num + 1} {move.get("name")} {move.get("type")} "
                                       f"Pwr:{move.get("power")} Acc:{move.get("accuracy")}")
            else:
                terminal.printf(45, y, "Empty Slot")
        if not swap:
            while True:
                print_txt("What move would you like to use?(1-4)", 0)
                button = terminal.read()
                if button == terminal.TK_1:
                    if self.print_move(0):
                        return True
                elif button == terminal.TK_2 and 2 <= len(self.player.active.moves):
                    if self.print_move(1):
                        return True
                elif button == terminal.TK_3 and 3 <= len(self.player.active.moves):
                    if self.print_move(2):
                        return True
                elif button == terminal.TK_4 and 4 <= len(self.player.active.moves):
                    if self.print_move(3):
                        return True
                elif button == terminal.TK_BACKSPACE:
                    return False

    def print_move(self, slot):
        move = self.moves.get(self.player.active.moves[slot])
        print_txt(f"Use {move.get("name")}?(Enter/Backspace) {move.get("description")}", 0)
        while True:
            button = terminal.read()
            if button == terminal.TK_ENTER:
                self.p_move = move
                return True
            elif button == terminal.TK_BACKSPACE:
                return False

    def player_swap(self, must_swap):
        while True:
            terminal.layer(0)
            terminal.put(0, 0, 0xF8FD)
            terminal.layer(1)
            terminal.clear_area(45, 17, 42, 7)
            y = 17
            for num in range(0, 6):
                y += 1
                if num <= len(self.player.team) - 1:
                    terminal.printf(45, y, f"{num + 1} {self.player.team[num]}")
                else:
                    terminal.printf(45, y, "Empty Slot")
            print_txt("What Pokemon would you like to view/swap? (1-6)", 0)
            button = terminal.read()
            if button == terminal.TK_1:
                if self.print_pokemon(0):
                    return True
            elif button == terminal.TK_2 and 2 <= len(self.player.team):
                if self.print_pokemon(1):
                    return True
            elif button == terminal.TK_3 and 3 <= len(self.player.team):
                if self.print_pokemon(2):
                    return True
            elif button == terminal.TK_4 and 4 <= len(self.player.team):
                if self.print_pokemon(3):
                    return True
            elif button == terminal.TK_5 and 5 <= len(self.player.team):
                if self.print_pokemon(4):
                    return True
            elif button == terminal.TK_6 and 6 <= len(self.player.team):
                if self.print_pokemon(5):
                    return True
            elif button == terminal.TK_BACKSPACE and not must_swap:
                terminal.clear_area(45, 17, 42, 7)
                self.print_ui()
                break

    def print_pokemon(self, slot):
        while True:
            terminal.clear_area(45, 17, 42, 7)
            self.print_ui()
            self.print_moves(slot, True)
            print_txt(f"Swap to {self.player.team[slot].species}?(Enter/Backspace)"
                      f"{self.player.team[slot].info}", 0)
            button = terminal.read()
            if button == terminal.TK_ENTER:
                if self.ai.active.trapping[0] != 0:
                    print_txt(f"{self.player.active.species} is trapped and cant switch out!")
                    break
                if self.ai.active.blocking:
                    print_txt(f"{self.player.active.species} is trapped and cant switch out!")
                    break
                if self.player.active == self.player.team[slot]:
                    print_txt(f"{self.player.team[slot].species} is already out")
                    break
                if self.player.active is not None:
                    self.player.active.reset_temp()
                self.player.active = self.player.team[slot]
                self.player.active.first_turn = True
                terminal.clear_area(45, 20, 42, 4)
                print_txt(f"{self.player.name} sent out {self.player.active.species}")
                return True
            if button == terminal.TK_BACKSPACE:
                return False

    def speed_check(self):
        if self.p_move.get("priority") > self.ai_move.get("priority"):
            return [self.player, self.p_move, self.ai, self.ai_move]
        if self.ai_move.get("priority") > self.p_move.get("priority"):
            return [self.ai, self.ai_move, self.player, self.p_move]
        player_speed = math.floor(self.player.active.speed *
                                  self.temp_stat_table_norm.get(self.player.active.temp_stats.get("speed")))
        if self.player.active.status == "PAR":
            player_speed = math.floor(player_speed * 0.25)
        ai_speed = math.floor(self.ai.active.speed *
                              self.temp_stat_table_norm.get(self.ai.active.temp_stats.get("speed")))
        if self.ai.active.status == "PAR":
            ai_speed = math.floor(ai_speed * 0.25)
        if player_speed > ai_speed:
            return [self.player, self.p_move, self.ai, self.ai_move]
        if ai_speed > player_speed:
            return [self.ai, self.ai_move, self.player, self.p_move]
        speed_tie = random.randint(0, 1)
        if speed_tie == 0:
            return [self.player, self.p_move, self.ai, self.ai_move]
        return [self.ai, self.ai_move, self.player, self.p_move]

    def action(self, attacker, defender, move):
        if attacker.uproar != 0:
            attacker.uproar -= 1
        if attacker.flinching:
            attacker.flinching = False
            attacker.charged = False
            print_txt(f"{attacker.owner.name}'s {attacker.species} flinched!")
            attacker.acted = True
            return
        if attacker.confused:
            pass
            # attacker.outraging = 0
        if attacker.status == "SLP" or move.get("name") == "Snore" or move.get("name") == "Sleep Talk":
            if move.get("name") == "Snore":
                if attacker.status == "SLP":
                    pass
                else:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    print_txt("But it failed")
                    return
            elif move.get("name") == "Sleep Talk":
                if attacker.status == "SLP":
                    print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    valid_moves = []
                    for attacks in attacker.moves:
                        for attack in moves:
                            if attack.get("name") == attacks:
                                if "No Sleep Talk" in attack.get("flags"):
                                    break
                                else:
                                    valid_moves.append(attack)
                                    break
                    if not valid_moves:
                        print_txt("But it failed")
                        return
                    move = random.choice(valid_moves)
                else:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    print_txt("But it failed")
                    return
            else:
                if attacker.sleep_turns == 0:
                    attacker.sleep_turns = random.randint(2, 6)
                attacker.sleep_turn -= 1
                if attacker.sleep_turns == 0 or defender.uproar != 0:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} woke up!")
                else:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} is fast asleep!")
                    attacker.acted = True
                    return
        if attacker.status == "FRZ":
            if random.randint(1, 100) <= 20 or "Thaws" in move.get("flags"):
                attacker.status = ""
                print_txt(f"{attacker.owner.name}'s {attacker.species} thawed it's self out!")
            else:
                print_txt(f"{attacker.owner.name}'s {attacker.species} is frozen solid!")
                attacker.acted = True
                return
        if attacker.status == "SLP":
            pass
        if attacker.status == "PAR":
            if random.randint(1, 100) <= 25:
                print_txt(f"{attacker.owner.name}'s {attacker.species} is paralyzed! It can't move!")
                attacker.outraging = 0
                attacker.acted = True
                return
            else:
                pass
        if move.get("name") == "Assist":
            choices = []
            for poke in attacker.owner.team:
                if poke == attacker:
                    continue
                for entry in poke.moves:
                    attack = self.moves.get(entry)
                    if "No Assist" not in attack.get("flags"):
                        choices.append(attack)
                        break
                    break
            if not choices:
                print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                print_txt("But it failed")
                attacker.acted = True
                return
            else:
                print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                move = random.choice(choices)
        if move.get("name") == "Metronome":
            while True:
                move = random.choice(list(self.moves.values()))
                if "Metronome" in move.get("flags"):
                    break
        if "Outrage" in move.get("flags"):
            if attacker.outraging == 2:
                attacker.outraging = 0
            elif attacker.outraging == 1:
                if random.randint(0, 1) == 0:
                    attacker.outraging += 1
                else:
                    attacker.outraging = 0
            else:
                attacker.outraging = 1
        if "Semi-invulnerable" in move.get("flags") and attacker.semi_invulnerable is None:
            if move.get("name") == "Bounce":
                attacker.semi_invulnerable = "bounce"
                print_txt(f"{attacker.owner.name}'s {attacker.species} sprang up!")
                attacker.acted = True
                return
            if move.get("name") == "Dig":
                attacker.semi_invulnerable = "dig"
                print_txt(f"{attacker.owner.name}'s {attacker.species} dug a hole!")
                attacker.acted = True
                return
            if move.get("name") == "Dive":
                attacker.semi_invulnerable = "dive"
                print_txt(f"{attacker.owner.name}'s {attacker.species} hide underwater!")
                attacker.acted = True
                return
            if move.get("name") == "Fly":
                attacker.semi_invulnerable = "fly"
                print_txt(f"{attacker.owner.name}'s {attacker.species} flew up high!")
                attacker.acted = True
                return
        elif "Semi-invulnerable" in move.get("flags"):
            attacker.semi_invulnerable = None
        if "Charge" in move.get("flags") and attacker.charged is False:
            if move.get("name") == "Skull Bash":
                print_txt(f"{attacker.owner.name}'s {attacker.species} lowered it's head!")
                attacker.charged = True
                attacker.temp_stats["defense"] += 1
                print_txt(f"{attacker.species}'s defense rose!")
                attacker.acted = True
                return
            elif move.get("name") == "Solar Beam":
                if self.weather == "sun":
                    print_txt(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                else:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                    attacker.charged = True
                    attacker.acted = True
                    return
            elif move.get("name") == "Razor Wind":
                print_txt(f"{attacker.owner.name}'s {attacker.species} whipped up a whirlwind!")
                attacker.charged = True
                attacker.acted = True
                return
            elif move.get("name") == "Sky Attack":
                print_txt(f"{attacker.owner.name}'s {attacker.species} is glowing!")
                attacker.charged = True
                attacker.acted = True
                return
        elif "Charge" in move.get("flags"):
            attacker.charged = False
        if move.get("name") == "Bide" and attacker.bide != 0:
            if attacker.bide == 1:
                print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
                attacker.bide = 2
                attacker.acted = True
                return
            else:
                print_txt(f"{attacker.owner.name}'s {attacker.species} unleashed energy")
                attacker.bide = 0
                attacker.acted = True
                if attacker.bide_dmg == 0:
                    print_txt("But it failed")
                elif defender.protecting:
                    print_txt(f"{defender.species} protected it's self")
                else:
                    if defender.enduring and attacker.bide_dmg * 2 >= defender.chp:
                        self.deal_dmg(defender, defender.chp - 1)
                    else:
                        self.deal_dmg(defender, (attacker.bide_dmg * 2))
                    if defender.bide != 0:
                        defender.bide_dmg += (attacker.bide_dmg * 2)
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = (attacker.bide_dmg * 2)
                attacker.bide_dmg = 0
                return
        print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
        if defender is None:
            if ("Requires Target" in move.get("flags") or move.get("category") == "Special"
                    or move.get("category") == "Physical"):
                print_txt("But it failed")
                attacker.acted = True
                return
        if defender.protecting and "Protect" in move.get("flags"):
            print_txt(f"{defender.species} protected it's self")
            attacker.acted = True
            if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                dmg = self.dmg_calc(attacker, defender, move)
                self.deal_dmg(attacker, (dmg / 2))
                attacker.dmg_last_type_taken = None
                attacker.dmg_last_taken = dmg / 2
            elif move.get("name") == "Explosion" or move.get("name") == "Self-Destruct":
                self.deal_dmg(attacker, 999)
            elif attacker.rage and move.get("name") != "Rage":
                attacker.rage = False
            elif move.get("name") == "Rage":
                attacker.rage = True
            return
        if move.get("type") == "Ghost":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Normal" or defender.type_two == "Normal":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Ground":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Flying" or defender.type_two == "Flying":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Electric":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ground" or defender.type_two == "Ground":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Normal":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Fighting":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Poison":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Steel" or defender.type_two == "Steel":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Psychic":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Dark" or defender.type_two == "Dark":
                    print_txt("It had no effect")
                    attacker.acted = True
                    return
        if move.get("name") == "Counter":
            if attacker.dmg_last_taken > 0 and attacker.dmg_last_type_taken == "Physical":
                if defender.enduring and attacker.dmg_last_taken * 2 >= defender.chp:
                    self.deal_dmg(defender, defender.chp - 1)
                else:
                    self.deal_dmg(defender, (attacker.dmg_last_taken * 2))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.dmg_last_taken * 2
                if defender.bide != 0:
                    defender.bide_dmg += attacker.dmg_last_taken * 2
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                return
            else:
                print_txt("But it failed")
                return
        if move.get("name") == "Mirror Coat":
            if attacker.dmg_last_taken > 0 and attacker.dmg_last_type_taken == "Special":
                if defender.enduring and attacker.dmg_last_taken * 2 >= defender.chp:
                    self.deal_dmg(defender, defender.chp - 1)
                else:
                    self.deal_dmg(defender, (attacker.dmg_last_taken * 2))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.dmg_last_taken * 2
                if defender.bide != 0:
                    defender.bide_dmg += attacker.dmg_last_taken * 2
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                return
            else:
                print_txt("But it failed")
                return
        if move.get("name") == "Focus Punch" and attacker.damaged_this_turn:
            print_txt("But it failed")
            attacker.acted = True
            return
        if defender.semi_invulnerable is not None:
            if (defender.semi_invulnerable == "bounce" or defender.semi_invulnerable == "fly" and
                    "Bypass Fly" not in move.get("flags")):
                print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                attacker.outraging = 0
                attacker.acted = True
                return
            elif defender.semi_invulnerable == "dig" and "Bypass Dig" not in move.get("flags"):
                print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                attacker.outraging = 0
                attacker.acted = True
                return
            elif defender.semi_invulnerable == "dive" and "Bypass Dive" not in move.get("flags"):
                print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                attacker.outraging = 0
                attacker.acted = True
                return
        if "OHKO" in move.get("flags"):
            if attacker.level < defender.level:
                print_txt(f"{attacker.species} Missed!")
                attacker.acted = True
                return
            else:
                hit_check = random.randint(1, 100)
                accuracy = math.floor(30 + (attacker.level - defender.level))
                if hit_check <= accuracy:
                    self.deal_dmg(defender, 999)
                    print_txt("It's a one-hit KO!")
                    attacker.acted = True
                    return
                else:
                    print_txt(f"{attacker.species} Missed!")
                    attacker.acted = True
                    return
        if attacker.rage and move.get("name") != "Rage":
            attacker.rage = False
        elif move.get("name") == "Rage":
            attacker.rage = True
        if move.get("name") == "Thunder" and self.weather == "rain":
            pass
        elif move.get("name") == "Thunder" and self.weather == "sun":
            hit_check = random.randint(1, 100)
            accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
            if accuracy_stage > 6:
                accuracy_stage = 6
            elif accuracy_stage < -6:
                accuracy_stage = -6
            accuracy = 50 * self.temp_stat_table_acc_eva.get(accuracy_stage)
            if hit_check > accuracy:
                print_txt(f"{attacker.species} Missed!")
                attacker.acted = True
                return
        elif move.get("accuracy") != 0:
            hit_check = random.randint(1, 100)
            accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
            if accuracy_stage > 6:
                accuracy_stage = 6
            elif accuracy_stage < -6:
                accuracy_stage = -6
            accuracy = move.get("accuracy") * self.temp_stat_table_acc_eva.get(accuracy_stage)
            if hit_check > accuracy:
                print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                attacker.outraging = 0
                attacker.acted = True
                return
        if move.get("name") == "Brick Break":
            if defender.owner.reflect > 0 or defender.owner.light_screen > 0:
                defender.owner.reflect = 0
                defender.owner.light_screen = 0
                print_txt("The wall shattered!")
        if move.get("name") == "Uproar" and attacker.uproar == 0:
            attacker.uproar = random.randint(2, 5)
        if move.get("name") == "Bide":
            attacker.bide = 1
            print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
            attacker.acted = True
            return
        if move.get("category") == "Non-Damaging":
            self.non_dmg_move(attacker, defender, move)
        else:
            # Do Secret Power, Covet, Knock Off, Thief, Struggle, Pursuit, Brick Break, Rapid Spin,
            # Doom Desire, Future Sight
            if "Multi-Hit" in move.get("flags"):
                hits = (random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5], k=1))[0]
                for hit in range(0, hits):
                    dmg = self.dmg_calc(attacker, defender, move)
                    if defender.enduring and dmg >= defender.chp:
                        dmg = defender.chp - 1
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    if defender.chp <= 0 or attacker.chp <= 0:
                        print_txt(f"It hit {hit + 1} time(s)")
                        break
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    print_txt(f"It hit {hits} time(s)")
            elif "Double-Hit" in move.get("flags"):
                for hit in range(0, 2):
                    dmg = self.dmg_calc(attacker, defender, move)
                    if defender.enduring and dmg >= defender.chp:
                        dmg = defender.chp - 1
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    if defender.chp <= 0 or attacker.chp <= 0:
                        print_txt("It hit 1 time(s)")
                        break
                    if "Secondary" in move.get("flags"):
                        self.secondary(attacker, defender, move, dmg)
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    print_txt("It hit 2 time(s)")
            elif move.get("name") == "Triple Kick":
                hits = 0
                for hit in range(3):
                    if hit > 0:
                        hit_check = random.randint(1, 100)
                        accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
                        if accuracy_stage > 6:
                            accuracy_stage = 6
                        elif accuracy_stage < -6:
                            accuracy_stage = -6
                        accuracy = move.get("accuracy") * self.temp_stat_table_acc_eva.get(accuracy_stage)
                        if hit_check > accuracy:
                            break
                    dmg = self.dmg_calc(attacker, defender, move)
                    if defender.enduring and dmg >= defender.chp:
                        dmg = defender.chp - 1
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    hits += 1
                    if defender.chp <= 0 or attacker.chp <= 0:
                        print_txt(f"It hit {hit + 1} time(s)")
                        break
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    print_txt(f"It hit {hits} time(s)")
                print_txt(f"It hit {hits} time(s)")
            elif move.get("name") == "Beat Up":
                for mon in attacker.owner.team:
                    if mon.status == "":
                        print_txt(f"{mon.species}'s attack!")
                        crit = crit_check(mon, move)
                        dmg = math.floor(math.floor((math.floor((2 * mon.level) / 5 + 2)
                                                     * mon.attack * 10) / defender.defense) / 50)
                        if mon.status == "BRN":
                            dmg = math.floor(dmg * 0.5)
                        if defender.owner.reflect and not crit:
                            dmg = math.floor(dmg * 0.5)
                        dmg += 2
                        if crit:
                            dmg = math.floor(dmg * 2)
                        dmg = math.floor((dmg * random.randint(85, 100)) / 100)
                        if dmg == 0:
                            dmg = 1
                        if defender.enduring and dmg >= defender.chp:
                            dmg = defender.chp - 1
                        self.deal_dmg(defender, dmg)
                        defender.dmg_last_type_taken = move.get("category")
                        defender.dmg_last_taken = dmg
                        if defender.bide != 0:
                            defender.bide_dmg += dmg
                        if defender.rage:
                            change_stats(attacker, defender, "Rage")
                        if defender.chp <= 0 or attacker.chp <= 0:
                            break
                defender.damaged_this_turn = True
            elif "Level Damage" in move.get("flags"):
                if defender.enduring and attacker.level >= defender.chp:
                    self.deal_dmg(defender, defender.chp - 1)
                else:
                    self.deal_dmg(defender, attacker.level)
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.level
                if defender.bide != 0:
                    defender.bide_dmg += attacker.level
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif "Fixed Damage" in move.get("flags"):
                if defender.enduring and move.get("amount") >= defender.chp:
                    self.deal_dmg(defender, defender.chp - 1)
                else:
                    self.deal_dmg(defender, move.get("amount"))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = move.get("amount")
                if defender.bide != 0:
                    defender.bide_dmg += move.get("amount")
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Psywave":
                ran = random.randint(0, 10)
                dmg = math.floor((attacker.level * (10 * ran + 50)) / 100)
                if dmg == 0:
                    dmg = 1
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                defender.dmg_last_type_taken = dmg
                defender.dmg_last_taken = dmg
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Super Fang":
                dmg = math.floor(defender.chp * 0.5)
                if dmg == 0:
                    dmg = 1
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = dmg
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Endeavor":
                if attacker.chp >= defender.chp:
                    print_txt("But it failed")
                else:
                    if defender.bide != 0:
                        defender.bide_dmg += (defender.chp - attacker.chp)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = (defender.chp - attacker.chp)
                    self.deal_dmg(defender, (defender.chp - attacker.chp))
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
            elif (move.get("name") == "Fake Out" and attacker.first_turn is False or
                  move.get("name") == "Fake Out" and defender.acted):
                print_txt("But it failed")
            elif move.get("name") == "Dream Eater" and defender.status != "SLP":
                print_txt("But it failed")
            elif move.get("name") == "Present":
                power = random.choices([0, 40, 80, 120], [20, 40, 30, 10], k=1)[0]
                if power > 0:
                    move["power"] = power
                    dmg = self.dmg_calc(attacker, defender, move)
                    if defender.enduring and dmg >= defender.chp:
                        dmg = defender.chp - 1
                    self.deal_dmg(defender, dmg)
                    if dmg > 0:
                        if defender.rage:
                            change_stats(attacker, defender, "Rage")
                        defender.damaged_this_turn = True
                        defender.dmg_last_type_taken = move.get("category")
                        defender.dmg_last_taken = dmg
                        if defender.bide != 0:
                            defender.bide_dmg += dmg
                else:
                    if defender.chp == defender.hp:
                        print_txt("It had no effect!")
                    else:
                        self.deal_dmg(defender, -math.floor(defender.hp / 4))
            elif move.get("name") == "Fury Cutter":
                if attacker.fury_cutter <= 3:
                    move["power"] = 10 * 2 ** attacker.fury_cutter
                else:
                    move["power"] = 160
                attacker.fury_cutter += 1
                attacker.fury_cutter_hit = True
                dmg = self.dmg_calc(attacker, defender, move)
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
            elif move.get("name") == "Rollout" or move.get("name") == "Ice Ball":
                move["power"] = 30 * 2 ** attacker.rolling
                dmg = self.dmg_calc(attacker, defender, move)
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                if attacker.rolling < 4:
                    attacker.rolling += 1
                    attacker.rolling_hit = True
                else:
                    attacker.rolling = 0
            else:
                dmg = self.dmg_calc(attacker, defender, move)
                if move.get("name") == "False Swipe" and dmg >= defender.chp:
                    dmg = defender.chp - 1
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                if "Secondary" in move.get("flags"):
                    self.secondary(attacker, defender, move, dmg)
        if "Outrage" in move.get("flags") and attacker.outraging == 0:
            if attacker.confused:
                print_txt(f"{attacker.owner.name}'s {attacker.species} is already confused!")
            else:
                print_txt(f"{attacker.owner.name}'s {attacker.species} became confused due to fatigue!")
                attacker.confused = True
        if defender.rage and defender.damaged_this_turn:
            print_txt(f"{defender.owner.name}'s {defender.species}'s rage is building!")
        if move.get("name") == "Uproar" and attacker.uproar == 1:
            print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
        elif move.get("name") == "Uproar" and attacker.uproar > 1:
            print_txt(f"{attacker.owner.name}'s {attacker.species} caused a uproar!")
        attacker.acted = True

    def non_dmg_move(self, attacker, defender, move):
        # Do Camouflage, Conversion, Conversion 2, Destiny Bond, Detect, Grudge,  Imprison, Ingrain, Magic Coat,
        # Memento, Mimic, Mirror Move, Nightmare, Pain Split, Perish Song, Recycle, Rest, Role Play, Safeguard, Sketch,
        # Skill Swap, Snatch, Spikes, Substitute, Teleport, Transform, Wish, Yawn, Attract, Encore, Foresight, Lock-On,
        # Mind Reader, Odor Sleuth, Spite, Taunt, Torment, Trick, Whirlwind, Disable, Leech Seed, Nature Power
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            change_stats(attacker, defender, move)
        if "Confuses" in move.get("flags"):
            defender.confused = True
            print_txt(f"{defender.owner.name}'s {defender.species} became confused!")
        if "Status" in move.get("flags"):
            if move.get("status") == "BRN":
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already burned!")
                elif defender.type_one != "Fire" and defender.type_two != "Fire":
                    defender.status = "BRN"
                    print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
                else:
                    print_txt("It has no effect!")
            elif move.get("status") == "FRZ":
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already frozen!")
                elif defender.type_one != "Ice" and defender.type_two != "Ice":
                    defender.status = "FRZ"
                    print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
                else:
                    print_txt("It has no effect!")
            elif move.get("status") == "PAR":
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already paralyzed!")
                else:
                    defender.status = "PAR"
                    print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
            elif (move.get("status") == "PSN" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                      defender.type_one != "Steel" and defender.type_two != "Steel"):
                    defender.status = "PSN"
                    print_txt(f"{defender.owner.name}'s {defender.species} was poisoned!")
                else:
                    print_txt("It has no effect!")
            elif (move.get("status") == "TOX" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                      defender.type_one != "Steel" and defender.type_two != "Steel"):
                    defender.status = "TOX"
                    defender.tox_turns = 0
                    print_txt(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
                else:
                    print_txt("It has no effect!")
            elif move.get("status") == "SLP":
                if defender.status != "":
                    print_txt(f"{defender.owner.name}'s {defender.species} is already asleep!")
                elif attacker.uproar != 0 or defender.uproar != 0:
                    print_txt(f"{defender.owner.name}'s {defender.species} cannot fall asleep due to the uproar!")
                else:
                    defender.status = "SLP"
                    print_txt(f"{defender.owner.name}'s {defender.species} is fast asleep")
        if "Lowers Attacker chp by hp" in move.get("flags"):
            if attacker.chp - math.floor(attacker.hp * move.get("hp changes")) <= 0:
                print_txt("But it failed")
                return
            else:
                self.deal_dmg(attacker, (math.floor(attacker.hp * move.get("hp changes"))))
        if "Raises Attacker chp by hp" in move.get("flags"):
            if move.get("name") == "Swallow":
                if attacker.stockpile <= 0:
                    print_txt("But it failed")
                    return
                else:
                    hp_change = [0.25, 0.50, 1]
                    self.deal_dmg(attacker, -math.floor(attacker.hp * hp_change[attacker.stockpile - 1]))
                    attacker.stockpile = 0
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp * move.get("hp changes")))
        if "Block" in move.get("flags"):
            if attacker.blocking:
                print_txt("But it failed")
            else:
                attacker.blocking = True
        elif "Weather" in move.get("flags"):
            if move.get("name") == "Hail":
                if self.weather == "hail":
                    print_txt("But it failed")
                else:
                    self.weather = "hail"
                    print_txt("It started to hail!")
            elif move.get("name") == "Rain Dance":
                if self.weather == "rain":
                    print_txt("But it failed")
                else:
                    self.weather = "rain"
                    print_txt("It started to rain!")
            elif move.get("name") == "Sandstorm":
                if self.weather == "sand":
                    print_txt("But it failed")
                else:
                    self.weather = "sand"
                    print_txt("A sand storm brewed!")
            elif move.get("name") == "Sunny Day":
                if self.weather == "sun":
                    print_txt("But it failed")
                else:
                    self.weather = "sun"
                    print_txt("The sun light got bright!")
        elif "Synthesis" in move.get("flags"):
            if self.weather == "clear":
                self.deal_dmg(attacker, -math.floor(attacker.hp / 2))
            elif self.weather == "sun":
                self.deal_dmg(attacker, -math.floor(attacker.hp * 0.66))
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp / 4))
        elif move.get("name") == "Psych Up":
            attacker.temp_stats.update(defender.temp_stats)
            print(attacker.temp_stats)
            print_txt(f"{attacker.owner.name}'s {attacker.species} copied it's opponents stat changes")
        elif move.get("name") == "Refresh":
            if attacker.status == "SLP" or attacker.status == "FRZ" or attacker.status == "":
                print_txt("But it failed")
            else:
                attacker.status = ""
                print_txt(f"{attacker.owner.name}'s {attacker.species} status returned to normal!")
        elif move.get("name") == "Haze":
            attacker.temp_stats = attacker.temp_stats.fromkeys(attacker.temp_stats.keys(), 0)
            defender.temp_stats = defender.temp_stats.fromkeys(defender.temp_stats.keys(), 0)
            print_txt("All stat changes were eliminated!")
        elif move.get("name") == "Protect" or move.get("name") == "Detect":
            if defender.acted:
                print_txt("But it failed")
            else:
                if attacker.protecting_chance >= random.uniform(0, 1):
                    attacker.protecting = True
                    print_txt(f"{attacker.species} is protecting it's self")
                else:
                    print_txt("But it failed")
        elif move.get("name") == "Endure":
            if defender.acted:
                print_txt("But it failed")
            else:
                if attacker.protecting_chance >= random.uniform(0, 1):
                    attacker.enduring = True
                    print_txt(f"{attacker.species} braced it's self!")
                else:
                    print_txt("But it failed")
        elif move.get("name") == "Reflect":
            if attacker.owner.reflect > 0:
                print_txt("But it failed")
            else:
                attacker.owner.reflect = 5
        elif move.get("name") == "Light Screen":
            if attacker.owner.light_screen > 0:
                print_txt("But it failed")
            else:
                attacker.owner.light_screen = 5
        elif move.get("name") == "Mist":
            if attacker.owner.mist > 0:
                print_txt("But it failed")
            else:
                attacker.owner.mist = 5
        elif move.get("name") == "Curse":
            if attacker.type_one == "Ghost" or attacker.type_two == "Ghost":
                self.deal_dmg(attacker, (math.floor(attacker.hp / 2)))
                defender.cursed = True
                print_txt(f"{attacker.owner.name}'s {attacker.species} cut its own HP in half and laid a curse on"
                          f" {defender.owner.name}'s {defender.species}")
            else:
                attacker.temp_stats["attack"] += 1
                print_txt(f"{attacker.species}'s attack rose!")
                attacker.temp_stats["defense"] += 1
                print_txt(f"{attacker.species}'s defense rose!")
                attacker.temp_stats["speed"] -= 1
                print_txt(f"{attacker.species}'s speed fell!")
        elif move.get("name") == "Water Sport":
            attacker.water_sport = True
            print_txt("Fire's power was weakened")
        elif move.get("name") == "Mud Sport":
            attacker.mud_sport = True
            print_txt("Electricity's power was weakened")
        elif move.get("name") == "Aromatherapy" or move.get("name") == "Heal Bell":
            for poke in attacker.owner.team:
                poke.status = ""
        elif move.get("name") == "Minimize":
            attacker.minimized = True
        elif move.get("name") == "Focus Energy":
            attacker.getting_pumped = True
        elif move.get("name") == "Charge":
            attacker.charge = True
        elif move.get("name") == "Stockpile":
            if attacker.stockpile >= 3:
                print_txt("But it failed")
                return
            else:
                attacker.stockpile += 1
                print_txt(f"{attacker.owner.name}'s {attacker.species} stockpiled {attacker.stockpile}!")
        elif move.get("name") == "Baton Pass":
            passer_temp_stats = attacker.temp_stats
            passer_confused = attacker.confused
            passer_getting_pumped = attacker.getting_pumped
            passer_blocking = attacker.blocking
            # passer_seeded = attacker.seeded
            # passer_curse = attacker.curse
            # passer_substitute  = attacker.substitute
            # passer_ingrain  = attacker.ingrain
            # passer_perish  = attacker.perish
            if attacker == self.player.active and len(self.player.team) > 1:
                self.player_swap(True)
                self.player.active.temp_stats = passer_temp_stats
                self.player.active.confused = passer_confused
                self.player.active.getting_pumped = passer_getting_pumped
                self.player.active.blocking = passer_blocking
                # self.player.active.seeded = passer_seeded
                # self.player.active.curse = passer_curse
                # self.player.active.substitute  = passer_substitute
                # self.player.active.ingrain  = passer_ingrain
                # self.player.active.perish  = passer_perish
            elif attacker == self.ai.active and len(self.ai.active) > 1:
                self.ai.active = random.choice(self.ai.team)
                print_txt(f"{self.ai.name} sent out {self.ai.active.species}")
                self.ai.active.temp_stats = passer_temp_stats
                self.ai.active.confused = passer_confused
                self.ai.active.getting_pumped = passer_getting_pumped
                self.ai.active.blocking = passer_blocking
                # self.ai.active.seeded = passer_seeded
                # self.ai.active.curse = passer_curse
                # self.ai.active.substitute  = passer_substitute
                # self.ai.active.ingrain  = passer_ingrain
                # self.ai.active.perish  = passer_perish
            else:
                print_txt("But it failed")

    def secondary(self, attacker, defender, move, dmg):
        if move.get("name") == "Tri Attack" and defender.status == "":
            roll = random.uniform(0, 1)
            if roll <= 0.0667:
                defender.status = "BRN"
                print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
                return
            elif roll <= 0.1334:
                defender.status = "PAR"
                print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
                return
            elif roll <= 0.2001:
                defender.status = "FRZ"
                print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
                return
            else:
                return
        if "Trapping" in move.get("flags"):
            attacker.trapping[0] = random.randint(2, 5)
            attacker.trapping[1] = move.get("name")
            if move.get("name") == "Fire Sping" or move.get("name") == "Whirlpool":
                print_txt(f"{defender.owner.name}'s {defender.species} was trapped in the vortex!")
            if move.get("name") == "Sand Tomb":
                print_txt(f"{defender.owner.name}'s {defender.species} was trapped by sand tomb!")
            if move.get("name") == "Clamp":
                print_txt(f"{defender.owner.name}'s {defender.species} was clamped by {attacker.species}!")
            if move.get("name") == "Bind":
                print_txt(f"{defender.owner.name}'s {defender.species} was squeezed by {attacker.species}'s bind!")
            if move.get("name") == "Wrap":
                print_txt(f"{defender.owner.name}'s {defender.species} was wrapped by {attacker.species}!")
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            change_stats(attacker, defender, move)
        if "Flinch" in move.get("flags") and not defender.acted:
            roll = random.uniform(0, 1)
            if roll <= move.get("chance"):
                defender.flinching = True
        if "Confuses" in move.get("flags"):
            roll = random.uniform(0, 1)
            if roll <= move.get("chance"):
                defender.confused = True
        if "Status" in move.get("flags"):
            if move.get("status") == "BRN":
                if defender.status != "":
                    pass
                elif defender.type_one != "Fire" and defender.type_two != "Fire":
                    if random.uniform(0, 1) <= move.get("chance"):
                        defender.status = "BRN"
                        print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
            elif move.get("status") == "FRZ":
                if defender.status != "":
                    pass
                elif defender.type_one != "Ice" and defender.type_two != "Ice":
                    if random.uniform(0, 1) <= move.get("chance"):
                        defender.status = "FRZ"
                        print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
            elif move.get("status") == "PAR":
                if defender.status != "":
                    pass
                else:
                    if random.uniform(0, 1) <= move.get("chance"):
                        defender.status = "PAR"
                        print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
            elif (move.get("status") == "PSN" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                if defender.status != "":
                    pass
                elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                      defender.type_one != "Steel" and defender.type_two != "Steel"):
                    if random.uniform(0, 1) <= move.get("chance"):
                        defender.status = "PSN"
                        print_txt(f"{defender.owner.name}'s {defender.species} was poisoned!")
            elif (move.get("status") == "TOX" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                if defender.status != "":
                    pass
                elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                      defender.type_one != "Steel" and defender.type_two != "Steel"):
                    if random.uniform(0, 1) <= move.get("chance"):
                        defender.status = "TOX"
                        defender.tox_turns = 0
                        print_txt(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
        if "Leech" in move.get("flags"):
            if math.floor(dmg * 0.5) == 0:
                self.deal_dmg(attacker, -1)
            else:
                self.deal_dmg(attacker, -math.floor(dmg * 0.5))
        if "Recoil" in move.get("flags"):
            self.deal_dmg(attacker, (math.floor(dmg * move.get("amount"))))
            print_txt(f"{attacker.owner.name}'s {attacker.species} is hit with recoil!")
        if "Recharge" in move.get("flags"):
            attacker.recharge = True

    def dmg_calc(self, attacker, defender, move):
        if "Cant Crit" in move.get("flags"):
            crit = False
        else:
            crit = crit_check(attacker, move)
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
        elif move.get("name") == "Hidden Power":
            move_type = attacker.hidden_type[0]
            dmg_type = attacker.hidden_type[1]
        else:
            dmg_type = move.get("category")
            move_type = move.get("type")
        # Fix Gen 1 Crit Bug
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
                atk = math.floor(attacker.sp_attack * 
                                 self.temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
                dfn = math.floor(defender.sp_defense * 
                                 self.temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
        if move_type == "Electric":
            if attacker.mud_sport or defender.mud_sport:
                move["power"] = math.floor(move.get("power") / 2)
        if move_type == "Fire":
            if attacker.water_sport or defender.water_sport:
                move["power"] = math.floor(move.get("power") / 2)
        if not move.get("name") != "Solar Beam" and self.weather != "sun" and self.weather != "clear":
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
        elif move.get("name") == "Eruption" or move.get("name") == "Water Spout":
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk 
                                           * (150 * attacker.chp / attacker.hp)) / dfn) / 50)
        elif move.get("name") == "Flail":
            attack_hp_percent = attacker.chp / attacker.hp
            if attack_hp_percent >= 0.6875:
                power = 20
            elif attack_hp_percent >= 0.3542:
                power = 40
            elif attack_hp_percent >= 0.2083:
                power = 80
            elif attack_hp_percent >= 0.1042:
                power = 100
            elif attack_hp_percent >= 0.0417:
                power = 150
            else:
                power = 200
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * power) / dfn) / 50)
        elif move.get("name") == "Low Kick":
            if defender.weight <= 9.9:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 20) / dfn) / 50)
            elif defender.weight <= 24.9:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 40) / dfn) / 50)
            elif defender.weight <= 49.9:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
            elif defender.weight <= 99.9:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 80) / dfn) / 50)
            elif defender.weight <= 199.9:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 100) / dfn) / 50)
            else:
                total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 120) / dfn) / 50)
        elif move.get("name") == "Magnitude":
            mag = random.choices([[4, 10], [5, 30], [6, 50], [7, 70], [8, 90], [9, 110], [10, 150]],
                                 weights=[5, 10, 20, 30, 20, 10, 5], k=1)[0]
            total = math.floor(
                math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * mag[1]) / dfn) / 50)
            print_txt(f"Magnitude {mag[0]}!")
        else:
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) 
                                           * atk * move.get("power")) / dfn) / 50)
        if attacker.status == "BRN" and dmg_type == "Physical":
            total = math.floor(total * 0.5)
        if defender.owner.reflect and dmg_type == "Physical" and not crit:
            total = math.floor(total * 0.5)
        if defender.owner.light_screen and dmg_type == "Special" and not crit:
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
                print_txt("But it failed")
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
        if move.get("name") == "Facade":
            if attacker.status == "BRN" or attacker.status == "PAR" or attacker.status == "PSN":
                total = math.floor(total * 2)
        if move.get("name") == "Smelling Salts" and defender.status == "PAR":
            total = math.floor(total * 2)
            defender.status = ""
        if move.get("name") == "Revenge" and attacker.damaged_this_turn:
            total = math.floor(total * 2)
        if move.get("name") == "Weather Ball" and self.weather != "clear":
            total = math.floor(total * 2)
        if attacker.charge and move_type == "Electric":
            total = math.floor(total * 2)
            attacker.charge = False
        if move_type == attacker.type_one or move_type == attacker.type_two:
            total = math.floor(total * 1.5)
        effectiveness = 1
        for item in self.types:
            if item["name"] == move_type:
                effectiveness = item.get(defender.type_one, 1)
                if defender.type_two is not None:
                    effectiveness = effectiveness * item.get(defender.type_two, 1)
                break
        if effectiveness >= 2 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            print_txt("It's super effective", 0)
        if effectiveness <= 0.5 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            print_txt("It's not very effective...", 0)
        total = math.floor(total * effectiveness)
        # dmg_range(total)
        if move.get("name") != "Spit Up":
            total = math.floor((total * random.randint(85, 100)) / 100)
        if total == 0:
            total = 1
        return total

    def alive_check(self):
        swapped = False
        if self.ai.active is None or self.ai.active.chp <= 0:
            if self.ai.active is not None:
                self.ai.team.remove(self.ai.active)
                print_txt(f"{self.ai.name}'s {self.ai.active.species} fainted!")
                self.ai.active = None
            if not self.ai.team:
                print_txt(f"{self.player.name} Wins!")
                return True
            self.ai.active = random.choice(self.ai.team)
            self.ai.active.first_turn = True
            swapped = True
        if self.player.active is None or self.player.active.chp <= 0:
            if self.player.active is not None:
                self.player.team.remove(self.player.active)
                print_txt(f"{self.player.name}'s {self.player.active.species} fainted!")
                self.player.active = None
            if not self.player.team:
                print_txt(f"{self.ai.name} Wins!")
                return True
            self.player_swap(True)
        if swapped:
            print_txt(f"{self.ai.name} sent out {self.ai.active.species}")

    def deal_dmg(self, victim, amount):
        hp_symbol = "█"
        lost_hp = "░"
        bars = 20
        if victim.owner == self.player:
            if amount >= 0:
                for blink in range(0, 4):
                    terminal.clear_area(23, 14, 1, 1)
                    terminal.refresh()
                    time.sleep(0.1)
                    terminal.put(23, 14, int(self.player.active.back_sprite, 16))
                    terminal.refresh()
                    time.sleep(0.15)
            x = 61
            x2 = 78
            y = 17
            y2 = 18
        else:
            for blink in range(0, 4):
                if amount >= 0:
                    terminal.clear_area(68, 5, 1, 1)
                    terminal.refresh()
                    time.sleep(0.1)
                    terminal.put(68, 5, int(self.ai.active.front_sprite, 16))
                    terminal.refresh()
                    time.sleep(0.15)
            x = 3
            x2 = 20
            y = 2
            y2 = 3
        remaining_health_bars_pre = round(victim.chp / victim.hp * bars)
        temp_hp = victim.chp
        if remaining_health_bars_pre <= 0:
            lost_bars = bars
        else:
            lost_bars = bars - remaining_health_bars_pre
        victim.chp -= amount
        if victim.chp < 0:
            victim.chp = 0
        elif victim.chp > victim.hp:
            victim.chp = victim.hp
        remaining_health_bars_post = round(victim.chp / victim.hp * bars)
        if amount > 0:
            if amount > temp_hp:
                dmg = math.floor(temp_hp / abs(remaining_health_bars_post - remaining_health_bars_pre))
                if dmg == 0:
                    dmg = 1
            else:
                dmg = math.floor(amount / abs(remaining_health_bars_post - remaining_health_bars_pre))
                if dmg == 0:
                    dmg = 1
        else:
            if (amount + victim.hp) > victim.chp:
                dmg = math.floor(temp_hp - victim.hp / abs(remaining_health_bars_post - remaining_health_bars_pre))
                if dmg == 0:
                    dmg = -1
            else:
                dmg = math.floor(amount / abs(remaining_health_bars_post - remaining_health_bars_pre))
                if dmg == 0:
                    dmg = -1
        if amount >= 0:
            for bar in range(0, abs(remaining_health_bars_pre - remaining_health_bars_post)):
                remaining_health_bars_pre -= 1
                if lost_bars + 1 > 20:
                    pass
                else:
                    lost_bars += 1
                terminal.printf(x, y, f"HP: {remaining_health_bars_pre * hp_symbol}{lost_bars * lost_hp}")
                if temp_hp - dmg >= victim.chp:
                    temp_hp -= dmg
                else:
                    temp_hp = victim.chp
                terminal.clear_area(x2, y2, 7, 1)
                terminal.printf(x2, y2, f"{temp_hp}/{victim.hp}")
                terminal.refresh()
                time.sleep(0.1)
        else:
            for bar in range(0, abs(remaining_health_bars_pre - remaining_health_bars_post)):
                if remaining_health_bars_pre + 1 > 20:
                    pass
                else:
                    remaining_health_bars_pre += 1
                lost_bars -= 1
                terminal.printf(x, y, f"HP: {remaining_health_bars_pre * hp_symbol}{lost_bars * lost_hp}")
                if temp_hp - dmg >= victim.chp:
                    temp_hp -= dmg
                else:
                    temp_hp = victim.chp
                terminal.clear_area(x2, y2, 7, 1)
                terminal.printf(x2, y2, f"{temp_hp}/{victim.hp}")
                terminal.refresh()
                time.sleep(0.1)
        terminal.clear_area(x2, y2, 7, 1)
        terminal.printf(x2, y2, f"{victim.chp}/{victim.hp}")
        terminal.refresh()
        if self.ai.active is not None and self.ai.active.chp <= 0:
            self.ai.team.remove(self.ai.active)
            print_txt(f"{self.ai.name}'s {self.ai.active.species} fainted!")
            terminal.clear_area(68, 5, 1, 1)
            self.ai.active = None
        if self.player.active is not None and self.player.active.chp <= 0:
            self.player.team.remove(self.player.active)
            print_txt(f"{self.player.name}'s {self.player.active.species} fainted!")
            terminal.clear_area(23, 14, 1, 1)
            self.player.active = None

    def hp_bars(self):
        hp_symbol = "█"
        lost_hp = "░"
        bars = 20
        ai_remaining_health_bars = round(self.ai.active.chp / self.ai.active.hp * bars)
        if ai_remaining_health_bars <= 0:
            ai_lost_bars = bars
        else:
            ai_lost_bars = bars - ai_remaining_health_bars
        terminal.clear_area(1, 1, 26, 3)
        terminal.printf(3, 1, f"{self.ai.active.species} {self.ai.active.gender}")
        terminal.printf(22, 1, f"Lv{self.ai.active.level}")
        terminal.printf(3, 2, f"HP: {ai_remaining_health_bars * hp_symbol}{ai_lost_bars * lost_hp}")
        if self.ai.active.chp <= 0:
            terminal.printf(20, 3, f"0/{self.ai.active.hp}")
        else:
            terminal.printf(20, 3, f"{self.ai.active.chp}/{self.ai.active.hp}")
        player_remaining_health_bars = round(self.player.active.chp / self.player.active.hp * bars)
        if player_remaining_health_bars <= 0:
            player_lost_bars = bars
        else:
            player_lost_bars = bars - player_remaining_health_bars
        terminal.clear_area(61, 16, 26, 3)
        terminal.printf(61, 16, f"{self.player.active.species} {self.player.active.gender}")
        terminal.printf(80, 16, f"Lv{self.player.active.level}")
        terminal.printf(61, 17, f"HP: {player_remaining_health_bars * hp_symbol}{player_lost_bars * lost_hp}")
        if self.player.active.chp <= 0:
            terminal.printf(78, 18, f"0/{self.player.active.hp}")
        else:
            terminal.printf(78, 18, f"{self.player.active.chp}/{self.player.active.hp}")
        terminal.refresh()

    def turn_end(self):
        trainers = [self.player, self.ai]
        for trainer in trainers:
            if trainer.active is not None:
                if trainer.active.acted:
                    trainer.active.first_turn = False
                if trainer.active.uproar != 0:
                    if self.player.active is not None and self.player.active.status == "SLP":
                        self.player.active.status = ""
                        print_txt(f"{self.player.name}'s {self.player.active.species} woke up!")
                    if self.ai.active is not None and self.ai.active.status == "SLP":
                        self.ai.active.status = ""
                        print_txt(f"{self.ai.name}'s {self.ai.active.species} woke up!")
                if trainer.active.uproar == 1:
                    trainer.active.uproar = 0
                if trainer.active.trapping[0] != 0:
                    print_txt(
                        f"{trainer.opponent.name}'s {trainer.opponent.active.species} "
                        f"was hurt by {trainer.active.trapping[1]}!")
                    self.deal_dmg(trainer.opponent.active, math.floor(trainer.opponent.active.hp / 16))
                    trainer.opponent.active.damaged_this_turn = True
                    if trainer.opponent.active.bide != 0:
                        trainer.opponent.active.bide_dmg += math.floor(trainer.opponent.active.hp / 16)
                    trainer.active.trapping[0] -= 1
                if trainer.active.fury_cutter != 0 and not trainer.active.fury_cutter_hit:
                    trainer.active.fury_cutter = 0
                elif trainer.active.fury_cutter_hit:
                    trainer.active.fury_cutter_hit = False
                if trainer.active.rolling != 0 and not trainer.active.rolling_hit:
                    trainer.active.rolling = 0
                elif trainer.active.rolling_hit:
                    trainer.active.rolling_hit = False
                if trainer.active.cursed:
                    print_txt(f"{trainer.name}'s {trainer.active.species} was hurt by the curse")
                    self.deal_dmg(trainer.active, math.floor(trainer.active.hp / 4))
                    if trainer.active.rage:
                        change_stats(trainer.active, trainer.active, "Rage")
                        trainer.active.damaged_this_turn = True
                        trainer.active.dmg_last_taken = math.floor(trainer.active.hp / 4)
                    if trainer.active.bide != 0:
                        trainer.active.bide_dmg += math.floor(trainer.active.hp / 4)
                if trainer.active.status == "BRN":
                    print_txt(f"{trainer.name}'s {trainer.active.species} was hurt by it's burn!")
                    self.deal_dmg(trainer.active, math.floor(trainer.active.hp / 8))
                if trainer.active.status == "PSN":
                    print_txt(f"{trainer.name}'s {trainer.active.species} was hurt by poison!", 0.5)
                    self.deal_dmg(trainer.active, math.floor(trainer.active.hp / 8))
                if trainer.active.status == "TOX":
                    print_txt(f"{trainer.name}'s {trainer.active.species} was hurt by poison!", 0.5)
                    trainer.active.tox_turns += 1
                    dmg = math.floor(trainer.active.hp * (trainer.active.tox_turns / 16))
                    self.deal_dmg(trainer.active, dmg)
                if trainer.reflect > 0:
                    trainer.reflect -= 1
                if trainer.light_screen > 0:
                    trainer.light_screen -= 1
                if trainer.mist > 0:
                    trainer.mist -= 1
                if trainer.active.protecting:
                    trainer.active.protecting_chance = trainer.active.protecting_chance / 2
                    trainer.active.protecting = False
                elif not trainer.active.protecting:
                    trainer.active.protecting_chance = 1
                if trainer.active.enduring:
                    trainer.active.protecting_chance = trainer.active.protecting_chance / 2
                    trainer.active.enduring = False
                elif not trainer.active.enduring:
                    trainer.active.protecting_chance = 1
        self.alive_check()

    def clean_up(self):
        trainers = [self.player, self.ai]
        for trainer in trainers:
            if trainer.active is not None:
                trainer.active.flinched = False
                trainer.active.damaged_this_turn = False
                trainer.active.acted = False
                trainer.active.dmg_last_type_taken = None
                trainer.active.dmg_last_taken = 0
        