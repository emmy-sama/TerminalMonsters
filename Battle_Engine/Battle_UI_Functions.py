from math import floor
from time import sleep
from bearlibterminal import terminal
from Classes import Ai, Player


def print_ui(self, first_turn=False):
    terminal.layer(0)
    terminal.put(0, 0, 0xF8FF)
    terminal.layer(1)
    if self.player.active is not None and self.ai.active is not None and not first_turn:
        hp_bars(self)
    terminal.refresh()


def print_txt_battle(txt, delay=1.5):
    if len(txt) > 126:
        txt = txt[0:42] + "\n" + txt[42:84] + "\n" + txt[84:126] + "\n" + txt[126:]
    elif len(txt) > 84:
        txt = txt[0:42] + "\n" + txt[42:84] + "\n" + txt[84:]
    elif len(txt) > 42:
        txt = txt[0:42] + "\n" + txt[42:]
    terminal.clear_area(1, 20, 42, 4)
    terminal.printf(1, 20, txt)
    terminal.refresh()
    sleep(delay)


def poke_ball_animation(self, side):
    if isinstance(side, Player):
        path = [[0, 13], [2, 12], [4, 11], [6, 11], [8, 11], [10, 12], [12, 13], [14, 14], [16, 15], [18, 16],
                [20, 17], [22, 18]]
        for cord in path:
            terminal.clear_area(0, 11, 30, 8)
            terminal.put(cord[0], cord[1], 0xF8F4)
            terminal.refresh()
            sleep(0.1)
        terminal.clear_area(0, 11, 30, 8)
        terminal.put(22, 18, 0xF8F3)
        terminal.refresh()
        sleep(0.1)
        terminal.clear_area(0, 11, 30, 8)
        terminal.put(22, 18, 0xF8F2)
        terminal.refresh()
        sleep(0.2)
        terminal.clear_area(0, 11, 30, 8)
        hp_bars(self, ai=False)
        terminal.put(23, 14, int(side.active.back_sprite, 16))
    if isinstance(side, Ai):
        path = [[87, 4], [86, 3], [84, 2], [82, 2], [80, 2], [78, 3], [76, 4], [74, 5], [72, 6], [70, 7], [68, 8],
                [66, 9]]
        for cord in path:
            terminal.clear_area(68, 2, 30, 8)
            terminal.put(cord[0], cord[1], 0xF8F4)
            terminal.refresh()
            sleep(0.1)
        terminal.clear_area(66, 2, 30, 8)
        terminal.put(66, 9, 0xF8F3)
        terminal.refresh()
        sleep(0.1)
        terminal.clear_area(66, 2, 30, 8)
        terminal.put(66, 9, 0xF8F2)
        terminal.refresh()
        sleep(0.2)
        terminal.clear_area(66, 2, 30, 8)
        hp_bars(self, player=False)
        terminal.put(66, 5, int(side.active.front_sprite, 16))


def faint(mon):
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
                sleep(0.1)
                terminal.put(23, 14, int(self.player.active.back_sprite, 16))
                terminal.refresh()
                sleep(0.15)
        x = 61
        x2 = 78
        y = 17
        y2 = 18
    else:
        for blink in range(0, 4):
            if amount >= 0:
                terminal.clear_area(66, 5, 1, 1)
                terminal.refresh()
                sleep(0.1)
                terminal.put(66, 5, int(self.ai.active.front_sprite, 16))
                terminal.refresh()
                sleep(0.15)
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
            dmg = floor(temp_hp / abs(remaining_health_bars_post - remaining_health_bars_pre))
            if dmg == 0:
                dmg = 1
        else:
            dmg = floor(amount / abs(remaining_health_bars_post - remaining_health_bars_pre))
            if dmg == 0:
                dmg = 1
    else:
        if (amount + victim.hp) > victim.chp:
            dmg = floor(temp_hp - victim.hp / abs(remaining_health_bars_post - remaining_health_bars_pre))
            if dmg == 0:
                dmg = -1
        else:
            dmg = floor(amount / abs(remaining_health_bars_post - remaining_health_bars_pre))
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
            sleep(0.1)
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
            sleep(0.1)
    terminal.clear_area(x2, y2, 7, 1)
    terminal.printf(x2, y2, f"{victim.chp}/{victim.hp}")
    terminal.refresh()
