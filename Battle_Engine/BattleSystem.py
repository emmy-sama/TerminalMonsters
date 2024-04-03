from Helpers.queue_custom import *
from Classes import Ai, Player, Pokemon
from Helpers import get_input
from bearlibterminal import terminal
from Data_Builders import *
import time
import inspect
import math

moves = get_moves()
types = get_type_effectiveness()


def dmg_range(total):
    r = []
    for n in range(85, 101):
        r.append(math.floor(total * (n / 100)))
    print(r)


def grounded(mon):
    if mon.type_one == "Flying" or mon.type_two == "Flying":
        return
    if mon.ability == "Levitate":
        return
    return True


def can_swap(mon_1, mon_2):
    if mon_1.rooted:
        return
    if mon_2.trapping[0] != 0:
        return
    if mon_2.blocking:
        return
    if mon_2.ability in ["Arena Trap", "Magnet Pull", "Shadow Tag"]:
        if mon_2.ability == "Arena Trap" and grounded(mon_1):
            return
        if mon_2.ability == "Magnet Pull":
            if mon_1.type_one == "Steel" or mon_1.type_two == "Steel":
                return
        if mon_2.ability == "Shadow Tag":
            return
    return True


def check_for_status_cure(mon_1):
    if mon_1.ability == "Immunity" and mon_1.status in ["PSN", "TOX"]:
        mon_1.status = ""
        # print pop up
    elif mon_1.ability in ["Insomnia", "Vital Spirit"] and mon_1.status == "SLP":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Limber" and mon_1.status == "PAR":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Magma Armor" and mon_1.status == "FRZ":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Water Veil" and mon_1.status == "BRN":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Own Tempo" and mon_1.confused:
        mon_1.confused = False


class Battle:
    def __init__(self, player, lead, ai):
        self.temp_stat_table_norm = {-6: 2 / 8, -5: 2 / 7, -4: 2 / 6, -3: 2 / 5, -2: 2 / 4, -1: 2 / 3, 0: 2 / 2,
                                     1: 3 / 2, 2: 4 / 2,
                                     3: 5 / 2, 4: 6 / 2, 5: 7 / 2, 6: 8 / 2}
        self.temp_stat_table_acc_eva = {-6: 33 / 100, -5: 36 / 100, -4: 43 / 100, -3: 50 / 100, -2: 60 / 100,
                                        -1: 75 / 100, 0: 100 / 100, 1: 133 / 100, 2: 166 / 100, 3: 200 / 100,
                                        4: 250 / 100, 5: 266 / 100, 6: 300 / 100}
        self.moves = moves
        self.types = types
        self.player = player
        self.player.active = lead
        self.ai = ai
        self.ai.active = ai.team[0]
        self.player.opponent = self.ai
        self.ai.opponent = self.player
        self.weather = "clear"
        self.p_move_last = None
        self.ai_move_last = None
        self.print_ui(True)
        self.finished = False
        self.recurse = False
        self.suspend = []
        self.turn_order = Queue()

    # Main Battle Function
    def battle(self):
        # Handles bringing in lead pokemon
        # pokeball animation
        self.poke_ball_animation(self.player)
        self.print_txt(f"{self.player.name} sent out {self.player.active.species}")
        terminal.clear_area(1, 20, 42, 4)
        self.poke_ball_animation(self.ai)
        self.print_txt(f"{self.ai.name} sent out {self.ai.active.species}")
        # Abilities with entry effects can announce
        if self.player.active.speed < self.ai.active.speed:
            order = [self.player.active, self.ai.active]
        elif self.player.active.speed > self.ai.active.speed:
            order = [self.ai.active, self.player.active]
        else:
            if random.randint(0, 1) == 0:
                order = [self.ai.active, self.player.active]
            else:
                order = [self.player.active, self.ai.active]
        for mon_1 in order:
            mon_2 = mon_1.owner.opponent.active
            if mon_1.status != "" or mon_1.confused:
                check_for_status_cure(mon_1)
            elif mon_1.ability == "Drizzle":
                self.weather = "rain"
                self.print_txt("It started to rain!")
                # print pop up
            elif mon_1.ability == "Drought":
                self.weather = "sun"
                self.print_txt("The sun light got bright!")
                # print pop up
            elif mon_1.ability == "Sand Stream":
                self.weather = "sand"
                self.print_txt("A sand storm brewed!")
                # print pop up
            elif mon_1.ability == "Intimidate":
                self.print_txt(f"{mon_1.owner.name}'s {mon_1.species}'s Intimidate cuts {mon_2.species}'s attack!")
                # print pop up
                self.change_stats(mon_1, mon_2, {"chance": 1, "flags": ["Changes Defender Stats"],
                                                 "stat changes": {"attack": -1}})
        # Berries/Berry Juice/White Herb/Mental Herb can be consumed if applicable
        # Forecast and  abilities can announce themselves if applicable, and cause form changes

        while not self.finished:
            # BackUp Check
            if self.ai.active is None or self.player.active is None:
                self.alive_check()
            # Refreshes Ui
            self.print_ui()
            # AI action select
            if self.can_attack(self.ai.active):
                if self.ai.active.recharge:
                    self.ai.active.recharge = False
                    self.ai.active.loafing = False
                    self.print_txt(f"{self.ai.name}'s {self.ai.active.species} must recharge!")
                else:
                    self.turn_order.put([1, self.ai.active.speed, self.ai_turn().copy(), self.ai])
            # Player action select
            if self.can_attack(self.player.active):
                if self.player.active.recharge:
                    self.player.active.recharge = False
                    self.player.active.loafing = False
                    self.print_txt(f"{self.player.name}'s {self.player.active.species} must recharge!")
                else:
                    a = self.player_turn()
                    if isinstance(a, Pokemon):
                        self.turn_order.put([0, a.speed, a, self.player])
                    else:
                        self.turn_order.put([1, self.player.active.speed, a, self.player])
                    terminal.clear_area(45, 20, 42, 4)

            # Turn processing:
            # Resets rage if rage not used
            rage = self.turn_order.rage()
            if self.player.active.rage and self.player not in rage:
                self.player.active.rage = False
            if self.ai.active.rage and self.ai not in rage:
                self.ai.active.rage = False
            # Quick Claw proc
            # Handles switch ins
            while isinstance(self.turn_order.peek(), Pokemon):
                x = self.turn_order.dequeue()
                x.acted = True
                self.on_switch_in(x)
                # pokeball animation
                # entry hazards
                # Abilities with entry effects can announce
                # Berries/Berry Juice/White Herb/Mental Herb can be consumed if applicable
                # Forecast and  abilities can announce themselves if applicable, and cause form changes
            # Focus Punch message
            for item in self.turn_order.focus_punch():
                self.print_txt(f"{item.name}'s {item.active.species} is tightening its focus!")
            # Calculates Speeds
            if self.turn_order.len() > 1:
                order = self.speed_check(self.turn_order.move_dequeue(), self.turn_order.move_dequeue())
                for item in order:
                    self.turn_order.append(item)
            # Checks if a move is successful then performs it
            while self.turn_order.peek() is not None:
                x = self.turn_order.move_dequeue()
                if x[3].active is not None and x[3].active.chp > 0:
                    try:
                        result = self.move_clearance(x[3].active, x[3].opponent.active, x[2])
                        if result == "Failed":
                            self.print_txt("But it failed")
                        elif result == "Failed No Text":
                            pass
                        elif result == "Suspend":
                            self.suspend.append([x[2], x[3].active])
                        elif result == "Passed":
                            self.perform_move(x[3].active, x[3].opponent.active, x[2])
                        x[3].active.acted = True
                    except AttributeError:
                        self.print_txt("But it failed")
                        x[3].active.acted = True
                # Cures pokemon with curing abilities
                if self.player.active is not None:
                    if self.player.active.status != "" or self.player.active.confused:
                        check_for_status_cure(self.player.active)
                if self.ai.active is not None:
                    if self.ai.active.status != "" or self.ai.active.confused:
                        check_for_status_cure(self.ai.active)
                if self.player.active is not None and self.player.active.chp <= 0:
                    self.player.team.remove(self.player.active)
                    self.player.active = None
                if self.ai.active is not None and self.ai.active.chp <= 0:
                    self.ai.team.remove(self.ai.active)
                    self.ai.active = None
            # End of turn effects
            self.end_of_turn_effects()

    def can_attack(self, trainer_mon):
        for data in self.suspend:
            if trainer_mon in data:
                self.turn_order.put([1, data[1].speed, data[0], data[1].owner])
                self.suspend.remove(data)
                return False
        if trainer_mon.bide > 0:
            self.turn_order.put([1, trainer_mon.speed, self.moves.get("Bide"), trainer_mon.owner])
        elif trainer_mon.uproar > 0:
            self.turn_order.put([1, trainer_mon.speed, self.moves.get("Uproar"), trainer_mon.owner])
        else:
            return True

