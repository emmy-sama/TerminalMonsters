from math import floor
from random import randint, choice, uniform

from Battle_Engine.Status_Checks import grounded
from Data_Builders import moves


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
            move = choice(valid_moves)
        else:
            if attacker.sleep_turns == 0:
                attacker.sleep_turns = randint(1, 5)
                if attacker.ability == "Early Bird":
                    attacker.sleep_turns = floor(attacker.sleep_turns / 2)
            else:
                attacker.sleep_turns -= 1
            if attacker.sleep_turns == 0 or defender.ability != "Soundproof" and defender.uproar != 0:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} woke up!")
                attacker.status = ""
            else:
                self.print_txt(f"{attacker.owner.name}'s {attacker.species} is fast asleep!")
                return "Failed No Text"
    if attacker.status == "FRZ" and "Thaws" not in move.get("flags"):
        if randint(1, 100) <= 20:
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
        if randint(1, 100) <= 25:
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
            move = choice(list(self.moves.values()))
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
            move = choice(choices)
    # set typing for hidden power, weather ball
    # subtract pp (if called subtract from og move)
    # move failure conditions pt1
    # fake out defender all ready acted
    if move.get("name") == "Fake Out":
        if attacker.first_turn is False:
            return "Failed"
        # protection move fail if no other moved queue, or rng fail
    elif move.get("name") == "Protect" or move.get("name") == "Detect" or move.get("name") == "Endure":
        if attacker.protecting_chance < uniform(0, 1) or defender.acted:
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
        if attacker.chp <= floor(attacker.hp * 0.25):
            return "Failed"
    elif move.get("name") == "Belly Drum":
        if attacker.chp <= floor(attacker.hp * 0.50):
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
            self.deal_dmg(defender, -floor(defender.hp / 4))
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
            self.deal_dmg(defender, -floor(defender.hp / 4))
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
        hit_check = randint(1, 100)
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
        hit_check = randint(1, 100)
        accuracy = floor(30 + (attacker.level - defender.level))
        if hit_check >= accuracy:
            self.print_txt(f"{attacker.species} Missed!")
            return "Failed No Text"
    elif move.get("accuracy") != 0:
        hit_check = randint(1, 100)
        accuracy_stage = attacker.temp_stats.get("accuracy") + defender.temp_stats.get("evasion")
        if accuracy_stage > 6:
            accuracy_stage = 6
        elif accuracy_stage < -6:
            accuracy_stage = -6
        accuracy = move.get("accuracy") * self.temp_stat_table_acc_eva.get(accuracy_stage)
        if self.weather == "sand" and defender.ability == "Sand Veil":
            accuracy = floor(accuracy * 0.8)
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
