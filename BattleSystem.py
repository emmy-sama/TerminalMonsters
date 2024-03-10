from Classes import *
from bearlibterminal import terminal
import time


class Battle:
    def __init__(self, player, opponent):
        self.temp_stat_table_norm = {-6: 2 / 8, -5: 2 / 7, -4: 2 / 6, -3: 2 / 5, -2: 2 / 4, -1: 2 / 3, 0: 2 / 2,
                                     1: 3 / 2, 2: 4 / 2,
                                     3: 5 / 2, 4: 6 / 2, 5: 7 / 2, 6: 8 / 2}
        self.temp_stat_table_acc_eva = {-6: 33 / 100, -5: 36 / 100, -4: 43 / 100, -3: 50 / 100, -2: 60 / 100,
                                        -1: 75 / 100, 0: 100 / 100, 1: 133 / 100, 2: 166 / 100, 3: 200 / 100,
                                        4: 250 / 100, 5: 266 / 100, 6: 300 / 100}
        self.moves = moves
        self.types = types
        self.player = player
        self.player_active = player.team[0]
        self.opponent = opponent
        self.opponent_active = opponent.team[0]
        self.weather = "clear"
        self.p_move = None
        self.p_move_last = None
        self.ai_move = None
        self.ai_move_last = None

    def print_ui(self):
        terminal.layer(0)
        terminal.put(0, 0, 0xF8FF)
        terminal.layer(1)
        terminal.put(68, 5, int(self.opponent_active.front_sprite, 16))
        terminal.put(23, 14, int(self.player_active.back_sprite, 16))
        if self.player_active is not None and self.opponent_active is not None:
            self.hp_bars()
        terminal.refresh()

    def battle(self):
        while True:
            self.player_active.flinched = False
            self.opponent_active.flinched = False
            self.player_active.damaged_this_turn = False
            self.opponent_active.damaged_this_turn = False
            self.player_active.acted = False
            self.opponent_active.acted = False
            self.player_active.dmg_last_type_taken = None
            self.player_active.dmg_last_taken = 0
            self.opponent_active.dmg_last_type_taken = None
            self.opponent_active.dmg_last_taken = 0
            self.print_ui()
            if (self.opponent_active.semi_invulnerable is None and self.opponent_active.charged is False and
                    self.opponent_active.bide == 0 and self.opponent_active.outraging == 0 and self.opponent_active.uproar == 0
                    and self.opponent_active.rolling == 0):
                if self.opponent_active.recharge:
                    self.ai_move = None
                    self.opponent_active.recharge = False
                    self.print_txt(f"{self.opponent.name}'s {self.opponent_active.species} must recharge!")
                else:
                    self.ai_move = self.ai_turn()
            if (self.player_active.semi_invulnerable is None and self.player_active.charged is False and
                    self.player_active.bide == 0 and self.player_active.outraging == 0 and self.player_active.uproar == 0
                    and self.player_active.rolling == 0):
                if self.player_active.recharge:
                    self.p_move = None
                    self.player_active.recharge = False
                    self.print_txt(f"{self.player.name}'s {self.player_active.species} must recharge!")
                else:
                    self.p_move = None
                    self.player_turn()
                    terminal.clear_area(45, 20, 42, 4)
            if self.p_move is not None and self.p_move.get("name") == "Focus Punch":
                self.print_txt(f"{self.player.name}'s {self.player_active.species} is tightening its focus!")
            if self.ai_move is not None and self.ai_move.get("name") == "Focus Punch":
                self.print_txt(f"{self.opponent.name}'s {self.opponent_active.species} is tightening its focus!")
            if self.p_move is not None and self.ai_move is not None:
                order = self.speed_check()
                self.action(order[0], order[2], order[1])
                if order[0].chp <= 0:
                    if order[0] == self.player_active:
                        self.player.team.remove(self.player_active)
                        self.player_active = None
                    elif order[0] == self.opponent_active:
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
            if self.player_active.acted:
                self.player_active.first_turn = False
            if self.opponent_active.acted:
                self.opponent_active.first_turn = False
            if self.player_active.uproar != 0 or self.opponent_active.uproar != 0:
                if self.player_active.status == "SLP":
                    self.player_active.status = ""
                    self.print_txt(f"{self.player.name}'s {self.player_active.species} woke up!")
                if self.opponent_active.status == "SLP":
                    self.opponent_active.status = ""
                    self.print_txt(f"{self.opponent.name}'s {self.opponent_active.species} woke up!")
            if self.player_active.uproar == 1:
                self.player_active.uproar = 0
            if self.opponent_active.uproar == 1:
                self.opponent_active.uproar = 0
            if self.player_active.trapping[0] != 0:
                self.deal_dmg(self.opponent_active, math.floor(self.opponent_active.hp / 16))
                self.opponent_active.damaged_this_turn = True
                if self.opponent_active.bide != 0:
                    self.opponent_active.bide_dmg += math.floor(self.opponent_active.hp / 16)
                self.hp_bars()
                self.print_txt(f"{self.opponent.name}'s {self.opponent_active.species} was hurt by {self.player_active.trapping[1]}!")
                self.player_active.trapping[0] -= 1
            if self.opponent_active.trapping[0] != 0:
                self.deal_dmg(self.player_active, math.floor(self.player_active.hp / 16))
                self.player_active.damaged_this_turn = True
                if self.player_active.bide != 0:
                    self.player_active.bide_dmg += math.floor(self.player_active.hp / 16)
                self.hp_bars()
                self.print_txt(f"{self.player.name}'s {self.player_active.species} was hurt by {self.opponent_active.trapping[1]}!")
                self.opponent_active.trapping[0] -= 1
            if self.player_active.fury_cutter != 0 and not self.player_active.fury_cutter_hit:
                self.player_active.fury_cutter = 0
            elif self.player_active.fury_cutter_hit:
                self.player_active.fury_cutter_hit = False
            if self.opponent_active.fury_cutter != 0 and not self.opponent_active.fury_cutter_hit:
                self.opponent_active.fury_cutter = 0
            elif self.opponent_active.fury_cutter_hit:
                self.opponent_active.fury_cutter_hit = False
            if self.player_active.rolling != 0 and not self.player_active.rolling_hit:
                self.player_active.rolling = 0
            elif self.player_active.rolling_hit:
                self.player_active.rolling_hit = False
            if self.opponent_active.rolling != 0 and not self.opponent_active.rolling_hit:
                self.opponent_active.rolling = 0
            elif self.opponent_active.rolling_hit:
                self.opponent_active.rolling_hit = False
            if self.player_active.cursed:
                self.deal_dmg(self.player_active, math.floor(self.player_active.hp / 4))
                self.hp_bars()
                self.print_txt(f"{self.player.name}'s {self.player_active.species} was hurt by the curse")
                if self.player_active.rage:
                    self.change_stats(self.player_active, self.player_active, "Rage")
                    self.player_active.damaged_this_turn = True
                    self.player_active.dmg_last_taken = math.floor(self.player_active.hp / 4)
                if self.player_active.bide != 0:
                    self.player_active.bide_dmg += math.floor(self.player_active.hp / 4)
            if self.opponent_active.cursed:
                self.deal_dmg(self.opponent_active, math.floor(self.opponent_active.hp / 4))
                self.hp_bars()
                self.print_txt(f"{self.opponent.name}'s {self.opponent_active.species} was hurt by the curse")
                if self.opponent_active.rage:
                    self.change_stats(self.player_active, self.opponent_active, "Rage")
                    self.opponent_active.damaged_this_turn = True
                    self.opponent_active.dmg_last_taken = math.floor(self.opponent_active.hp / 4)
                if self.opponent_active.bide != 0:
                    self.opponent_active.bide_dmg += math.floor(self.opponent_active.hp / 4)
            if self.player.reflect > 0:
                self.player.reflect -= 1
            if self.opponent.reflect > 0:
                self.opponent.reflect -= 1
            if self.player.light_screen > 0:
                self.player.light_screen -= 1
            if self.opponent.light_screen > 0:
                self.opponent.light_screen -= 1
            if self.player.mist > 0:
                self.player.mist -= 1
            if self.opponent.mist > 0:
                self.opponent.mist -= 1
            if self.player_active.protecting:
                self.player_active.protecting_chance = self.player_active.protecting_chance / 2
                self.player_active.protecting = False
            elif not self.player_active.protecting:
                self.player_active.protecting_chance = 1
            if self.opponent_active.protecting:
                self.opponent_active.protecting_chance = self.opponent_active.protecting_chance / 2
                self.opponent_active.protecting = False
            elif not self.opponent_active.protecting:
                self.opponent_active.protecting_chance = 1
            self.alive_check()

    def ai_turn(self):
        ai_random = random.choice(self.opponent_active.moves)
        for move in self.moves:
            if move.get("name") == ai_random:
                return move

    def player_turn(self):
        while True:
            terminal.clear_area(45, 20, 60, 4)
            terminal.printf(45, 20, "1 Fight\n2 Pokemon")
            self.print_txt("What will you do?", 0)
            button = terminal.read()
            if button == terminal.TK_1:
                while True:
                    terminal.clear_area(45, 20, 42, 4)
                    for move in moves:
                        if self.player_active.moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 20, f"1 {self.player_active.moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player_active.moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player_active.moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"2 {self.player_active.moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player_active.moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player_active.moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"3 {self.player_active.moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player_active.moves):
                        terminal.printf(45, 23, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player_active.moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 23, f"4 {self.player_active.moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt("What move would you like to use?(1-4)", 0)
                    button = terminal.read()
                    if button == terminal.TK_1:
                        while True:
                            for move in moves:
                                if self.player_active.moves[0] == move.get("name"):
                                    desc = move.get("description")
                                    break
                            self.print_txt(f"Use {self.player_active.moves[0]}?(Enter/Backspace) {desc}", 0)
                            button = terminal.read()
                            if button == terminal.TK_ENTER:
                                for move in self.moves:
                                    if move.get("name") == self.player_active.moves[0]:
                                        self.p_move = move
                                        return
                            elif button == terminal.TK_BACKSPACE:
                                break
                    elif button == terminal.TK_2 and 2 <= len(self.player_active.moves):
                        while True:
                            for move in moves:
                                if self.player_active.moves[1] == move.get("name"):
                                    desc = move.get("description")
                                    break
                            self.print_txt(f"Use {self.player_active.moves[1]}?(Enter/Backspace) {desc}", 0)
                            button = terminal.read()
                            if button == terminal.TK_ENTER:
                                for move in self.moves:
                                    if move.get("name") == self.player_active.moves[1]:
                                        self.p_move = move
                                        return
                            elif button == terminal.TK_BACKSPACE:
                                break
                    elif button == terminal.TK_3 and 3 <= len(self.player_active.moves):
                        while True:
                            for move in moves:
                                if self.player_active.moves[2] == move.get("name"):
                                    desc = move.get("description")
                                    break
                            self.print_txt(f"Use {self.player_active.moves[2]}?(Enter/Backspace) {desc}", 0)
                            button = terminal.read()
                            if button == terminal.TK_ENTER:
                                for move in self.moves:
                                    if move.get("name") == self.player_active.moves[2]:
                                        self.p_move = move
                                        return
                            elif button == terminal.TK_BACKSPACE:
                                break
                    elif button == terminal.TK_4 and 4 <= len(self.player_active.moves):
                        while True:
                            for move in moves:
                                if self.player_active.moves[3] == move.get("name"):
                                    desc = move.get("description")
                                    break
                            self.print_txt(f"Use {self.player_active.moves[3]}?(Enter/Backspace) {desc}", 0)
                            button = terminal.read()
                            if button == terminal.TK_ENTER:
                                for move in self.moves:
                                    if move.get("name") == self.player_active.moves[3]:
                                        self.p_move = move
                                        return
                            elif button == terminal.TK_BACKSPACE:
                                break
                    elif button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_2:
                if self.player_swap(False):
                    break

    def player_swap(self, must_swap):
        while True:
            terminal.layer(0)
            terminal.put(0, 0, 0xF8FD)
            terminal.layer(1)
            terminal.clear_area(45, 17, 42, 7)
            terminal.printf(45, 18, f"1 {self.player.team[0]}")
            if 1 >= len(self.player.team):
                terminal.printf(45, 19, "Empty Slot")
            else:
                terminal.printf(45, 19, f"2 {self.player.team[1]}")
            if 2 >= len(self.player.team):
                terminal.printf(45, 20, "Empty Slot")
            else:
                terminal.printf(45, 20, f"3 {self.player.team[2]}")
            if 3 >= len(self.player.team):
                terminal.printf(45, 21, "Empty Slot")
            else:
                terminal.printf(45, 21, f"4 {self.player.team[3]}")
            if 4 >= len(self.player.team):
                terminal.printf(45, 22, "Empty Slot")
            else:
                terminal.printf(45, 22, f"5 {self.player.team[4]}")
            if 5 >= len(self.player.team):
                terminal.printf(45, 23, "Empty Slot")
            else:
                terminal.printf(45, 23, f"6 {self.player.team[5]}")
            self.print_txt("What Pokemon would you like to view/swap? (1-6)", 0)
            button = terminal.read()
            if button == terminal.TK_1:
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[0].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[0].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[0].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[0].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[0].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[0].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[0].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[0].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[0].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[0].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[0].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[0].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[0].species}?(Enter/Backspace)"
                                   f"{self.player.team[0].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[0]:
                            self.print_txt(f"{self.player.team[0].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[0]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_2 and 2 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[1].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[1].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[1].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[1].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[1].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[1].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[1].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[1].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[1].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[1].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[1].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[1].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[1].species}?(Enter/Backspace)"
                                   f"{self.player.team[1].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[1]:
                            self.print_txt(f"{self.player.team[1].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[1]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_3 and 3 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[2].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[2].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[2].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[2].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[2].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[2].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[2].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[2].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[2].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[2].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[2].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[2].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[2].species}?(Enter/Backspace)"
                                   f"{self.player.team[2].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[2]:
                            self.print_txt(f"{self.player.team[2].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[2]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_4 and 4 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[3].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[3].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[3].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[3].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[3].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[3].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[3].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[3].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[3].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[3].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[3].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[3].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[3].species}?(Enter/Backspace)"
                                   f"{self.player.team[3].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[3]:
                            self.print_txt(f"{self.player.team[3].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[3]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_5 and 5 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[4].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[4].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[4].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[4].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[4].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[4].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[4].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[4].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[4].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[4].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[4].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[4].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[4].species}?(Enter/Backspace)"
                                   f"{self.player.team[4].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[4]:
                            self.print_txt(f"{self.player.team[4].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[4]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_6 and 6 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    for move in moves:
                        if self.player.team[5].moves[0] == move.get("name"):
                            power = move.get("power")
                            acc = move.get("accuracy")
                            type = move.get("type")
                            break
                    terminal.printf(45, 18, f"Ability: {self.player.team[5].ability}")
                    terminal.printf(45, 19, f"1 {self.player.team[5].moves[0]} {type} Pwr:{power} Acc:{acc}")
                    if 2 > len(self.player.team[5].moves):
                        terminal.printf(45, 20, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[5].moves[1] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 20, f"2 {self.player.team[5].moves[1]} {type} Pwr:{power} Acc:{acc}")
                    if 3 > len(self.player.team[5].moves):
                        terminal.printf(45, 21, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[5].moves[2] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 21, f"3 {self.player.team[5].moves[2]} {type} Pwr:{power} Acc:{acc}")
                    if 4 > len(self.player.team[5].moves):
                        terminal.printf(45, 22, "Empty Slot")
                    else:
                        for move in moves:
                            if self.player.team[5].moves[3] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 22, f"4 {self.player.team[5].moves[3]} {type} Pwr:{power} Acc:{acc}")
                    self.print_txt(f"Swap to {self.player.team[5].species}?(Enter/Backspace)"
                                   f"{self.player.team[5].info}", 0)
                    button = terminal.read()
                    if button == terminal.TK_ENTER:
                        if self.opponent_active.trapping[0] != 0:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.opponent_active.blocking:
                            self.print_txt(f"{self.player_active.species} is trapped and cant switch out!")
                            break
                        if self.player_active == self.player.team[5]:
                            self.print_txt(f"{self.player.team[5].species} is already out")
                            break
                        self.player_active.reset_temp()
                        self.player_active = self.player.team[5]
                        self.player_active.first_turn = True
                        terminal.clear_area(45, 17, 42, 7)
                        self.print_ui()
                        self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                        return True
                    if button == terminal.TK_BACKSPACE:
                        break
            elif button == terminal.TK_BACKSPACE and not must_swap:
                terminal.clear_area(45, 17, 42, 7)
                self.print_ui()
                break

    def speed_check(self):
        player_speed = math.floor(self.player_active.speed *
                                  self.temp_stat_table_norm.get(self.player_active.temp_stats.get("speed")))
        opponent_speed = math.floor(self.opponent_active.speed *
                                    self.temp_stat_table_norm.get(self.opponent_active.temp_stats.get("speed")))
        if self.p_move.get("priority") > self.ai_move.get("priority"):
            return [self.player_active, self.p_move, self.opponent_active, self.ai_move]
        elif self.ai_move.get("priority") > self.p_move.get("priority"):
            return [self.opponent_active, self.ai_move, self.player_active, self.p_move]
        elif player_speed > opponent_speed:
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
        if attacker.uproar != 0:
            attacker.uproar -= 1
        if attacker.flinching:
            attacker.flinching = False
            attacker.charged = False
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} flinched!")
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
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    self.print_txt("But it failed")
                    return
            elif move.get("name") == "Sleep Talk":
                if attacker.status == "SLP":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    valid_moves = []
                    for attacks in attacker.moves:
                        for attack in moves:
                            if attack.get("name") == attacks:
                                if "No Sleep Talk" in attack.get("flags"):
                                    break
                                else:
                                    valid_moves.append(attack)
                                    break
                    if valid_moves == []:
                        self.print_txt("But it failed")
                        return
                    move = random.choice(valid_moves)
                else:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                    self.print_txt("But it failed")
                    return
            else:
                # wake up during uproar
                pass
        if attacker.status == "FRZ":
            pass
        if attacker.status == "SLP":
            pass
        if attacker.status == "PAR":
            pass
            # attacker.outraging = 0
        if move.get("name") == "Assist":
            choices = []
            for poke in attacker.owner.team:
                if poke == attacker:
                    continue
                for entry in poke.moves:
                    for attack in self.moves:
                        if attack.get("name") == entry:
                            if "No Assist" not in attack.get("flags"):
                                choices.append(attack)
                                break
                            break
            if not choices:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                self.print_txt("But it failed")
                attacker.acted = True
                return
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                move = random.choice(choices)
        if move.get("name") == "Metronome":
            while True:
                move = random.choice(self.moves)
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
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} sprang up!")
                attacker.acted = True
                return
            if move.get("name") == "Dig":
                attacker.semi_invulnerable = "dig"
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} dug a hole!")
                attacker.acted = True
                return
            if move.get("name") == "Dive":
                attacker.semi_invulnerable = "dive"
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} hide underwater!")
                attacker.acted = True
                return
            if move.get("name") == "Fly":
                attacker.semi_invulnerable = "fly"
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} flew up high!")
                attacker.acted = True
                return
        elif "Semi-invulnerable" in move.get("flags"):
            attacker.semi_invulnerable = None
        if "Charge" in move.get("flags") and attacker.charged is False:
            if move.get("name") == "Skull Bash":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} lowered it's head!")
                attacker.charged = True
                attacker.temp_stats["defense"] += 1
                self.print_txt(f"{attacker.species}'s defense rose!")
                attacker.acted = True
                return
            elif move.get("name") == "Solar Beam":
                if self.weather == "sun":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                else:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
                    attacker.charged = True
                    attacker.acted = True
                    return
            elif move.get("name") == "Razor Wind":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} whipped up a whirlwind!")
                attacker.charged = True
                attacker.acted = True
                return
            elif move.get("name") == "Sky Attack":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is glowing!")
                attacker.charged = True
                attacker.acted = True
                return
        elif "Charge" in move.get("flags"):
            attacker.charged = False
        if move.get("name") == "Bide" and attacker.bide != 0:
            if attacker.bide == 1:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
                attacker.bide = 2
                attacker.acted = True
                return
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} unleashed energy")
                attacker.bide = 0
                attacker.acted = True
                if attacker.bide_dmg == 0:
                    self.print_txt("But it failed")
                elif defender.protecting:
                    self.print_txt(f"{defender.species} protected it's self")
                else:
                    self.deal_dmg(defender, (attacker.bide_dmg * 2))
                    if defender.bide != 0:
                        defender.bide_dmg += (attacker.bide_dmg * 2)
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = (attacker.bide_dmg * 2)
                attacker.bide_dmg = 0
                return
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
        if defender is None:
            if "Requires Target" in move.get("flags") or move.get("category") == "Special" or move.get("category") == "Physical":
                self.print_txt("But it failed")
                attacker.acted = True
                return
        if defender.protecting and "Protect" in move.get("flags"):
            self.print_txt(f"{defender.species} protected it's self")
            attacker.acted = True
            if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                dmg = self.dmg_calc(attacker, defender, move)
                self.deal_dmg(attacker, (dmg / 2))
                attacker.dmg_last_type_taken = None
                attacker.dmg_last_taken = dmg / 2
                self.hp_bars()
            elif move.get("name") == "Explosion" or move.get("name") == "Self-Destruct":
                self.deal_dmg(attacker, 999)
                self.hp_bars()
            elif attacker.rage and move.get("name") != "Rage":
                attacker.rage = False
            elif move.get("name") == "Rage":
                attacker.rage = True
            return
        if move.get("type") == "Ghost":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Normal" or defender.type_two == "Normal":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Ground":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Flying" or defender.type_two == "Flying":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Electric":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ground" or defender.type_two == "Ground":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Normal":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Fighting":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Poison":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Steel" or defender.type_two == "Steel":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        elif move.get("type") == "Psychic":
            if move.get("category") == "Special" or move.get("category") == "Physical":
                if defender.type_one == "Dark" or defender.type_two == "Dark":
                    self.print_txt("It had no effect")
                    attacker.acted = True
                    return
        if move.get("name") == "Counter":
            if attacker.dmg_last_taken > 0 and attacker.dmg_last_type_taken == "Physical":
                self.deal_dmg(defender, (attacker.dmg_last_taken * 2))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.dmg_last_taken * 2
                if defender.bide != 0:
                    defender.bide_dmg += attacker.dmg_last_taken * 2
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                return
            else:
                self.print_txt("But it failed")
                return
        if move.get("name") == "Mirror Coat":
            if attacker.dmg_last_taken > 0 and attacker.dmg_last_type_taken == "Special":
                self.deal_dmg(defender, (attacker.dmg_last_taken * 2))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.dmg_last_taken * 2
                if defender.bide != 0:
                    defender.bide_dmg += attacker.dmg_last_taken * 2
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                return
            else:
                self.print_txt("But it failed")
                return
        if move.get("name") == "Focus Punch" and attacker.damaged_this_turn:
            self.print_txt("But it failed")
            attacker.acted = True
            return
        if defender.semi_invulnerable is not None:
            if (defender.semi_invulnerable == "bounce" or defender.semi_invulnerable == "fly" and
                    "Bypass Fly" not in move.get("flags")):
                self.print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                    self.hp_bars()
                attacker.outraging = 0
                attacker.acted = True
                return
            elif defender.semi_invulnerable == "dig" and "Bypass Dig" not in move.get("flags"):
                self.print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                    self.hp_bars()
                attacker.outraging = 0
                attacker.acted = True
                return
            elif defender.semi_invulnerable == "dive" and "Bypass Dive" not in move.get("flags"):
                self.print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                    attacker.dmg_last_type_taken = None
                    attacker.dmg_last_taken = dmg / 2
                    self.hp_bars()
                attacker.outraging = 0
                attacker.acted = True
                return
        if "OHKO" in move.get("flags"):
            if attacker.level < defender.level:
                self.print_txt(f"{attacker.species} Missed!")
                attacker.acted = True
                return
            else:
                hit_check = random.randint(1, 100)
                accuracy = math.floor(30 + (attacker.level - defender.level))
                if hit_check <= accuracy:
                    self.deal_dmg(defender, 999)
                    self.print_txt("It's a one-hit KO!")
                    attacker.acted = True
                    return
                else:
                    self.print_txt(f"{attacker.species} Missed!")
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
                self.print_txt(f"{attacker.species} Missed!")
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
                self.print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Uproar" and attacker.uproar == 1:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
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
                self.print_txt("The wall shattered!")
        if move.get("name") == "Uproar" and attacker.uproar == 0:
            attacker.uproar = random.randint(2, 5)
        if move.get("name") == "Bide":
            attacker.bide = 1
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
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
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    if defender.chp <= 0 or attacker.chp <= 0:
                        self.print_txt(f"It hit {hit + 1} time(s)")
                        break
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    self.print_txt(f"It hit {hits} time(s)")
            elif "Double-Hit" in move.get("flags"):
                for hit in range(0, 2):
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    if defender.chp <= 0 or attacker.chp <= 0:
                        self.print_txt("It hit 1 time(s)")
                        break
                    if "Secondary" in move.get("flags"):
                        self.secondary(attacker, defender, move, dmg)
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    self.print_txt("It hit 2 time(s)")
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
                    self.deal_dmg(defender, dmg)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    hits += 1
                    if defender.chp <= 0 or attacker.chp <= 0:
                        self.print_txt(f"It hit {hit + 1} time(s)")
                        break
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
                if defender.chp > 0 and attacker.chp > 0:
                    self.print_txt(f"It hit {hits} time(s)")
                self.print_txt(f"It hit {hits} time(s)")
            elif move.get("name") == "Beat Up":
                for mon in attacker.owner.team:
                    if mon.status == "":
                        self.print_txt(f"{mon.species}'s attack!")
                        crit = self.crit_check(mon, move)
                        dmg = math.floor(math.floor((math.floor((2 * mon.level) / 5 + 2) * mon.attack * 10) / defender.defense) / 50)
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
                        self.deal_dmg(defender, dmg)
                        defender.dmg_last_type_taken = move.get("category")
                        defender.dmg_last_taken = dmg
                        if defender.bide != 0:
                            defender.bide_dmg += dmg
                        if defender.rage:
                            self.change_stats(attacker, defender, "Rage")
                        if defender.chp <= 0 or attacker.chp <= 0:
                            break
                defender.damaged_this_turn = True
            elif "Level Damage" in move.get("flags"):
                self.deal_dmg(defender, attacker.level)
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = attacker.level
                if defender.bide != 0:
                    defender.bide_dmg += attacker.level
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif "Fixed Damage" in move.get("flags"):
                self.deal_dmg(defender, move.get("amount"))
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = move.get("amount")
                if defender.bide != 0:
                    defender.bide_dmg += move.get("amount")
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Psywave":
                ran = random.randint(0, 10)
                dmg = math.floor((attacker.level * (10 * ran + 50)) / 100)
                if dmg == 0:
                    dmg = 1
                self.deal_dmg(defender, dmg)
                defender.dmg_last_type_taken = dmg
                defender.dmg_last_taken = dmg
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Super Fang":
                dmg = math.floor(defender.chp * 0.5)
                if dmg == 0:
                    dmg = 1
                self.deal_dmg(defender, dmg)
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = dmg
                if defender.bide != 0:
                    defender.bide_dmg += dmg
                if defender.rage:
                    self.change_stats(attacker, defender, "Rage")
                defender.damaged_this_turn = True
            elif move.get("name") == "Endeavor":
                if attacker.chp >= defender.chp:
                    self.print_txt("But it failed")
                else:
                    if defender.bide != 0:
                        defender.bide_dmg += (defender.chp - attacker.chp)
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = (defender.chp - attacker.chp)
                    self.deal_dmg(defender, (defender.chp - attacker.chp))
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
            elif (move.get("name") == "Fake Out" and attacker.first_turn is False or
                  move.get("name") == "Fake Out" and defender.acted):
                self.print_txt("But it failed")
            elif move.get("name") == "Dream Eater" and defender.status != "SLP":
                self.print_txt("But it failed")
            elif move.get("name") == "Present":
                power = random.choices([0, 40, 80, 120], [20, 40, 30, 10], k=1)[0]
                if power > 0:
                    move["power"] = power
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(defender, dmg)
                    if dmg > 0:
                        if defender.rage:
                            self.change_stats(attacker, defender, "Rage")
                        defender.damaged_this_turn = True
                        defender.dmg_last_type_taken = move.get("category")
                        defender.dmg_last_taken = dmg
                        if defender.bide != 0:
                            defender.bide_dmg += dmg
                else:
                    if defender.chp == defender.hp:
                        self.print_txt("It had no effect!")
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
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
            elif move.get("name") == "Rollout" or move.get("name") == "Ice Ball":
                move["power"] = 30 * 2 ** attacker.rolling
                dmg = self.dmg_calc(attacker, defender, move)
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
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
                self.deal_dmg(defender, dmg)
                if dmg > 0:
                    if defender.rage:
                        self.change_stats(attacker, defender, "Rage")
                    defender.damaged_this_turn = True
                    defender.dmg_last_type_taken = move.get("category")
                    defender.dmg_last_taken = dmg
                    if defender.bide != 0:
                        defender.bide_dmg += dmg
                if "Secondary" in move.get("flags"):
                    self.secondary(attacker, defender, move, dmg)
        self.hp_bars()
        if "Outrage" in move.get("flags") and attacker.outraging == 0:
            if attacker.confused:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is already confused!")
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} became confused due to fatigue!")
                attacker.confused = True
        if defender.rage and defender.damaged_this_turn:
            self.print_txt(f"{defender.owner.name}'s {defender.species}'s rage is building!")
        if move.get("name") == "Uproar" and attacker.uproar == 1:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} calmed down.")
        elif move.get("name") == "Uproar" and attacker.uproar > 1:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} caused a uproar!")
        attacker.acted = True

    def non_dmg_move(self, attacker, defender, move):
        # Do Camouflage, Conversion, Conversion 2, Curse, Destiny Bond, Detect,
        # Endure, Grudge, Haze, Imprison, Ingrain, Light Screen, Magic Coat, Memento,
        # Metronome, Mimic, Mirror Move, Mist, Mud Sport, Nightmare, Pain Split, Perish Song,
        # Protect, Psych Up, Recycle, Reflect, Refresh, Rest, Role Play, Safeguard, Sketch,
        # Skill Swap, Snatch, Spikes, Substitute,
        # Teleport, Transform, Wish, Yawn, Attract, Encore, Foresight, Lock-On, Mind Reader, Odor Sleuth,
        # Spite, Taunt, Torment, Trick, Whirlwind, Disable, Leech Seed, Nature Power
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            self.change_stats(attacker, defender, move)
        if "Confuses" in move.get("flags"):
            defender.confused = True
            self.print_txt(f"{defender.owner.name}'s {defender.species} became confused!")
        if "Status" in move.get("flags") and defender.status is None:
            if (move.get("status") == "BRN"
                    and defender.type_one != "Fire" and defender.type_two != "Fire"):
                defender.status = "BRN"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
            elif (move.get("status") == "FRZ"
                  and defender.type_one != "Ice" and defender.type_two != "Ice"):
                defender.status = "FRZ"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
            elif move.get("status") == "PAR":
                defender.status = "PAR"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
            elif (move.get("status") == "PSN" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                defender.status = "PSN"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was poisoned!")
            elif (move.get("status") == "TOX" and defender.type_one != "Poison"
                  and defender.type_two != "Poison" and defender.type_one != "Steel"
                  and defender.type_two != "Steel"):
                defender.status = "TOX"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
            elif move.get("status") == "SLP":
                if attacker.uproar != 0 or defender.uproar != 0:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} cannot fall asleep due to the uproar!")
                else:
                    defender.status = "SLP"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is fast asleep")
        if "Lowers Attacker chp by hp" in move.get("flags"):
            if attacker.chp - math.floor(attacker.hp * move.get("hp changes")) <= 0:
                self.print_txt("But it failed")
                return
            else:
                self.deal_dmg(attacker, (math.floor(attacker.hp * move.get("hp changes"))))
        if "Raises Attacker chp by hp" in move.get("flags"):
            if move.get("name") == "Swallow":
                if attacker.stockpile <= 0:
                    self.print_txt("But it failed")
                    return
                else:
                    hp_change = [0.25, 0.50, 1]
                    self.deal_dmg(attacker, -math.floor(attacker.hp * hp_change[attacker.stockpile - 1]))
                    attacker.stockpile = 0
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp * move.get("hp changes")))
        if "Block" in move.get("flags"):
            if attacker.blocking:
                self.print_txt("But it failed")
            else:
                attacker.blocking = True
        elif "Weather" in move.get("flags"):
            if move.get("name") == "Hail":
                if self.weather == "hail":
                    self.print_txt("But it failed")
                else:
                    self.weather = "hail"
                    self.print_txt("It started to hail!")
            elif move.get("name") == "Rain Dance":
                if self.weather == "rain":
                    self.print_txt("But it failed")
                else:
                    self.weather = "rain"
                    self.print_txt("It started to rain!")
            elif move.get("name") == "Sandstorm":
                if self.weather == "sand":
                    self.print_txt("But it failed")
                else:
                    self.weather = "sand"
                    self.print_txt("A sand storm brewed!")
            elif move.get("name") == "Sunny Day":
                if self.weather == "sun":
                    self.print_txt("But it failed")
                else:
                    self.weather = "sun"
                    self.print_txt("The sun light got bright!")
        elif "Synthesis" in move.get("flags"):
            if self.weather == "clear":
                self.deal_dmg(attacker, -math.floor(attacker.hp / 2))
            elif self.weather == "sun":
                self.deal_dmg(attacker, -math.floor(attacker.hp * 0.66))
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp / 4))
        elif move.get("name") == "Protect" or move.get("name") == "Detect":
            if defender.acted:
                self.print_txt("But it failed")
            else:
                if attacker.protecting_chance >= random.uniform(0, 1):
                    attacker.protecting = True
                    self.print_txt(f"{attacker.species} is protecting it's self")
                else:
                    self.print_txt("But it failed")
        elif move.get("name") == "Reflect":
            if attacker.owner.reflect > 0:
                self.print_txt("But it failed")
            else:
                attacker.owner.reflect = 5
        elif move.get("name") == "Light Screen":
            if attacker.owner.light_screen > 0:
                self.print_txt("But it failed")
            else:
                attacker.owner.light_screen = 5
        elif move.get("name") == "Mist":
            if attacker.owner.mist > 0:
                self.print_txt("But it failed")
            else:
                attacker.owner.mist = 5
        elif move.get("name") == "Curse":
            if attacker.type_one == "Ghost" or attacker.type_two == "Ghost":
                self.deal_dmg(attacker, (math.floor(attacker.hp / 2)))
                defender.cursed = True
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} cut its own HP in half and laid a curse on"
                               f" {defender.owner.name}'s {defender.species}")
            else:
                attacker.temp_stats["attack"] += 1
                self.print_txt(f"{attacker.species}'s attack rose!")
                attacker.temp_stats["defense"] += 1
                self.print_txt(f"{attacker.species}'s defense rose!")
                attacker.temp_stats["speed"] -= 1
                self.print_txt(f"{attacker.species}'s speed fell!")
        elif move.get("name") == "Water Sport":
            attacker.water_sport = True
        elif move.get("name") == "Mud Sport":
            attacker.mud_sport = True
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
                self.print_txt("But it failed")
                return
            else:
                attacker.stockpile += 1
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} stockpiled {attacker.stockpile}!")
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
            if attacker == self.player_active and len(self.player.team) > 1:
                self.player_swap(True)
                self.player_active.temp_stats = passer_temp_stats
                self.player_active.confused = passer_confused
                self.player_active.getting_pumped = passer_getting_pumped
                self.player_active.blocking = passer_blocking
                # self.player_active.seeded = passer_seeded
                # self.player_active.curse = passer_curse
                # self.player_active.substitute  = passer_substitute
                # self.player_active.ingrain  = passer_ingrain
                # self.player_active.perish  = passer_perish
            elif attacker == self.opponent_active and len(self.opponent_active) > 1:
                self.opponent_active = random.choice(self.opponent.team)
                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                self.opponent_active.temp_stats = passer_temp_stats
                self.opponent_active.confused = passer_confused
                self.opponent_active.getting_pumped = passer_getting_pumped
                self.opponent_active.blocking = passer_blocking
                # self.opponent_active.seeded = passer_seeded
                # self.opponent_active.curse = passer_curse
                # self.opponent_active.substitute  = passer_substitute
                # self.opponent_active.ingrain  = passer_ingrain
                # self.opponent_active.perish  = passer_perish
            else:
                self.print_txt("But it failed")
    def secondary(self, attacker, defender, move, dmg):
        if move.get("name") == "Tri Attack" and defender.status == "":
            roll = random.uniform(0, 1)
            if roll <= 0.0667:
                defender.status = "BRN"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
                return
            elif roll <= 0.1334:
                defender.status = "PAR"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
                return
            elif roll <= 0.2001:
                defender.status = "FRZ"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
                return
            else:
                return
        if "Trapping" in move.get("flags"):
            attacker.trapping[0] = random.randint(2, 5)
            attacker.trapping[1] = move.get("name")
            if move.get("name") == "Fire Sping" or move.get("name") == "Whirlpool":
                self.print_txt(f"{defender.owner.name}'s {defender.species} was trapped in the vortex!")
            if move.get("name") == "Sand Tomb":
                self.print_txt(f"{defender.owner.name}'s {defender.species} was trapped by sand tomb!")
            if move.get("name") == "Clamp":
                self.print_txt(f"{defender.owner.name}'s {defender.species} was clamped by {attacker.species}!")
            if move.get("name") == "Bind":
                self.print_txt(f"{defender.owner.name}'s {defender.species} was squeezed by {attacker.species}'s bind!")
            if move.get("name") == "Wrap":
                self.print_txt(f"{defender.owner.name}'s {defender.species} was wrapped by {attacker.species}!")
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            self.change_stats(attacker, defender, move)
        if "Flinch" in move.get("flags") and not defender.acted:
            roll = random.uniform(0, 1)
            if roll <= move.get("chance"):
                defender.flinching = True
        if "Confuses" in move.get("flags"):
            roll = random.uniform(0, 1)
            if roll <= move.get("chance"):
                defender.confused = True
        if "Status" in move.get("flags") and defender.status == "":
            roll = random.uniform(0, 1)
            if roll <= move.get("chance"):
                if (move.get("status") == "BRN"
                        and defender.type_one != "Fire" and defender.type_two != "Fire"):
                    defender.status = "BRN"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
                elif (move.get("status") == "FRZ"
                      and defender.type_one != "Ice" and defender.type_two != "Ice"):
                    defender.status = "FRZ"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
                elif move.get("status") == "PAR":
                    defender.status = "PAR"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
                elif (move.get("status") == "PSN" and defender.type_one != "Poison"
                      and defender.type_two != "Poison" and defender.type_one != "Steel"
                      and defender.type_two != "Steel"):
                    defender.status = "PSN"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} was poisoned!")
                elif (move.get("status") == "TOX" and defender.type_one != "Poison"
                      and defender.type_two != "Poison" and defender.type_one != "Steel"
                      and defender.type_two != "Steel"):
                    defender.status = "TOX"
                    self.print_txt(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
                elif move.get("status") == "SLP":
                    if attacker.uproar != 0 or defender.uproar != 0:
                        self.print_txt(
                            f"{defender.owner.name}'s {defender.species} cannot fall asleep due to the uproar!")
                    else:
                        defender.status = "SLP"
                        self.print_txt(f"{defender.owner.name}'s {defender.species} is fast asleep")
        if "Leech" in move.get("flags"):
            if math.floor(dmg * 0.5) == 0:
                self.deal_dmg(attacker, -1)
            else:
                self.deal_dmg(attacker, -math.floor(dmg * 0.5))
        if "Recoil" in move.get("flags"):
            self.deal_dmg(attacker, (math.floor(dmg * move.get("amount"))))
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is hit with recoil!")
        if "Recharge" in move.get("flags"):
            attacker.recharge = True

    def change_stats(self, attacker, defender, move):
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
                        self.print_txt(f"{attacker.species}'s {key} rose sharply!")
                    elif move.get("stat changes").get(key) == 1:
                        self.print_txt(f"{attacker.species}'s {key} rose!")
                    if move.get("stat changes").get(key) == -1:
                        self.print_txt(f"{attacker.species}'s {key} fell!")
                    elif move.get("stat changes").get(key) < -1:
                        self.print_txt(f"{attacker.species}'s {key} harshly fell!")
                    if attacker.temp_stats[key] >= 6:
                        attacker.temp_stats[key] = 6
                        self.print_txt(f"{attacker.species}'s {key} wont go any higher!")
                    elif attacker.temp_stats[key] <= -6:
                        attacker.temp_stats[key] = -6
                        self.print_txt(f"{attacker.species}'s {key} wont go any lower!")
            if "Changes Defender Stats" in move.get("flags"):
                for key in list(move.get("stat changes").keys()):
                    if defender.owner.mist > 0 > move.get("stat changes").get(key):
                        self.print_txt(f"{defender.species} was protected by the mist")
                        continue
                    defender.temp_stats[key] += move.get("stat changes").get(key)
                    if move.get("stat changes").get(key) > 1:
                        self.print_txt(f"{defender.species}'s {key} rose sharply!")
                    elif move.get("stat changes").get(key) == 1:
                        self.print_txt(f"{defender.species}'s {key} rose!")
                    if move.get("stat changes").get(key) == -1:
                        self.print_txt(f"{defender.species}'s {key} fell!")
                    elif move.get("stat changes").get(key) < -1:
                        self.print_txt(f"{defender.species}'s {key} harshly fell!")
                    if defender.temp_stats[key] >= 6:
                        defender.temp_stats[key] = 6
                        self.print_txt(f"{defender.species}'s {key} wont go any higher!")
                    elif defender.temp_stats[key] <= -6:
                        defender.temp_stats[key] = -6
                        self.print_txt(f"{defender.species}'s {key} wont go any lower!")

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
                atk = math.floor(attacker.sp_attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
                dfn = math.floor(defender.sp_defense * self.temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
        if move_type == "Electric":
            if attacker.mud_sport or defender.mud_sport:
                move["power"] = math.floor(move.get("power") / 2)
        if move_type == "Fire":
            if attacker.water_sport or defender.water_sport:
                move["power"] = math.floor(move.get("power") / 2)
        if not move.get("name") != "Solar Beam" and self.weather != "sun" and self.weather != "clear":
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
        elif move.get("name") == "Eruption" or move.get("name") == "Water Spout":
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * (150 * attacker.chp / attacker.hp)) / dfn) / 50)
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
            self.print_txt(f"Magnitude {mag[0]}!")
        else:
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) * atk * move.get("power")) / dfn) / 50)
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
                self.print_txt("But it failed")
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
        for item in self.types:
            if item["name"] == move_type:
                effectiveness = item.get(defender.type_one, 1)
                if defender.type_two is not None:
                    effectiveness = effectiveness * item.get(defender.type_two, 1)
                break
        if effectiveness >= 2 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            self.print_txt("It's super effective", 0)
        if effectiveness <= 0.5 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            self.print_txt("It's not very effective...", 0)
        total = math.floor(total * effectiveness)
        # Check dmg range values
        # for n in range(85, 101):
            # print(math.floor(total * (n / 100)))
        if move.get("name") != "Spit Up":
            total = math.floor((total * random.randint(85, 100)) / 100)
        if total == 0:
            total = 1
        return total

    def crit_check(self, attacker, move):
        crit_roll = random.uniform(0, 1)
        if "High Crit" in move.get("flags") and attacker.getting_pumped:
            if crit_roll <= 0.3333:
                self.print_txt("[color=red]A critical hit[/color]")
                return True
            return False
        elif attacker.getting_pumped:
            if crit_roll <= 0.2500:
                self.print_txt("[color=red]A critical hit[/color]")
                return True
            return False
        elif "High Crit" in move.get("flags"):
            if crit_roll <= 0.1250:
                self.print_txt("[color=red]A critical hit[/color]")
                return True
            return False
        else:
            if crit_roll <= 0.0625:
                self.print_txt("[color=red]A critical hit[/color]")
                return True
            return False

    def alive_check(self):
        swapped = False
        if self.opponent_active is None or self.opponent_active.chp <= 0:
            if self.opponent_active is not None:
                self.opponent.team.remove(self.opponent_active)
                self.opponent_active = None
            if not self.opponent.team:
                self.print_txt(f"{self.player.name} Wins!")
                return True
            self.opponent_active = random.choice(self.opponent.team)
            self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
            self.opponent_active.first_turn = True
            swapped = True
        if self.player_active is None or self.player_active.chp <= 0:
            if self.player_active is not None:
                self.player.team.remove(self.player_active)
                self.player_active = None
            if not self.player.team:
                self.print_txt(f"{self.opponent.name} Wins!")
                return True
            while self.player_active is None:
                terminal.layer(0)
                terminal.put(0, 0, 0xF8FD)
                terminal.layer(1)
                terminal.clear_area(45, 17, 42, 7)
                terminal.printf(45, 18, f"1 {self.player.team[0]}")
                if 1 >= len(self.player.team):
                    terminal.printf(45, 19, "Empty Slot")
                else:
                    terminal.printf(45, 19, f"2 {self.player.team[1]}")
                if 2 >= len(self.player.team):
                    terminal.printf(45, 20, "Empty Slot")
                else:
                    terminal.printf(45, 20, f"3 {self.player.team[2]}")
                if 3 >= len(self.player.team):
                    terminal.printf(45, 21, "Empty Slot")
                else:
                    terminal.printf(45, 21, f"4 {self.player.team[3]}")
                if 4 >= len(self.player.team):
                    terminal.printf(45, 22, "Empty Slot")
                else:
                    terminal.printf(45, 22, f"5 {self.player.team[4]}")
                if 5 >= len(self.player.team):
                    terminal.printf(45, 23, "Empty Slot")
                else:
                    terminal.printf(45, 23, f"6 {self.player.team[5]}")
                self.print_txt("What Pokemon would you like to view/swap? (1-6)", 0)
                button = terminal.read()
                if button == terminal.TK_1:
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[0].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[0].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[0].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[0].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[0].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[0].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[0].moves):
                            terminal.printf(45, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[0].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[0].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[0].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[0].moves[3] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[0].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[0].species}?(Enter/Backspace)"
                                       f"{self.player.team[0].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[0]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break
                elif button == terminal.TK_2 and 2 <= len(self.player.team):
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[1].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[1].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[1].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[1].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[1].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[1].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[1].moves):
                            terminal.printf(45, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[1].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[1].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[1].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[1].moves[3] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[1].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[1].species}?(Enter/Backspace)"
                                       f"{self.player.team[1].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[1]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break
                elif button == terminal.TK_3 and 3 <= len(self.player.team):
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[2].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[2].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[2].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[2].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[2].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[2].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[2].moves):
                            terminal.printf(45, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[2].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[2].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[2].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[3].moves[0] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[2].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[2].species}?(Enter/Backspace)"
                                       f"{self.player.team[2].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[2]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break
                elif button == terminal.TK_4 and 4 <= len(self.player.team):
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[3].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[3].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[3].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[3].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[3].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[3].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[3].moves):
                            terminal.printf(45, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[3].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[3].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[3].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[3].moves[3] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[3].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[3].species}?(Enter/Backspace)"
                                       f"{self.player.team[3].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[3]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break
                elif button == terminal.TK_5 and 5 <= len(self.player.team):
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[4].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[4].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[4].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[4].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[4].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[4].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[4].moves):
                            terminal.printf(55, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[4].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[4].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[4].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[4].moves[3] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[4].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[4].species}?(Enter/Backspace)"
                                       f"{self.player.team[4].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[4]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break
                elif button == terminal.TK_6 and 6 <= len(self.player.team):
                    while True:
                        terminal.clear_area(45, 17, 42, 7)
                        for move in moves:
                            if self.player.team[5].moves[0] == move.get("name"):
                                power = move.get("power")
                                acc = move.get("accuracy")
                                type = move.get("type")
                                break
                        terminal.printf(45, 18, f"Ability: {self.player.team[5].ability}")
                        terminal.printf(45, 19, f"1 {self.player.team[5].moves[0]} {type} Pwr:{power} Acc:{acc}")
                        if 2 > len(self.player.team[5].moves):
                            terminal.printf(45, 20, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[5].moves[1] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 20, f"2 {self.player.team[5].moves[1]} {type} Pwr:{power} Acc:{acc}")
                        if 3 > len(self.player.team[5].moves):
                            terminal.printf(45, 21, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[5].moves[2] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 21, f"3 {self.player.team[5].moves[2]} {type} Pwr:{power} Acc:{acc}")
                        if 4 > len(self.player.team[5].moves):
                            terminal.printf(45, 22, "Empty Slot")
                        else:
                            for move in moves:
                                if self.player.team[5].moves[3] == move.get("name"):
                                    power = move.get("power")
                                    acc = move.get("accuracy")
                                    type = move.get("type")
                                    break
                            terminal.printf(45, 22, f"4 {self.player.team[5].moves[3]} {type} Pwr:{power} Acc:{acc}")
                        self.print_txt(f"Swap to {self.player.team[5].species}?(Enter/Backspace)"
                                       f"{self.player.team[5].info}", 0)
                        button = terminal.read()
                        if button == terminal.TK_ENTER:
                            self.player_active = self.player.team[5]
                            self.player_active.first_turn = True
                            terminal.clear_area(45, 17, 42, 7)
                            self.print_ui()
                            self.print_txt(f"{self.player.name} sent out {self.player_active.species}")
                            if swapped:
                                self.print_txt(f"{self.opponent.name} sent out {self.opponent_active.species}")
                            return
                        if button == terminal.TK_BACKSPACE:
                            break

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
                    terminal.put(23, 14, int(self.player_active.back_sprite, 16))
                    terminal.refresh()
                    time.sleep(0.15)
            x = 61
            y = 17
        else:
            for blink in range(0, 4):
                if amount >= 0:
                    terminal.clear_area(68, 5, 1, 1)
                    terminal.refresh()
                    time.sleep(0.1)
                    terminal.put(68, 5, int(self.opponent_active.front_sprite, 16))
                    terminal.refresh()
                    time.sleep(0.15)
            x = 3
            y = 2
        remaining_health_bars_pre = round(victim.chp / victim.hp * bars)
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
        if amount >= 0:
            for bar in range(0, abs(remaining_health_bars_pre - remaining_health_bars_post)):
                remaining_health_bars_pre -= 1
                if lost_bars + 1 > 20:
                    pass
                else:
                    lost_bars += 1
                terminal.printf(x, y, f"HP: {remaining_health_bars_pre * hp_symbol}{lost_bars * lost_hp}")
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
                terminal.refresh()
                time.sleep(0.1)

    def hp_bars(self):
        hp_symbol = "█"
        lost_hp = "░"
        bars = 20
        opponent_remaining_health_bars = round(self.opponent_active.chp / self.opponent_active.hp * bars)
        if opponent_remaining_health_bars <= 0:
            opponent_lost_bars = bars
        else:
            opponent_lost_bars = bars - opponent_remaining_health_bars
        player_remaining_health_bars = round(self.player_active.chp / self.player_active.hp * bars)
        if player_remaining_health_bars <= 0:
            player_lost_bars = bars
        else:
            player_lost_bars = bars - player_remaining_health_bars
        terminal.clear_area(1, 1, 26, 3)
        terminal.printf(3, 1, f"{self.opponent_active.species} {self.opponent_active.gender}")
        terminal.printf(22, 1, f"Lv{self.opponent_active.level}")
        terminal.printf(3, 2, f"HP: {opponent_remaining_health_bars * hp_symbol}{opponent_lost_bars * lost_hp}")
        if self.opponent_active.chp <= 0:
            terminal.printf(20, 3, f"0/{self.opponent_active.hp}")
        else:
            terminal.printf(20, 3, f"{self.opponent_active.chp}/{self.opponent_active.hp}")
        terminal.clear_area(61, 16, 26, 3)
        terminal.printf(61, 16, f"{self.player_active.species} {self.player_active.gender}")
        terminal.printf(80, 16, f"Lv{self.player_active.level}")
        terminal.printf(61, 17, f"HP: {player_remaining_health_bars * hp_symbol}{player_lost_bars * lost_hp}")
        if self.player_active.chp <= 0:
            terminal.printf(78, 18, f"0/{self.player_active.hp}")
        else:
            terminal.printf(78, 18, f"{self.player_active.chp}/{self.player_active.hp}")
        terminal.refresh()

    def print_txt(self, txt, delay=1.5):
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

    def ai_turn2(self):
        moves = []
        for item in self.opponent_active.moves:
            for move in self.moves:
                if item == move.get("name"):
                    moves.append(move)
                    break
        for move in moves:
            if self.dmg_calc(self.opponent_active, self.player_active, move) >= self.player_active.chp:
                self.ai_move = move
                return
        for move in moves:
            for item in self.types:
                if item["name"] == move.get("type"):
                    effectiveness = item.get(self.player_active.type_one, 1)
                    if self.player_active.type_two is not None:
                        effectiveness = effectiveness * item.get(self.player_active.type_two, 1)
                    if effectiveness >= 2:
                        self.ai_move = move
                        return
        