# UI Functions
    def print_ui(self, first_turn=False):
        terminal.layer(0)
        terminal.put(0, 0, 0xF8FF)
        terminal.layer(1)
        if self.player.active is not None and self.ai.active is not None and not first_turn:
            self.hp_bars()
        terminal.refresh()

    @staticmethod
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

    def poke_ball_animation(self, side):
        if isinstance(side, Player):
            path = [[0, 13], [2, 12], [4, 11], [6, 11], [8, 11], [10, 12], [12, 13], [14, 14], [16, 15], [18, 16],
                    [20, 17], [22, 18]]
            for cord in path:
                terminal.clear_area(0, 11, 30, 8)
                terminal.put(cord[0], cord[1], 0xF8F4)
                terminal.refresh()
                time.sleep(0.1)
            terminal.clear_area(0, 11, 30, 8)
            terminal.put(22, 18, 0xF8F3)
            terminal.refresh()
            time.sleep(0.1)
            terminal.clear_area(0, 11, 30, 8)
            terminal.put(22, 18, 0xF8F2)
            terminal.refresh()
            time.sleep(0.2)
            terminal.clear_area(0, 11, 30, 8)
            self.hp_bars(ai=False)
            terminal.put(23, 14, int(side.active.back_sprite, 16))
        if isinstance(side, Ai):
            path = [[87, 4], [86, 3], [84, 2], [82, 2], [80, 2], [78, 3], [76, 4], [74, 5], [72, 6], [70, 7], [68, 8],
                    [66, 9]]
            for cord in path:
                terminal.clear_area(68, 2, 30, 8)
                terminal.put(cord[0], cord[1], 0xF8F4)
                terminal.refresh()
                time.sleep(0.1)
            terminal.clear_area(66, 2, 30, 8)
            terminal.put(66, 9, 0xF8F3)
            terminal.refresh()
            time.sleep(0.1)
            terminal.clear_area(66, 2, 30, 8)
            terminal.put(66, 9, 0xF8F2)
            terminal.refresh()
            time.sleep(0.2)
            terminal.clear_area(66, 2, 30, 8)
            self.hp_bars(player=False)
            terminal.put(66, 5, int(side.active.front_sprite, 16))

    def faint(self, mon):
        if isinstance(mon.owner, Player):
            terminal.clear_area(23, 14, 1, 1)
            terminal.clear_area(61, 16, 26, 3)
            terminal.refresh()
        elif isinstance(mon.owner, Ai):
            terminal.clear_area(66, 5, 1, 1)
            terminal.clear_area(1, 1, 26, 3)
            terminal.refresh()

    def hp_bars(self, ai=True, player=True):
        hp_symbol = "█"
        lost_hp = "░"
        bars = 20
        if ai:
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
        if player:
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
                    terminal.clear_area(66, 5, 1, 1)
                    terminal.refresh()
                    time.sleep(0.1)
                    terminal.put(66, 5, int(self.ai.active.front_sprite, 16))
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
        if abs(remaining_health_bars_post - remaining_health_bars_pre) == 0:
            if amount > 0:
                if amount > temp_hp:
                    dmg = temp_hp
                else:
                    dmg = amount
            else:
                if amount - temp_hp > victim.hp:
                    dmg = victim.hp - temp_hp
                else:
                    dmg = amount
        elif amount > 0:
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

# Ai action select functions

    def ai_turn(self):
        ai_random = random.choice(self.ai.active.moves)
        return self.moves.get(ai_random)

# Player action select functions
    def player_turn(self):
        while True:
            terminal.clear_area(45, 20, 60, 4)
            terminal.printf(45, 20, "1 Fight\n2 Pokemon")
            self.print_txt("What will you do?", 0)
            i = get_input(2)
            if i == 0:
                self.print_moves(self.player.team.index(self.player.active))
                while True:
                    self.print_txt("What move would you like to use?(1-4)", 0)
                    i = get_input(4, is_backspace_used=True)
                    if i == 42:
                        break
                    else:
                        move = self.moves.get(self.player.active.moves[i])
                        self.print_txt(f"Use {move.get("name")}?(Enter/Backspace) {move.get("description")}", 0)
                        while True:
                            i = get_input(is_enter_used=True, is_backspace_used=True)
                            if i == 40:
                                return move.copy()
                            elif i == 42:
                                break
            elif i == 1:
                a = self.player_swap(False)
                if a is not None:
                    return a

    def print_moves(self, slot):
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
            self.print_txt("What Pokemon would you like to view/swap? (1-6)", 0)
            i = get_input(6, is_backspace_used=True)
            if i == 42 and not must_swap:
                terminal.clear_area(45, 17, 42, 7)
                self.print_ui()
                break
            elif i + 1 <= len(self.player.team):
                while True:
                    terminal.clear_area(45, 17, 42, 7)
                    self.print_ui()
                    self.print_moves(i)
                    self.print_txt(f"Swap to {self.player.team[i].species}?(Enter/Backspace)"
                                   f"{self.player.team[i].info}", 0)
                    x = get_input(is_enter_used=True, is_backspace_used=True)
                    if x == 40:
                        if not must_swap and not can_swap(self.player.active, self.ai.active):
                            self.print_txt(f"{self.player.active.species} is trapped and cant switch out!")
                            break
                        if self.player.active == self.player.team[i]:
                            self.print_txt(f"{self.player.team[i].species} is already out")
                            break
                        if self.player.active is not None:
                            if self.player.active.ability == "Natural Cure" and self.player.active.status != "":
                                # print pop up
                                self.print_txt(f"{self.player.name}'s {self.player.active.species}'s cured it's status")
                                self.player.active.status = ""
                            self.player.active.reset_temp()
                        return self.player.team[i]
                    if x == 42:
                        break

# Handles switching in new mons
    def on_switch_in(self, mon_1):
        mon_1.owner.active = mon_1
        # pokeball animation
        mon_2 = mon_1.owner.opponent.active
        terminal.clear_area(1, 20, 42, 4)
        terminal.clear_area(45, 20, 42, 4)
        self.poke_ball_animation(mon_1.owner)
        self.print_txt(f"{mon_1.owner.name} sent out {mon_1.species}")
        # entry hazards
        # Abilities with entry effects can announce
        if mon_1.status != "" or mon_1.confused:
            check_for_status_cure(mon_1)
        elif mon_1.ability == "Drizzle":
            self.weather = "rain"
            self.print_txt("It started to rain!")
            # print pop up
        elif mon_1.ability == "Drought":
            self.weather = "sun"
            self.print_txt("The sun light got bright!")
            # print pop up
        elif mon_1.ability == "Sand Stream":
            self.weather = "sand"
            self.print_txt("A sand storm brewed!")
            # print pop up
        elif mon_1.ability == "Intimidate":
            self.print_txt(f"{mon_1.owner.name}'s {mon_1.species}'s Intimidate cuts {mon_2.species}'s attack!")
            # print pop up
            self.change_stats(mon_1, mon_2, {"chance": 1, "flags": ["Changes Defender Stats"],
                                             "stat changes": {"attack": -1}})
        # Berries/Berry Juice/White Herb/Mental Herb can be consumed if applicable
        # Forecast and  abilities can announce themselves if applicable, and cause form changes

# Calculates speed of each mon
    def speed_check(self, mon_1, mon_2):
        # Checks priority
        if mon_1[2].get("priority") > mon_2[2].get("priority"):
            return [mon_1, mon_2]
        if mon_1[2].get("priority") < mon_2[2].get("priority"):
            return [mon_2, mon_1]

        # Normal speed calcs
        mon_1_speed = math.floor(
            mon_1[3].active.speed * self.temp_stat_table_norm.get(mon_1[3].active.temp_stats.get("speed")))
        if mon_1[3].active.ability == "Chlorophyll" and self.weather == "sun":
            mon_1_speed = math.floor(mon_1_speed * 2)
        if mon_1[3].active.ability == "Swift Swim" and self.weather == "rain":
            mon_1_speed = math.floor(mon_1_speed * 2)
        if mon_1[3].active.status == "PAR":
            mon_1_speed = math.floor(mon_1_speed * 0.25)
        mon_2_speed = math.floor(
            mon_2[3].active.speed * self.temp_stat_table_norm.get(mon_2[3].active.temp_stats.get("speed")))
        if mon_2[3].active.ability == "Chlorophyll" and self.weather == "sun":
            mon_2_speed = math.floor(mon_2_speed * 2)
        if mon_2[3].active.ability == "Swift Swim" and self.weather == "rain":
            mon_2_speed = math.floor(mon_2_speed * 2)
        if mon_2[3].active.status == "PAR":
            mon_2_speed = math.floor(mon_2_speed * 0.25)

        # Returns Turn Order
        if mon_1_speed > mon_2_speed:
            return [mon_1, mon_2]
        if mon_1_speed < mon_2_speed:
            return [mon_2, mon_1]
        if random.randint(0, 1) == 0:
            return [mon_1, mon_2]
        else:
            return [mon_2, mon_1]

