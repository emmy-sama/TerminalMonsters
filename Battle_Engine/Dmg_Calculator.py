from math import floor
from random import uniform, randint, choices

from Debug_Functions import dmg_range


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
            atk = floor(attacker.attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("attack")))
            dfn = floor(defender.defense * self.temp_stat_table_norm.get(defender.temp_stats.get("defense")))
        if "Explode" in move.get("flags"):
            dfn = floor(dfn * 0.5)
        if attacker.ability == "Guts" and attacker.status != "":
            atk = floor(atk * 1.5)
        elif attacker.ability in ["Huge Power", "Pure Power"]:
            atk = floor(atk * 2)
        elif attacker.ability == "Hustle":
            atk = floor(atk * 1.5)
        if defender.ability == "Marvel Scale" and attacker.status != "":
            dfn = floor(dfn * 1.5)
    else:
        if crit:
            atk = attacker.sp_attack
            dfn = defender.sp_defense
        else:
            atk = floor(attacker.sp_attack * self.temp_stat_table_norm.get(attacker.temp_stats.get("sp_attack")))
            dfn = floor(defender.sp_defense * self.temp_stat_table_norm.get(defender.temp_stats.get("sp_defense")))
    if move_type == "Electric":
        if attacker.mud_sport or defender.mud_sport:
            move["power"] = floor(move.get("power") / 2)
    elif move_type == "Fire":
        if attacker.ability == "Blaze" and attacker.chp <= (attacker.hp * 0.33):
            move["power"] = floor(move.get("power") * 1.5)
        if attacker.water_sport or defender.water_sport:
            move["power"] = floor(move.get("power") / 2)
        if defender.ability == "Thick Fat":
            atk = floor(atk / 2)
    elif move_type == "Grass":
        if attacker.ability == "Overgrow" and attacker.chp <= (attacker.hp * 0.33):
            move["power"] = floor(move.get("power") * 1.5)
    elif move_type == "Water":
        if attacker.ability == "Torrent" and attacker.chp <= (attacker.hp * 0.33):
            move["power"] = floor(move.get("power") * 1.5)
    elif move_type == "Bug":
        if attacker.ability == "Swarm" and attacker.chp <= (attacker.hp * 0.33):
            move["power"] = floor(move.get("power") * 1.5)
    elif move_type == "Ice":
        if defender.ability == "Thick Fat":
            atk = floor(atk / 2)
    if not move.get("name") != "Solar Beam" and self.weather != "sun" and self.weather != "clear":
        total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
    elif move.get("name") == "Eruption" or move.get("name") == "Water Spout":
        total = (
            floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * (150 * attacker.chp / attacker.hp)) / dfn) / 50))
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
        total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * power) / dfn) / 50)
    elif move.get("name") == "Low Kick":
        if defender.weight <= 9.9:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 20) / dfn) / 50)
        elif defender.weight <= 24.9:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 40) / dfn) / 50)
        elif defender.weight <= 49.9:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 60) / dfn) / 50)
        elif defender.weight <= 99.9:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 80) / dfn) / 50)
        elif defender.weight <= 199.9:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 100) / dfn) / 50)
        else:
            total = floor(floor((floor((2 * attacker.level) / 5 + 2) * atk * 120) / dfn) / 50)
    elif move.get("name") == "Magnitude":
        mag = choices([[4, 10], [5, 30], [6, 50], [7, 70], [8, 90], [9, 110], [10, 150]],
                      weights=[5, 10, 20, 30, 20, 10, 5], k=1)[0]
        total = floor(
            floor((floor((2 * attacker.level) / 5 + 2) * atk * mag[1]) / dfn) / 50)
        self.print_txt(f"Magnitude {mag[0]}!")
    else:
        total = floor(floor((floor((2 * attacker.level) / 5 + 2)
                                       * atk * move.get("power")) / dfn) / 50)
    if attacker.status == "BRN" and dmg_type == "Physical" and attacker.ability != "Guts":
        total = floor(total * 0.5)
    if defender.owner.reflect and dmg_type == "Physical" and not crit:
        total = floor(total * 0.5)
    if defender.owner.light_screen and dmg_type == "Special" and not crit:
        total = floor(total * 0.5)
    if self.weather != "clear" and move_type == "Fire" or move_type == "Water":
        if self.weather == "rain":
            if move_type == "Water":
                total = floor(total * 1.5)
            if move_type == "Fire":
                total = floor(total * 0.5)
        if self.weather == "sun":
            if move_type == "Fire":
                total = floor(total * 1.5)
            if move_type == "Water":
                total = floor(total * 0.5)
    if attacker.flash_fired and move_type == "Fire":
        total = floor(total * 1.5)
    total += 2
    if move.get("name") == "Spit Up":
        total = floor(total * attacker.stockpile)
        attacker.stockpile = 0
    if crit:
        total = floor(total * 2)
    if defender.semi_invulnerable is not None and "Double Damage" in move.get("flags"):
        total = floor(total * 2)
    if defender.minimized and "Double Minimized" in move.get("flags"):
        total = floor(total * 2)
    if move.get("name") == "Facade":
        if attacker.status == "BRN" or attacker.status == "PAR" or attacker.status == "PSN":
            total = floor(total * 2)
    if move.get("name") == "Smelling Salts" and defender.status == "PAR":
        total = floor(total * 2)
        defender.status = ""
    if move.get("name") == "Revenge" and attacker.damaged_this_turn:
        total = floor(total * 2)
    if move.get("name") == "Weather Ball" and self.weather != "clear":
        total = floor(total * 2)
    if attacker.charge and move_type == "Electric":
        total = floor(total * 2)
        attacker.charge = False
    if move_type == attacker.type_one or move_type == attacker.type_two:
        total = floor(total * 1.5)
    effectiveness = self.types.get(move_type).get(defender.type_one, 1)
    if defender.type_two is not None:
        effectiveness = effectiveness * self.types.get(move_type).get(defender.type_two, 1)
    if effectiveness >= 2 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
        self.print_txt("It's super effective", 0)
    if effectiveness <= 0.5 and move.get("name") != "Jump Kick" and move.get("name") != "High Jump Kick":
        self.print_txt("It's not very effective...", 0)
    total = floor(total * effectiveness)
    dmg_range(total)
    print(attacker)
    print(attacker.temp_stats)
    print(defender)
    print(defender.temp_stats)
    print(f"Crit: {crit}")
    if move.get("name") != "Spit Up":
        total = floor((total * randint(85, 100)) / 100)
    if total == 0:
        total = 1
    return total


def crit_check(self, attacker, move):
    crit_roll = uniform(0, 1)
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
