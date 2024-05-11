from math import floor
from random import randint, choice


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
                    self.deal_dmg(mon, floor(mon.hp / 16))
                if mon.chp <= 0:
                    order_m.remove(mon)
        elif self.weather == "sand":
            for mon in order_m:
                immune_type = ["Rock", "Steel", "Ground"]
                if (mon.type_one not in immune_type and mon.type_two not in immune_type
                        and mon.ability != "Sand Veil"):
                    self.print_txt(f"{mon.owner.name}'s {mon.species} is buffeted by the sandstorm!", 1)
                    self.deal_dmg(mon, floor(mon.hp / 16))
                if mon.chp <= 0:
                    order_m.remove(mon)
        elif self.weather == "rain":
            for mon in order_m:
                if mon.ability == "Rain Dish":
                    # print pop up
                    self.deal_dmg(mon, -floor(mon.hp / 16))
    # future moves
    # wish
    for mon in order_m:
        if mon.uproar != 0:
            for m in order_m:
                if m.status == "SLP" and m.ability != "Soundproof":
                    m.status = ""
                    self.print_txt(f"{m.owner.name}'s {m.species} woke up!")
        if mon.status != "" and mon.ability == "Shed Skin":
            if randint(1, 3) == 1:
                # print pop up
                mon.status = ""
        # leftovers
    for mon in order_m:
        if mon.rooted:
            self.print_txt(f"{mon.owner.name}'s {mon.species} absorbed some nutrients!", 1)
            self.deal_dmg(mon, -floor(mon.hp / 16))
    # leech seed
    for mon in order_m:
        if mon.status == "PSN":
            self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by poison!", 1)
            self.deal_dmg(mon, floor(mon.hp / 8))
        elif mon.status == "TOX":
            self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by poison!", 1)
            mon.tox_turns += 1
            self.deal_dmg(mon, floor(mon.hp * (mon.tox_turns / 16)))
        elif mon.status == "BRN":
            self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by it's burn!", 1)
            self.deal_dmg(mon, floor(mon.hp / 8))
        if mon.chp <= 0:
            order_m.remove(mon)
    # nightmare
    for mon in order_m:
        if mon.cursed:
            self.print_txt(f"{mon.owner.name}'s {mon.species} was hurt by the curse")
            self.deal_dmg(mon, floor(mon.hp / 4))
        if mon.chp <= 0:
            order_m.remove(mon)
    for mon in order_m:
        if mon.trapping[0] != 0:
            if mon.owner.opponent.active is not None:
                self.print_txt(f"{mon.owner.opponent.name}'s {mon.owner.opponent.active.species} "
                               f"was hurt by {mon.trapping[1]}!")
                self.deal_dmg(mon.owner.opponent.active, floor(mon.owner.opponent.active.hp / 16))
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
    clean_up(order_m)
    alive_check(self)


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
        self.ai.active = choice(self.ai.team)
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
        