# Preforms checks to see if move is successful
    def move_clearance(self, attacker, defender, move):
        if attacker.chp <= 0:
            return "Failed No Text"
        attacker.bonded = False
        # Checks if user is asleep or frozen
        if attacker.status == "SLP":
            if move.get("name") == "Snore":
                pass
            elif move.get("name") == "Sleep Talk":
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
                if not valid_moves:
                    return "Failed"
                move = random.choice(valid_moves)
            else:
                if attacker.sleep_turns == 0:
                    attacker.sleep_turns = random.randint(1, 5)
                    if attacker.ability == "Early Bird":
                        attacker.sleep_turns = math.floor(attacker.sleep_turns / 2)
                else:
                    attacker.sleep_turns -= 1
                if attacker.sleep_turns == 0 or defender.ability != "Soundproof" and defender.uproar != 0:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} woke up!")
                    attacker.status = ""
                else:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} is fast asleep!")
                    return "Failed No Text"
        if attacker.status == "FRZ" and "Thaws" not in move.get("flags"):
            if random.randint(1, 100) <= 20:
                attacker.status = ""
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} thawed it's self out!")
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is frozen solid!")
                return "Failed No Text"
        # Checks for truant loafing turn
        if attacker.ability == "Truant":
            if attacker.loafing:
                attacker.flinching = False
                attacker.charged = False
                attacker.semi_invulnerable = None
                # print pop up
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is loafing around!")
                attacker.loafing = False
                return "Failed No Text"
            else:
                attacker.loafing = True
        # focus punch check
        if move.get("name") == "Focus Punch" and attacker.damaged_this_turn:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} lost its focus and couldn't move!")
            return "Failed No Text"
        # flinch
        if attacker.flinching:
            attacker.flinching = False
            attacker.charged = False
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} flinched!")
            return "Failed No Text"
        # confusion
        if attacker.confused:
            pass
        # para
        if attacker.status == "PAR":
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is paralyzed! It may be unable to move!")
            if random.randint(1, 100) <= 25:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is paralyzed! It can't move!")
                return "Failed No Text"
            else:
                pass
        # attraction
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
        # check pp
        # check disabled
        # check choice locked
        # check taunt
        # check imprison
        # Set Rage
        if move.get("name") == "Rage":
            attacker.rage = True
        # if holding choice item lock move
        # if move calls another move repeat replace move now
        if move.get("name") == "Metronome":
            while True:
                move = random.choice(list(self.moves.values()))
                if "Metronome" in move.get("flags"):
                    break
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
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
                return "Failed"
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} used {move.get("name")}")
                move = random.choice(choices)
        # set typing for hidden power, weather ball
        # subtract pp (if called subtract from og move)
        # move failure conditions pt1
            # fake out defender all ready acted
        if move.get("name") == "Fake Out":
            if attacker.first_turn is False:
                return "Failed"
            # protection move fail if no other moved queue, or rng fail
        elif move.get("name") == "Protect" or move.get("name") == "Detect" or move.get("name") == "Endure":
            if attacker.protecting_chance < random.uniform(0, 1) or defender.acted:
                return "Failed"
            # stockpile and stacks at 3
        elif move.get("name") == "Stockpile":
            if attacker.stockpile == 3:
                return "Failed"
            # swallow/spit up and stacks at 0
        elif move.get("name") == "Swallow" or move.get("name") == "Spit Up":
            if attacker.stockpile == 0:
                return "Failed"
            # bide and energy = 0
        elif move.get("name") == "Bide":
            if attacker.bide == 2 and attacker.bide_dmg == 0:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} unleashed energy")
                attacker.bide = 0
                return "Failed"
            # nothing to counter/mirror coat
        elif move.get("name") == "Counter":
            if attacker.dmg_last_taken <= 0 and attacker.dmg_last_type_taken != "Physical":
                return "Failed"
        elif move.get("name") == "Mirror Coat":
            if attacker.dmg_last_taken <= 0 and attacker.dmg_last_type_taken != "Special":
                return "Failed"
            # encore and target hasn't used a more, or it has no pp or is exempt
            # rest full hp or already asleep
        elif move.get("name") == "Rest":
            if attacker.chp == attacker.hp or attacker.status == "SLP":
                return "Failed"
            # rest user has insomnia/vital spirit
            if attacker.ability == "Insomnia" or attacker.ability == "Vital Spirit":
                return "Failed"
            # snore/sleep talk and user is not asleep
        elif move.get("name") in ["Snore", "Sleep Talk"]:
            if attacker.status != "SLP":
                return "Failed"
            # future move and future move all ready queued
        # if thaws unthaw user
        if "Thaws" in move.get("flags"):
            attacker.status = ""
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} thawed it's self out!")
        # if future move do effect and exit (no fail)
        # check if move fails due to damp
        if "Explode" in move.get("flags"):
            if defender.ability == "Damp" or attacker.ability == "Damp":
                # print pop up
                return "Failed"
        # if move needs charging suspend move and do effects unless solar beam in sun (no fail)
        if "Charge" in move.get("flags") and attacker.charged is False:
            if move.get("name") == "Skull Bash":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} lowered it's head!")
                attacker.temp_stats["defense"] += 1
                self.print_txt(f"{attacker.species}'s defense rose!")
            elif move.get("name") == "Solar Beam":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} took in the sunlight!")
            elif move.get("name") == "Razor Wind":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} whipped up a whirlwind!")
            elif move.get("name") == "Sky Attack":
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is glowing!")
            if move.get("name") != "Solar Beam" or self.weather != "sun":
                attacker.charged = True
                return "Suspend"
        elif "Charge" in move.get("flags"):
            attacker.charged = False
        # check for failure due to lack of targets
        if defender is None:
            if ("Requires Target" in move.get("flags") or move.get("category") == "Special"
                    or move.get("category") == "Physical"):
                return "Failed"
        # check if move stolen by pending snatch (go back to check choice locked)
        # if move explode deal 100% max hp
        if "Explode" in move.get("flags"):
            self.deal_dmg(attacker, attacker.hp)
        # move failure conditions pt2
        # rest if uproar active
        if move.get("name") == "Rest":
            if attacker.ability != "Soundproof" and defender.uproar != 0:
                return "Failed"
            # recovery move and user 100% hp
        elif "Raises Attacker chp by hp" in move.get("flags") or "Synthesis" in move.get("flags"):
            if attacker.chp == attacker.hp:
                return "Failed"
            # substitute/belly drum and not enough hp
        elif move.get("name") == "Substitute":
            if attacker.chp <= math.floor(attacker.hp * 0.25):
                return "Failed"
        elif move.get("name") == "Belly Drum":
            if attacker.chp <= math.floor(attacker.hp * 0.50):
                return "Failed"
            # conversion/camo is already the type
            # conversion 2 no prior move or all resistances are already users type
        # Checks if defender is semi invulnerable
        if defender.semi_invulnerable is not None:
            if (defender.semi_invulnerable == "bounce" or defender.semi_invulnerable == "fly" and
                    "Bypass Fly" not in move.get("flags")):
                self.print_txt(f"{attacker.species} Missed!")
                return "Failed No Text"
            elif defender.semi_invulnerable == "dig" and "Bypass Dig" not in move.get("flags"):
                self.print_txt(f"{attacker.species} Missed!")
                return "Failed No Text"
            elif defender.semi_invulnerable == "dive" and "Bypass Dive" not in move.get("flags"):
                self.print_txt(f"{attacker.species} Missed!")
                return "Failed No Text"
            if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                dmg = self.dmg_calc(attacker, defender, move)
                self.deal_dmg(attacker, (dmg / 2))
        # check if move is blocked by protect/detect
        if defender.protecting and "Protect" in move.get("flags"):
            if move.get("name") == "Bide" and attacker.bide != 2:
                pass
            else:
                self.print_txt(f"{defender.species} protected it's self")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                elif move.get("name") == "Memento":
                    self.deal_dmg(attacker, attacker.hp)
                return "Failed No Text"
        # Checks if move is reflectable and then reflects it if it is
        if defender.reflecting and "Reflectable" in move.get("flags"):
            self.print_txt(f"{attacker.owner.name}'s {attacker.species}'s {move.get("name")} was bounced back!")
            temp = attacker
            attacker = defender
            defender = temp
        # check for ability-based immunities pt 1
            # flash fire
        if move.get("type") == "Fire":
            if defender.ability == "Flash Fire" and defender.status != "FRZ":
                # print pop up
                self.print_txt("It had no effect")
                defender.flash_fired = True
                return "Failed No Text"
            # water absorb
        elif move.get("type") == "Water":
            if defender.ability == "Water Absorb":
                # print pop up
                self.print_txt("It had no effect")
                self.deal_dmg(defender, -math.floor(defender.hp / 4))
                return "Failed No Text"
            # lightning rod/volt absorb
        elif move.get("type") == "Electric":
            if defender.ability == "Lightning Rod":
                # print pop up
                self.print_txt("It had no effect")
                if defender.type_one != "Ground" and defender.type_two != "Ground":
                    self.change_stats(defender, attacker, {"chance": 1, "flags": ["Changes Attacker Stats"],
                                                           "stat changes": {"sp_attack": 1}})
                return "Failed No Text"
            elif defender.ability == "Volt Absorb" and move.get("category") != "Non-Damaging":
                # print pop up
                self.print_txt("It had no effect")
                self.deal_dmg(defender, -math.floor(defender.hp / 4))
                return "Failed No Text"
            # soundproof
        if "Sound" in move.get("flags") and defender.ability == "Soundproof":
            # print pop up
            self.print_txt("It had no effect")
            return "Failed No Text"
            # wonder guard
        if defender.ability == "Wonder Guard":
            if move.get("category") != "Non-Damaging" and "Typeless" not in move.get("flags"):
                effectiveness = self.types.get(move.get("type")).get(defender.type_one, 1)
                if defender.type_two is not None:
                    effectiveness = effectiveness * self.types.get(move.get("type")).get(defender.type_two, 1)
                if effectiveness < 2:
                    # print pop up
                    self.print_txt("It had no effect")
                    return "Failed No Text"
        # If move is thunder wave or a damaging move check for type immunity
        if move.get("name") == "Thunder Wave" or move.get("category") != "Non-Damaging":
            if move.get("type") == "Ghost":
                if defender.type_one == "Normal" or defender.type_two == "Normal":
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Ground":
                if not grounded(defender):
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Electric":
                if defender.type_one == "Ground" or defender.type_two == "Ground":
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Normal":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Fighting":
                if defender.type_one == "Ghost" or defender.type_two == "Ghost":
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Poison":
                if defender.type_one == "Steel" or defender.type_two == "Steel":
                    self.print_txt("It had no effect")
                    return "Failed No Text"
            elif move.get("type") == "Psychic":
                if move.get("category") == "Special" or move.get("category") == "Physical":
                    if defender.type_one == "Dark" or defender.type_two == "Dark":
                        self.print_txt("It had no effect")
                        return "Failed No Text"
        # check for type-based move condition immunities
            # fire immune to burning moves
        if move.get("name") == "Will-O-Wisp":
            if defender.type_one == "Fire" or defender.type_two == "Fire":
                self.print_txt("It had no effect")
                return "Failed No Text"
            # poisoning moves (poison/steel)
        elif move.get("name") == "Toxic" or move.get("name") == "Poison Powder" or move.get("name") == "Poison Gas":
            if (defender.type_one == "Steel" or defender.type_two == "Steel"
                    or defender.type_one == "Poison" or defender.type_two == "Poison"):
                self.print_txt("It had no effect")
                return "Failed No Text"
        # check for other move condition immunities
            # dream eater/ nightmare target is awake
        if move.get("name") == "Dream Eater" or move.get("name") == "Nightmare":
            if defender.status != "SLP":
                return "Failed"
            # attract gender fail
            # endeavor target has less hp then user
        elif move.get("name") == "Endeavor":
            if attacker.chp >= defender.chp:
                return "Failed"
            # OHKO moves and target is higher level
        elif "OHKO" in move.get("flags"):
            if attacker.level < defender.level:
                self.print_txt(f"{attacker.species} Missed!")
                return "Failed No Text"
        # check for ability-based immunities, part 2
            # sturdy and OHKO move
        if "OHKO" in move.get("flags"):
            if defender.ability == "Sturdy":
                # print pop up
                return "Failed"
            # sticky hold (trick)
            # oblivious (attract/taunt)
        # check for generic move failure due to redundancy (Confusion/Infatuated also)
            # status move and target is all ready statused
        if move.get("category") == "Non-Damaging" and "Status" in move.get("flags"):
            if defender.status != "":
                return "Failed"
        elif move.get("category") == "Non-Damaging" and "Confuses" in move.get("flags"):
            if defender.confused:
                return "Failed"
            # attempted creation of weather/Leech Seed/Curse/Nightmare/Encore/Perish song that already exists
        elif "Weather" in move.get("flags"):
            if self.weather != "clear":
                if move.get("name") == "hail":
                    if self.weather == "hail":
                        return "Failed"
                elif move.get("name") == "Rain Dance":
                    if self.weather == "rain":
                        return "Failed"
                elif move.get("name") == "Sandstorm":
                    if self.weather == "sand":
                        return "Failed"
                elif move.get("name") == "Sunny Day":
                    if self.weather == "sun":
                        return "Failed"
        elif move.get("name") == "Curse":
            if attacker.type_one == "Ghost" or attacker.type_two == "Ghost":
                if defender.cursed:
                    return "Failed"
            # stat changing moves that can't go any higher or lower
        elif "Changes Attacker Stats" in move.get("flags") and move.get("category") == "Non-Damaging":
            for key in list(move.get("stat changes").keys()):
                if attacker.temp_stats[key] >= 6:
                    self.print_txt(f"{attacker.species}'s {key} wont go any higher!")
                    return "Failed No Text"
                elif attacker.temp_stats[key] <= -6:
                    self.print_txt(f"{attacker.species}'s {key} wont go any lower!")
                    return "Failed No Text"
        elif "Changes Defender Stats" in move.get("flags") and move.get("category") == "Non-Damaging":
            for key in list(move.get("stat changes").keys()):
                if defender.temp_stats[key] >= 6:
                    self.print_txt(f"{defender.species}'s {key} wont go any higher!")
                    return "Failed No Text"
                elif defender.temp_stats[key] <= -6:
                    self.print_txt(f"{defender.species}'s {key} wont go any lower!")
                    return "Failed No Text"
                    # trick and no item or unmovable item
            # disable/sketch and no moves or ineligible move
        # blocked by safeguard
        # blocked by Insomnia/Vital Spirit
        if move.get("name") == "Yawn" or "SLP" in move.get("status", "N/A"):
            if defender.ability == "Insomnia" or defender.ability == "Vital Spirit":
                return "Failed"
        # check move accuracy
        if attacker.ability == "Compound Eyes" and move.get("accuracy") != 0:
            move["accuracy"] = move.get("accuracy") * 1.3
        elif attacker.ability == "Hustle" and move.get("accuracy") != 0:
            if move.get("category") != "Special" and move.get("type") in ["Normal", "Fighting", "Flying", "Poison",
                                                                          "Ground", "Rock", "Bug", "Ghost", "Steel"]:
                move["accuracy"] = move.get("accuracy") * 0.8
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
                return "Failed No Text"
        elif "OHKO" in move.get("flags"):
            hit_check = random.randint(1, 100)
            accuracy = math.floor(30 + (attacker.level - defender.level))
            if hit_check >= accuracy:
                self.print_txt(f"{attacker.species} Missed!")
                return "Failed No Text"
        elif move.get("accuracy") != 0:
            hit_check = random.randint(1, 100)
            accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
            if accuracy_stage > 6:
                accuracy_stage = 6
            elif accuracy_stage < -6:
                accuracy_stage = -6
            accuracy = move.get("accuracy") * self.temp_stat_table_acc_eva.get(accuracy_stage)
            if self.weather == "sand" and defender.ability == "Sand Veil":
                accuracy = math.floor(accuracy * 0.8)
            if hit_check > accuracy:
                self.print_txt(f"{attacker.species} Missed!")
                if move.get("name") == "Jump Kick" or move.get("name") == "High Jump Kick":
                    dmg = self.dmg_calc(attacker, defender, move)
                    self.deal_dmg(attacker, (dmg / 2))
                return "Failed No Text"
        # blocked by substitute
        # blocked by mist
        if defender.owner.mist > 0:
            if "Changes Defender Stats" in move.get("flags"):
                if move.get("name") != "Swagger" and move.get("name") != "Flatter":
                    self.print_txt(f"{defender.species} was protected by the mist")
                    return "Failed No Text"
        # check for ability-based immunities, part 3
            # clear body/white smoke (all stat drop moves)
        if defender.ability == "Clear Body" or defender.ability == "White Smoke":
            if "Changes Defender Stats" in move.get("flags"):
                if move.get("name") != "Swagger" and move.get("name") != "Flatter":
                    return "Failed"
            # hyper cutter (attack drop moves)
        elif defender.ability == "Hyper Cutter":
            if "Changes Defender Stats" in move.get("flags") and "attack" in move.get("stat changes"):
                if move.get("name") != "Swagger":
                    return "Failed"
            # keen eye (accuracy drop moves)
        elif defender.ability == "Keen Eye":
            if "Changes Defender Stats" in move.get("flags") and "accuracy" in move.get("stat changes"):
                return "Failed"
            # water veil (burn moves)
        elif defender.ability == "Water Veil":
            if move.get("name") == "Will-O-Wisp":
                return "Failed"
            # immunity (poisoning moves)
        elif defender.ability == "Immunity":
            if move.get("name") == "Toxic" or move.get("name") == "Poison Powder" or move.get("name") == "Poison Gas":
                return "Failed"
            # limber (para moves)
        elif defender.ability == "Limber":
            if "Status" in move.get("flags") and move.get("status") == "PAR" and move.get("category") == "Non-Damaging":
                return "Failed"
            # own tempo (confusion moves)
        elif defender.ability == "Own Tempo":
            if "Confuses" in move.get("flags") and move.get("category") == "Non-Damaging":
                return "Failed"
            # suction cups (roar, whirlwind)
        elif defender.ability == "Suction Cups":
            if move.get("name") == "Roar" or move.get("name") == "Whirlwind":
                return "Failed"
        # if roar or whirlwind check for ingrain
        if move.get("name") == "Roar" or move.get("name") == "Whirlwind":
            if defender.rooted:
                return "Failed"
        # brick break side effect now
        if move.get("name") == "Brick Break":
            if defender.owner.reflect > 0 or defender.owner.light_screen > 0:
                defender.owner.reflect = 0
                defender.owner.light_screen = 0
                self.print_txt("The wall shattered!")
        return "Passed"

