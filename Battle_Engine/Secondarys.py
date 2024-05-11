from math import floor
from random import uniform, choice


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
    rng = uniform(0, 1)
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


def contact(self, attacker, defender):
    if defender.ability == "Cute Charm":
        # print pop up
        # add infatuate
        pass
    elif defender.ability == "Rough Skin":
        # print pop up
        self.deal_dmg(attacker, floor(attacker.hp / 16))
    if attacker.status == "":
        if defender.ability == "Effect Spore":
            if uniform(0, 1) <= 0.1:
                # print pop up
                status = choice(["SLP", "PSN", "PAR"])
                if status == "SLP":
                    self.give_status(defender, attacker, "SLP")
                elif status == "PSN":
                    self.give_status(defender, attacker, "PSN")
                elif status == "PAR":
                    self.give_status(defender, attacker, "PAR")
        if uniform(0, 1) <= 0.33:
            # print pop up
            if defender.ability == "Flame Body":
                self.give_status(defender, attacker, "BRN")
            if defender.ability == "Poison Point":
                self.give_status(defender, attacker, "PSN")
            if defender.ability == "Static":
                self.give_status(defender, attacker, "PAR")
