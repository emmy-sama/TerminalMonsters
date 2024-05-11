from math import floor
from random import randint, choice, choices
from Data_Builders import moves


# Non Damaging Attacks
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
        self.ai.active = choice(self.ai.team)
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
    attacker.type_one = choice(t)
    attacker.type_two = None
    self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")


def conversion(self, attacker):
    t = []
    for attack in attacker.moves:
        if moves[attack].get("type") not in [attacker.type_one, attacker.type_two]:
            t.append(moves[attack].get("type"))
    if t:
        attacker.type_one = choice(t)
        attacker.type_two = None
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")
    else:
        self.print_txt("But it failed")


# def conversion_2(self, attacker, defender):
#    t = []
#    for x, y in self.types.get(defender.type_one).items():
#        if y < 1:
#            t.append(x)
#    attacker.type_one = choice(t)
#    attacker.type_two = None
#    self.print_txt(f"{attacker.owner.name}'s {attacker.species} became {attacker.type_one.lower()} type")


def charge(attacker):
    attacker.charge = True


def curse(self, attacker, defender):
    if attacker.type_one == "Ghost" or attacker.type_two == "Ghost":
        self.deal_dmg(attacker, (floor(attacker.hp / 2)))
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


def destiny_bond(attacker):
    attacker.bonded = True


def detect(self, attacker, defender):
    attacker.protecting = True
    self.print_txt(f"{attacker.species} is protecting it's self")


def endure(self, attacker, defender):
    attacker.enduring = True
    self.print_txt(f"{attacker.species} braced it's self!")


def focus_energy(attacker):
    attacker.getting_pumped = True


def haze(self, attacker, defender):
    attacker.temp_stats = attacker.temp_stats.fromkeys(attacker.temp_stats.keys(), 0)
    defender.temp_stats = defender.temp_stats.fromkeys(defender.temp_stats.keys(), 0)
    self.print_txt("All stat changes were eliminated!")


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
            hit_check = randint(1, 100)
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
            dmg = floor(floor((floor((2 * mon.level) / 5 + 2)
                                        * mon.attack * 10) / defender.defense) / 50)
            if mon.status == "BRN":
                dmg = floor(dmg * 0.5)
            if defender.owner.reflect and not crit:
                dmg = floor(dmg * 0.5)
            dmg += 2
            if crit:
                dmg = floor(dmg * 2)
            dmg = floor((dmg * randint(85, 100)) / 100)
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


def counter(attacker, defender, move):
    return attacker.dmg_last_taken * 2


def mirror_coat(attacker, defender, move):
    return attacker.dmg_last_taken * 2


def psywave(attacker, defender, move):
    ran = randint(0, 10)
    dmg = floor((attacker.level * (10 * ran + 50)) / 100)
    if dmg == 0:
        dmg = 1
    return dmg


def super_fang(attacker, defender, move):
    dmg = floor(defender.chp * 0.5)
    if dmg == 0:
        dmg = 1
    return dmg


def endeavor(attacker, defender, move):
    return defender.chp - attacker.chp


def present(self, attacker, defender, move):
    power = choices([0, 40, 80, 120], [20, 40, 30, 10], k=1)[0]
    if power > 0:
        move["power"] = power
        dmg = self.dmg_calc(attacker, defender, move)
        return dmg
    else:
        if defender.chp == defender.hp:
            self.print_txt("It had no effect!")
            return 0
        else:
            return -floor(defender.hp / 4)


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