# Performs moves
    def perform_move(self, attacker, defender, move):
        dmg = 0
        # Status Moves
        # Do Conversion 2, Grudge,  Imprison,
        # Memento, Mimic, Mirror Move, Nightmare, Pain Split, Perish Song, Recycle, Rest, Role Play, Safeguard, Sketch,
        # Skill Swap, Snatch, Spikes, Substitute, Teleport, Transform, Wish, Yawn, Attract, Encore, Foresight, Lock-On,
        # Mind Reader, Odor Sleuth, Spite, Taunt, Torment, Trick, Whirlwind, Disable, Leech Seed, Nature Power
        if "Raises Attacker chp by hp" in move.get("flags"):
            if move.get("name") == "Swallow":
                hp_change = [0.25, 0.50, 1]
                self.deal_dmg(attacker, -math.floor(attacker.hp * hp_change[attacker.stockpile - 1]))
                attacker.stockpile = 0
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp * move.get("hp changes")))
        elif "Weather" in move.get("flags"):
            if move.get("name") == "hail":
                self.weather = "hail"
                self.print_txt("It started to hail!")
            elif move.get("name") == "Rain Dance":
                self.weather = "rain"
                self.print_txt("It started to rain!")
            elif move.get("name") == "Sandstorm":
                self.weather = "sand"
                self.print_txt("A sand storm brewed!")
            elif move.get("name") == "Sunny Day":
                self.weather = "sun"
                self.print_txt("The sun light got bright!")
        elif "Synthesis" in move.get("flags"):
            if self.weather == "clear":
                self.deal_dmg(attacker, -math.floor(attacker.hp / 2))
            elif self.weather == "sun":
                self.deal_dmg(attacker, -math.floor(attacker.hp * 0.66))
            else:
                self.deal_dmg(attacker, -math.floor(attacker.hp / 4))
        elif move.get("category") == "Non-Damaging":
            s = move.get("name").lower()
            s = s.replace(" ", "_")
            a = getattr(self, s, None)
            if a:
                sig = str(inspect.signature(a))
                if "attacker" and "defender" in sig:
                    a(attacker=attacker, defender=defender)
                elif "attacker" in sig:
                    a(attacker)
                else:
                    a(defender)

        # Special Damaging moves
        elif "Semi-invulnerable" in move.get("flags") and attacker.semi_invulnerable is None:
            if attacker.semi_invulnerable is None:
                if move.get("name") == "Bounce":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} sprang up!")
                elif move.get("name") == "Dig":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} dug a hole!")
                elif move.get("name") == "Dive":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} hide underwater!")
                elif move.get("name") == "Fly":
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} flew up high!")
                attacker.semi_invulnerable = move.get("name")
                self.suspend.append([move, attacker])
                return
        elif move.get("name") == "Triple Kick":
            self.triple_kick(attacker, defender, move)
        elif move.get("name") == "Beat Up":
            self.beat_up(attacker, defender, move)
        # Everything Else
        else:
            if "Level Damage" in move.get("flags"):
                dmg = attacker.level
            elif "Fixed Damage" in move.get("flags"):
                dmg = move.get("amount")
            elif "Semi-invulnerable" in move.get("flags"):
                attacker.semi_invulnerable = None
                dmg = self.dmg_calc(attacker, defender, move)
            elif "OHKO" in move.get("flags"):
                self.print_txt("It's a one-hit KO!")
                dmg = defender.hp
            elif move.get("name") == "Present":
                dmg = self.present(attacker, defender, move)
                if dmg == 0:
                    return
            elif move.get("name") == "Bide":
                dmg = self.bide(attacker, defender, move)
                if dmg == 0:
                    return
            else:
                s = move.get("name").lower()
                s = s.replace(" ", "_")
                a = getattr(self, s, None)
                if a:
                    sig = str(inspect.signature(a))
                    if "attacker" and "defender" in sig:
                        dmg = a(attacker, defender, move)
                    elif "attacker" in sig:
                        dmg = a(attacker, move)
                    else:
                        dmg = a(defender, move)
                else:
                    # Do Secret Power, Covet, Knock Off, Thief, Struggle, Pursuit, Rapid Spin, Doom Desire, Future Sight
                    dmg = self.dmg_calc(attacker, defender, move)
                    if move.get("name") == "False Swipe" and dmg >= defender.chp:
                        dmg = defender.chp - 1
            if dmg > 0:
                if defender.enduring and dmg >= defender.chp:
                    dmg = defender.chp - 1
                self.deal_dmg(defender, dmg)
                defender.damaged_this_turn = True
                defender.dmg_last_type_taken = move.get("category")
                defender.dmg_last_taken = dmg
                if defender.bide != 0:
                    defender.bide_dmg += dmg
        # Status effects
        if defender.ability != "Shield Dust" and defender.chp > 0:
            if move.get("name") == "Tri Attack" and defender.status == "":
                roll = random.uniform(0, 1)
                if roll <= 0.0667:
                    self.give_status(attacker, defender, "BRN", False)
                elif roll <= 0.1334:
                    self.give_status(attacker, defender, "PAR", False)
                elif roll <= 0.2001:
                    self.give_status(attacker, defender, "FRZ", False)
            elif "Flinch" in move.get("flags") or attacker.ability == "Stench":
                if defender.acted:
                    pass
                elif defender.ability == "Inner Focus":
                    if "Flinch" in move.get("flags") and move.get("chance") == 1:
                        # print pop up
                        self.print_txt(f"{defender.owner.name}'s {defender.species}'s Inner Focus prevents flinching!")
                else:
                    if attacker.ability == "Serene Grace":
                        move["chance"] = move.get("chance") * 2
                    if "Flinch" not in move.get("flags"):
                        if random.uniform(0, 1) <= 0.1:
                            defender.flinching = True
                    elif random.uniform(0, 1) <= move.get("chance"):
                        defender.flinching = True
            elif "Confuses" in move.get("flags") and defender.ability != "Own Tempo" and not defender.confused:
                if attacker.ability == "Serene Grace":
                    move["chance"] = move.get("chance") * 2
                if random.uniform(0, 1) <= move.get("chance"):
                    self.print_txt(f"{defender.owner.name}'s {defender.species} became confused!")
                    defender.confused = True
            elif "Status" in move.get("flags") and defender.status == "":
                if attacker.ability == "Serene Grace":
                    move["chance"] = move.get("chance") * 2
                if random.uniform(0, 1) <= move.get("chance"):
                    self.give_status(attacker, defender, move.get("status"), False)
        # Uproar
        if move.get("name") == "Uproar" and attacker.uproar == 0:
            attacker.uproar = random.randint(2, 5)
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} caused a uproar!")
        # Outrage
        if "Outrage" in move.get("flags"):
            if attacker.outraging == 0:
                attacker.outraging = random.randint(3, 4)
            attacker.outraging -= 1
            if attacker.outraging > 1:
                self.suspend.append([move, attacker])
            elif attacker.outraging == 1:
                if attacker.confused:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} is already confused!")
                elif attacker.ability == "Own Tempo":
                    # print pop up
                    pass
                else:
                    self.print_txt(f"{attacker.owner.name}'s {attacker.species} became confused due to fatigue!")
                    attacker.confused = True
                attacker.outraging = 0
        # Stat changes, HP drain
        if "Lowers Attacker chp by hp" in move.get("flags"):
            self.deal_dmg(attacker, (math.floor(attacker.hp * move.get("hp changes"))))
        if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
            if defender.ability == "Shield Dust" and "Changes Defender Stats" in move.get("flags"):
                pass
            elif defender.chp <= 0 and "Changes Defender Stats" in move.get("flags"):
                pass
            else:
                self.change_stats(attacker, defender, move)
        if "Leech" in move.get("flags"):
            if math.floor(dmg * 0.5) == 0:
                self.deal_dmg(attacker, -1)
            else:
                self.deal_dmg(attacker, -math.floor(dmg * 0.5))
        # Targets Rage
        if defender.rage and defender.damaged_this_turn:
            self.change_stats(attacker, defender, {"chance": 1, "flags": ["Changes Defender Stats"],
                                                   "stat changes": {"attack": 1}})
            self.print_txt(f"{defender.owner.name}'s {defender.species}'s rage is building!")
        # Grudge
        # Synchronize
        if defender.ability == "Synchronize" and attacker.status == "":
            self.give_status(defender, attacker, defender.status)
        # Contact
        if "Contact" in move.get("flags"):
            self.contact(attacker, defender, move)
        # Color Change
        # Shell Bell
        # If multi-hit moves go back to step 1
        if "Multi-Hit" in move.get("flags") and not self.recurse:
            self.recurse = True
            if attacker.chp > 0 and defender.chp > 0:
                if "Double-Hit" in move.get("flags"):
                    hits = 2
                else:
                    hits = (random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5], k=1))[0]
                s_hits = 1
                for hit in range(1, hits):
                    if (defender.chp <= 0 or attacker.chp <= 0 or defender.ability == "Effect Spore"
                            and attacker.status == "SLP"):
                        self.print_txt(f"It hit {s_hits} time(s)")
                        break
                    self.perform_move(attacker, defender, move)
                    s_hits += 1
                self.print_txt(f"It hit {s_hits} time(s)")
            else:
                self.print_txt(f"It hit 1 time")
            self.recurse = False
        elif "Multi-Hit" in move.get("flags"):
            return
        # Destiny Bond
        if defender.chp <= 0 and defender.bonded:
            self.deal_dmg(attacker, attacker.hp)
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} fainted!")
            self.faint(attacker)
        # Faint animation
        if defender.chp <= 0:
            self.print_txt(f"{defender.owner.name}'s {defender.species} fainted!")
            self.faint(defender)
        # Recoil Dmg, Rapid Spin
        if "Recoil" in move.get("flags"):
            if attacker.ability == "Rock Head" and "Explode" not in move.get("flags"):
                pass
            else:
                self.deal_dmg(attacker, (math.floor(dmg * move.get("amount"))))
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is hit with recoil!")
        # Knock off, Thief, Covet
        # Binding Moves
        if "Trapping" in move.get("flags") and defender.chp > 0 and attacker.chp > 0:
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
        # White herb Here
        if "Recharge" in move.get("flags") and attacker.chp > 0:
            attacker.recharge = True
        if attacker.chp <= 0:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} fainted!")
            self.faint(attacker)

    def dmg_calc(self, attacker, defender, move):
        if "Cant Crit" in move.get("flags") or defender.ability in ["Battle Armor", "Shell Armor"]:
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
            if attacker.ability == "Guts" and attacker.status != "":
                atk = math.floor(atk * 1.5)
            elif attacker.ability in ["Huge Power", "Pure Power"]:
                atk = math.floor(atk * 2)
            elif attacker.ability == "Hustle":
                atk = math.floor(atk * 1.5)
            if defender.ability == "Marvel Scale" and attacker.status != "":
                dfn = math.floor(dfn * 1.5)
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
        elif move_type == "Fire":
            if attacker.ability == "Blaze" and attacker.chp <= (attacker.hp * 0.33):
                move["power"] = math.floor(move.get("power") * 1.5)
            if attacker.water_sport or defender.water_sport:
                move["power"] = math.floor(move.get("power") / 2)
            if defender.ability == "Thick Fat":
                atk = math.floor(atk / 2)
        elif move_type == "Grass":
            if attacker.ability == "Overgrow" and attacker.chp <= (attacker.hp * 0.33):
                move["power"] = math.floor(move.get("power") * 1.5)
        elif move_type == "Water":
            if attacker.ability == "Torrent" and attacker.chp <= (attacker.hp * 0.33):
                move["power"] = math.floor(move.get("power") * 1.5)
        elif move_type == "Bug":
            if attacker.ability == "Swarm" and attacker.chp <= (attacker.hp * 0.33):
                move["power"] = math.floor(move.get("power") * 1.5)
        elif move_type == "Ice":
            if defender.ability == "Thick Fat":
                atk = math.floor(atk / 2)
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
            self.print_txt(f"Magnitude {mag[0]}!")
        else:
            total = math.floor(math.floor((math.floor((2 * attacker.level) / 5 + 2) 
                                           * atk * move.get("power")) / dfn) / 50)
        if attacker.status == "BRN" and dmg_type == "Physical" and attacker.ability != "Guts":
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
        if attacker.flash_fired and move_type == "Fire":
            total = math.floor(total * 1.5)
        total += 2
        if move.get("name") == "Spit Up":
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
        effectiveness = self.types.get(move_type).get(defender.type_one, 1)
        if defender.type_two is not None:
            effectiveness = effectiveness * self.types.get(move_type).get(defender.type_two, 1)
        if effectiveness >= 2 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            self.print_txt("It's super effective", 0)
        if effectiveness <= 0.5 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
            self.print_txt("It's not very effective...", 0)
        total = math.floor(total * effectiveness)
        dmg_range(total)
        print(attacker)
        print(attacker.temp_stats)
        print(defender)
        print(defender.temp_stats)
        print(f"Crit: {crit}")
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

    def change_stats(self, attacker, defender, move):
        if move == "Rage":
            defender.temp_stats["attack"] += 1
            if defender.temp_stats["attack"] > 6:
                defender.temp_stats["attack"] = 6
            return
        if defender.ability in ["Clear Body", "White Smoke"] and "Changes Defender Stats" in move.get("flags"):
            if move.get("chance") == 1:
                self.print_txt(f"{defender.owner.name} {defender.species}'s stats were not lowered!")
                # print popup
            return
        elif (defender.ability == "Keen Eye" and "accuracy" in move.get("stat changes")
              and "Changes Defender Stats" in move.get("flags")):
            if move.get("chance") == 1:
                self.print_txt(f"{defender.owner.name} {defender.species}'s stats were not lowered!")
                # print popup
            return
        elif (defender.ability == "Hype Cutter" and "attack" in move.get("stat changes")
              and "Changes Defender Stats" in move.get("flags")):
            if move.get("chance") == 1:
                self.print_txt(f"{defender.owner.name} {defender.species}'s stats were not lowered!")
                # print popup
            return
        rng = random.uniform(0, 1)
        if attacker.ability == "Serene Grace":
            move["chance"] = move.get("chance") * 2
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

    def give_status(self, attacker, defender, status, display=True):
        if status == "BRN":
            if defender.status != "":
                if defender.status == "BRN" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already burned!")
                elif display:
                    self.print_txt("It has no effect!")
            elif defender.type_one != "Fire" and defender.type_two != "Fire" and defender.ability != "Water Veil":
                defender.status = "BRN"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was burned!")
            elif display:
                if defender.ability == "Water Veil":
                    pass
                # print pop up
                self.print_txt("It has no effect!")
        elif status == "FRZ":
            if defender.status != "":
                if defender.status == "FRZ" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already frozen!")
                elif display:
                    self.print_txt("It has no effect!")
            elif defender.type_one != "Ice" and defender.type_two != "Ice" and defender.ability != "Magma Armor":
                defender.status = "FRZ"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was frozen!")
            elif display:
                if defender.ability == "Magma Armor":
                    pass
                # print pop up
                self.print_txt("It has no effect!")
        elif status == "PAR":
            if defender.status != "":
                if defender.status == "PAR" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already paralyzed!")
                elif display:
                    self.print_txt("It has no effect!")
            elif defender.ability != "Limber":
                defender.status = "PAR"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was paralyzed!")
            elif defender.ability == "Limber" and display:
                # print pop up
                self.print_txt("It has no effect!")
        elif status == "PSN":
            if defender.status != "":
                if defender.status == "PSN" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif defender.status == "TOX" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif display:
                    self.print_txt("It has no effect!")
            elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                  defender.type_one != "Steel" and defender.type_two != "Steel" and defender.ability != "Immunity"):
                defender.status = "PSN"
                self.print_txt(f"{defender.owner.name}'s {defender.species} was poisoned!")
            elif display:
                if defender.ability == "Immunity":
                    pass
                # print pop up
                self.print_txt("It has no effect!")
        elif status == "TOX":
            if defender.status != "":
                if defender.status == "PSN" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif defender.status == "TOX" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already poisoned!")
                elif display:
                    self.print_txt("It has no effect!")
            elif (defender.type_one != "Poison" and defender.type_two != "Poison" and
                  defender.type_one != "Steel" and defender.type_two != "Steel" and defender.ability != "Immunity"):
                defender.status = "TOX"
                defender.tox_turns = 0
                self.print_txt(f"{defender.owner.name}'s {defender.species} was badly poisoned!")
            elif display:
                if defender.ability == "Immunity":
                    pass
                # print pop up
                self.print_txt("It has no effect!")
        elif status == "SLP":
            if defender.status != "":
                if defender.status == "SLP" and display:
                    self.print_txt(f"{defender.owner.name}'s {defender.species} is already asleep!")
                elif display:
                    self.print_txt("It has no effect!")
            elif (defender.ability != "Soundproof" and attacker.uproar != 0 or defender.ability != "Soundproof"
                  and defender.uproar != 0):
                self.print_txt(f"{defender.owner.name}'s {defender.species} cannot fall asleep due to the uproar!")
            elif defender.ability not in ["Insomnia", "Vital Spirit"]:
                defender.status = "SLP"
                self.print_txt(f"{defender.owner.name}'s {defender.species} is fast asleep!")
            elif defender.ability in ["Insomnia", "Vital Spirit"] and display:
                # print pop up
                self.print_txt("It has no effect!")

    def contact(self, attacker, defender, move):
        if defender.ability == "Cute Charm":
            # print pop up
            # add infatuate
            pass
        elif defender.ability == "Rough Skin":
            # print pop up
            self.deal_dmg(attacker, math.floor(attacker.hp / 16))
        if attacker.status == "":
            if defender.ability == "Effect Spore":
                if random.uniform(0, 1) <= 0.1:
                    # print pop up
                    status = random.choice(["SLP", "PSN", "PAR"])
                    if status == "SLP":
                        self.give_status(defender, attacker, "SLP")
                    elif status == "PSN":
                        self.give_status(defender, attacker, "PSN")
                    elif status == "PAR":
                        self.give_status(defender, attacker, "PAR")
            if random.uniform(0, 1) <= 0.33:
                # print pop up
                if defender.ability == "Flame Body":
                    self.give_status(defender, attacker, "BRN")
                if defender.ability == "Poison Point":
                    self.give_status(defender, attacker, "PSN")
                if defender.ability == "Static":
                    self.give_status(defender, attacker, "PAR")

# End of Turn Functions
    def end_of_turn_effects(self):
        try:
            if self.player.active.speed > self.ai.active.speed:
                order = [self.player, self.ai]
                order_m = [self.player.active, self.ai.active]
            else:
                order = [self.ai, self.player]
                order_m = [self.ai.active, self.player.active]
        except AttributeError:
            if self.player.active is not None:
                order = [self.player, self.ai]
                order_m = [self.player.active]
            elif self.ai.active is not None:
                order = [self.ai, self.player]
                order_m = [self.ai.active]
            else:
                order = [self.ai, self.player]
                order_m = []
        # weather turns
        if self.weather != "clear":
            if self.weather == "hail":
                for mon in order_m:
                    if mon.type_one != "Ice" and mon.type_two != "Ice":
                        self.print_txt(f"{mon.owner.name}'s {mon.species} is stricken by Hail!", 1)
                        self.deal_dmg(mon, math.floor(mon.hp / 16))
                    if mon.chp <= 0:
                        order_m.remove(mon)
            elif self.weather == "sand":
                for mon in order_m:
                    immune_type = ["Rock", "Steel", "Ground"]
                    if (mon.type_one not in immune_type and mon.type_two not in immune_type
                            and mon.ability != "Sand Veil"):
                        self.print_txt(f"{mon.owner.name}'s {mon.species} is buffeted by the sandstorm!", 1)
                        self.deal_dmg(mon, math.floor(mon.hp / 16))
                    if mon.chp <= 0:
                        order_m.remove(mon)
            elif self.weather == "rain":
                for mon in order_m:
                    if mon.ability == "Rain Dish":
                        # print pop up
                        self.deal_dmg(mon, -math.floor(mon.hp / 16))
        # future moves
        # wish
        for mon in order_m:
            if mon.uproar != 0:
                for m in order_m:
                    if m.status == "SLP" and m.ability != "Soundproof":
                        m.status = ""
                        self.print_txt(f"{m.owner.name}'s {m.species} woke up!")
            if mon.status != "" and mon.ability == "Shed Skin":
                if random.randint(1, 3) == 1:
                    # print pop up
                    mon.status = ""
            # leftovers
        for mon in order_m:
            if mon.rooted:
                self.print_txt(f"{mon.owner.name}'s {mon.species} absorbed some nutrients!", 1)
                self.deal_dmg(mon, -math.floor(mon.hp / 16))
        # leech seed
        for mon in order_m:
            if mon.status == "PSN":
                self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by poison!", 1)
                self.deal_dmg(mon, math.floor(mon.hp / 8))
            elif mon.status == "TOX":
                self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by poison!", 1)
                mon.tox_turns += 1
                self.deal_dmg(mon, math.floor(mon.hp * (mon.tox_turns / 16)))
            elif mon.status == "BRN":
                self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by it's burn!", 1)
                self.deal_dmg(mon, math.floor(mon.hp / 8))
            if mon.chp <= 0:
                order_m.remove(mon)
        # nightmare
        for mon in order_m:
            if mon.cursed:
                self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by the curse")
                self.deal_dmg(mon, math.floor(mon.hp / 4))
            if mon.chp <= 0:
                order_m.remove(mon)
        for mon in order_m:
            if mon.trapping[0] != 0:
                if mon.owner.opponent.active is not None:
                    self.print_txt(f"{mon.owner.opponent.name}'s {mon.owner.opponent.active.species} "
                                   f"was hurt by {mon.trapping[1]}!")
                    self.deal_dmg(mon.owner.opponent.active, math.floor(mon.owner.opponent.active.hp / 16))
                    mon.trapping[0] -= 1
                    for m in order_m:
                        if m.chp <= 0:
                            order_m.remove(m)
                else:
                    mon.trapping[0] = 0
        # taunt fade
        # encore fade
        # disable fade
        # yawn
        # perish count
        for trainer in order:
            if trainer.reflect > 0:
                trainer.reflect -= 1
        for trainer in order:
            if trainer.light_screen > 0:
                trainer.light_screen -= 1
        # safeguard
        for trainer in order:
            if trainer.mist > 0:
                trainer.mist -= 1
        for mon in order_m:
            if mon.uproar > 0:
                mon.uproar -= 1
                if mon.uproar == 0:
                    self.print_txt(f"{mon.owner.name}'s {mon.species} calmed down.")
            if mon.ability == "Speed Boost":
                if mon.first_turn and not mon.acted:
                    pass
                else:
                    # print pop up
                    self.change_stats(mon, mon, {"chance": 1, "flags": ["Changes Attacker Stats"],
                                                 "stat changes": {"speed": 1}})
        self.clean_up(order_m)
        self.alive_check()

    @staticmethod
    def clean_up(order):
        for mon in order:
            mon.first_turn = False
            mon.acted = False
            mon.damaged_this_turn = False
            mon.dmg_last_type_taken = None
            mon.dmg_last_taken = 0
            mon.reflecting = False
            if mon.fury_cutter != 0 and not mon.fury_cutter_hit:
                mon.fury_cutter = 0
            elif mon.fury_cutter_hit:
                mon.fury_cutter_hit = False
            if mon.rolling != 0 and not mon.rolling_hit:
                mon.rolling = 0
            elif mon.rolling_hit:
                mon.rolling_hit = False
            if not mon.protecting and not mon.enduring:
                mon.protecting_chance = 1
            elif mon.protecting:
                mon.protecting_chance = mon.protecting_chance / 2
                mon.protecting = False
            elif mon.enduring:
                mon.protecting_chance = mon.protecting_chance / 2
                mon.enduring = False

    def alive_check(self):
        swapped = False
        if self.ai.active is None or self.ai.active.chp <= 0:
            if self.ai.active is not None:
                self.ai.team.remove(self.ai.active)
                self.print_txt(f"{self.ai.name}'s {self.ai.active.species} fainted!")
                self.ai.active = None
            if not self.ai.team:
                self.print_txt(f"{self.player.name} Wins!")
                for mon in self.player.team:
                    mon.reset_temp()
                self.finished = True
                return True
            self.ai.active = random.choice(self.ai.team)
            swapped = True
        if self.player.active is None or self.player.active.chp <= 0:
            if self.player.active is not None:
                self.player.team.remove(self.player.active)
                self.print_txt(f"{self.player.name}'s {self.player.active.species} fainted!")
                self.player.active = None
            if not self.player.team:
                self.print_txt(f"{self.ai.name} Wins!")
                self.finished = True
                return True
            self.on_switch_in(self.player_swap(True))
        if swapped:
            self.poke_ball_animation(self.ai)
            self.print_txt(f"{self.ai.name} sent out {self.ai.active.species}")

# Non Damaging Attacks
    @staticmethod
    def aromatherapy(attacker):
        for poke in attacker.owner.team:
            if poke.ability != "Soundproof":
                poke.status = ""

    def baton_pass(self, attacker):
        passer_temp_stats = attacker.temp_stats
        passer_confused = attacker.confused
        passer_getting_pumped = attacker.getting_pumped
        passer_blocking = attacker.blocking
        # passer_seeded = attacker.seeded
        passer_cursed = attacker.cursed
        # passer_substitute  = attacker.substitute
        passer_rooted = attacker.rooted
        # passer_perish  = attacker.perish
        if attacker == self.player.active and len(self.player.team) > 1:
            self.on_switch_in(self.player_swap(True))
            self.player.active.temp_stats = passer_temp_stats
            self.player.active.confused = passer_confused
            self.player.active.getting_pumped = passer_getting_pumped
            self.player.active.blocking = passer_blocking
            # self.player.active.seeded = passer_seeded
            self.player.active.cursed = passer_cursed
            # self.player.active.substitute  = passer_substitute
            self.player.active.rooted = passer_rooted
            # self.player.active.perish  = passer_perish
        elif attacker == self.ai.active and len(self.ai.active) > 1:
            self.ai.active = random.choice(self.ai.team)
            self.poke_ball_animation(self.ai)
            self.print_txt(f"{self.ai.name} sent out {self.ai.active.species}")
            self.ai.active.temp_stats = passer_temp_stats
            self.ai.active.confused = passer_confused
            self.ai.active.getting_pumped = passer_getting_pumped
            self.ai.active.blocking = passer_blocking
            # self.ai.active.seeded = passer_seeded
            self.ai.active.cursed = passer_cursed
            # self.ai.active.substitute  = passer_substitute
            self.ai.active.rooted = passer_rooted
            # self.ai.active.perish  = passer_perish
        else:
            self.print_txt("But it failed")

    def block(self, attacker):
        attacker.blocking = True

    def camouflage(self, attacker, defender):
        t = []
        for x, y in self.types.get(defender.type_one).items():
            if y < 1:
                t.append(x)
        attacker.type_one = random.choice(t)
        attacker.type_two = None
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")

    def conversion(self, attacker):
        t = []
        for attack in attacker.moves:
            if moves[attack].get("type") not in [attacker.type_one, attacker.type_two]:
                t.append(moves[attack].get("type"))
        if t:
            attacker.type_one = random.choice(t)
            attacker.type_two = None
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")
        else:
            self.print_txt("But it failed")

    # def conversion_2(self, attacker, defender):
    #    t = []
    #    for x, y in self.types.get(defender.type_one).items():
    #        if y < 1:
    #            t.append(x)
    #    attacker.type_one = random.choice(t)
    #    attacker.type_two = None
    #    self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")

    @staticmethod
    def charge(attacker):
        attacker.charge = True

    def curse(self, attacker, defender):
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

    @staticmethod
    def destiny_bond(attacker):
        attacker.bonded = True

    def detect(self, attacker, defender):
        attacker.protecting = True
        self.print_txt(f"{attacker.species} is protecting it's self")

    def endure(self, attacker, defender):
        attacker.enduring = True
        self.print_txt(f"{attacker.species} braced it's self!")

    @staticmethod
    def focus_energy(attacker):
        attacker.getting_pumped = True

    def haze(self, attacker, defender):
        attacker.temp_stats = attacker.temp_stats.fromkeys(attacker.temp_stats.keys(), 0)
        defender.temp_stats = defender.temp_stats.fromkeys(defender.temp_stats.keys(), 0)
        self.print_txt("All stat changes were eliminated!")

    @staticmethod
    def heal_bell(attacker):
        for poke in attacker.owner.team:
            if poke.ability != "Soundproof":
                poke.status = ""

    def ingrain(self, attacker):
        attacker.rooted = True
        self.print_txt(f"{attacker.owner.name} {attacker.species} planted it's roots!")

    def light_screen(self, attacker):
        if attacker.owner.light_screen > 0:
            self.print_txt("But it failed")
        else:
            attacker.owner.light_screen = 5

    def magic_coat(self, attacker, defender):
        if defender.acted:
            self.print_txt("But it failed")
        else:
            attacker.reflecting = True
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} shrouded it's self in magic coat!")

    def memento(self, attacker, defender):
        if defender.temp_stats.get("attack") == 6 and defender.temp_stats.get("sp_attack") == 6:
            self.print_txt("But it failed")
        else:
            self.deal_dmg(attacker, attacker.chp)
            self.change_stats(attacker, defender, {"chance": 1, "flags": ["Changes Defender Stats"],
                                                   "stat changes": {"attack": -2, "sp_attack": -2}})

    @staticmethod
    def minimize(attacker):
        attacker.minimized = True

    def mist(self, attacker):
        if attacker.owner.mist > 0:
            self.print_txt("But it failed")
        else:
            attacker.owner.mist = 5

    def mud_sport(self, attacker):
        attacker.mud_sport = True
        self.print_txt("Electricity's power was weakened")

    def protect(self, attacker, defender):
        attacker.protecting = True
        self.print_txt(f"{attacker.species} is protecting it's self")

    def psych_up(self, attacker, defender):
        attacker.temp_stats.update(defender.temp_stats)
        print(attacker.temp_stats)
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} copied it's opponents stat changes")

    def reflect(self, attacker):
        if attacker.owner.reflect > 0:
            self.print_txt("But it failed")
        else:
            attacker.owner.reflect = 5

    def refresh(self, attacker):
        if attacker.status == "SLP" or attacker.status == "FRZ" or attacker.status == "":
            self.print_txt("But it failed")
        else:
            attacker.status = ""
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} status returned to normal!")

    def stockpile(self, attacker):
        if attacker.stockpile >= 3:
            self.print_txt("But it failed")
            return
        else:
            attacker.stockpile += 1
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} stockpiled {attacker.stockpile}!")

    def water_sport(self, attacker):
        attacker.water_sport = True
        self.print_txt("Fire's power was weakened")

# Damaging Attacks

    def triple_kick(self, attacker, defender, move):
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
            self.contact(attacker, defender, move)
            if (defender.chp <= 0 or attacker.chp <= 0 or
                    defender.ability == "Effect Spore" and attacker.status == "SLP"):
                self.print_txt(f"It hit {hit + 1} time(s)")
                break
        if defender.bide != 0:
            defender.bide_dmg += dmg
        defender.damaged_this_turn = True
        if defender.chp > 0 and attacker.chp > 0:
            self.print_txt(f"It hit {hits} time(s)")
        self.print_txt(f"It hit {hits} time(s)")

    def beat_up(self, attacker, defender, move):
        for mon in attacker.owner.team:
            if mon.status == "":
                self.print_txt(f"{mon.species}'s attack!")
                if defender.ability in ["Battle Armor", "Shell Armor"]:
                    crit = False
                else:
                    crit = self.crit_check(mon, move)
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
                if defender.chp <= 0 or attacker.chp <= 0:
                    break
        defender.damaged_this_turn = True

    def bide(self, attacker, defender, move):
        if attacker.bide == 0:
            attacker.bide = 1
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
            dmg = 0
        elif attacker.bide == 1:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is storing energy")
            attacker.bide = 2
            dmg = 0
        else:
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} unleashed energy")
            attacker.bide = 0
            dmg = attacker.bide_dmg * 2
            attacker.bide_dmg = 0
        return dmg

    @staticmethod
    def counter(attacker, defender, move):
        return attacker.dmg_last_taken * 2

    @staticmethod
    def mirror_coat(attacker, defender, move):
        return attacker.dmg_last_taken * 2

    @staticmethod
    def psywave(attacker, defender, move):
        ran = random.randint(0, 10)
        dmg = math.floor((attacker.level * (10 * ran + 50)) / 100)
        if dmg == 0:
            dmg = 1
        return dmg

    @staticmethod
    def super_fang(attacker, defender, move):
        dmg = math.floor(defender.chp * 0.5)
        if dmg == 0:
            dmg = 1
        return dmg

    @staticmethod
    def endeavor(attacker, defender, move):
        return defender.chp - attacker.chp

    def present(self, attacker, defender, move):
        power = random.choices([0, 40, 80, 120], [20, 40, 30, 10], k=1)[0]
        if power > 0:
            move["power"] = power
            dmg = self.dmg_calc(attacker, defender, move)
            return dmg
        else:
            if defender.chp == defender.hp:
                self.print_txt("It had no effect!")
                return 0
            else:
                return -math.floor(defender.hp / 4)

    def fury_cutter(self, attacker, defender, move):
        if attacker.fury_cutter <= 3:
            move["power"] = 10 * 2 ** attacker.fury_cutter
        else:
            move["power"] = 160
        attacker.fury_cutter += 1
        attacker.fury_cutter_hit = True
        return self.dmg_calc(attacker, defender, move)

    def rollout(self, attacker, defender, move):
        move["power"] = 30 * 2 ** attacker.rolling
        if attacker.rolling < 4:
            attacker.rolling += 1
            attacker.rolling_hit = True
            self.suspend.append([move, attacker])
        else:
            attacker.rolling = 0
        return self.dmg_calc(attacker, defender, move)

    def ice_ball(self, attacker, defender, move):
        move["power"] = 30 * 2 ** attacker.rolling
        if attacker.rolling < 4:
            attacker.rolling += 1
            attacker.rolling_hit = True
            self.suspend.append([move, attacker])
        else:
            attacker.rolling = 0
        return self.dmg_calc(attacker, defender, move)
