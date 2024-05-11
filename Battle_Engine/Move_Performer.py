from inspect import signature
from math import floor
from random import uniform, randint, choices


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
            self.deal_dmg(attacker, -floor(attacker.hp * hp_change[attacker.stockpile - 1]))
            attacker.stockpile = 0
        else:
            self.deal_dmg(attacker, -floor(attacker.hp * move.get("hp changes")))
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
            self.deal_dmg(attacker, -floor(attacker.hp / 2))
        elif self.weather == "sun":
            self.deal_dmg(attacker, -floor(attacker.hp * 0.66))
        else:
            self.deal_dmg(attacker, -floor(attacker.hp / 4))
    elif move.get("category") == "Non-Damaging":
        s = move.get("name").lower()
        s = s.replace(" ", "_")
        a = getattr(self, s, None)
        if a:
            sig = str(signature(a))
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
                sig = str(signature(a))
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
            roll = uniform(0, 1)
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
                    if uniform(0, 1) <= 0.1:
                        defender.flinching = True
                elif uniform(0, 1) <= move.get("chance"):
                    defender.flinching = True
        elif "Confuses" in move.get("flags") and defender.ability != "Own Tempo" and not defender.confused:
            if attacker.ability == "Serene Grace":
                move["chance"] = move.get("chance") * 2
            if uniform(0, 1) <= move.get("chance"):
                self.print_txt(f"{defender.owner.name}'s {defender.species} became confused!")
                defender.confused = True
        elif "Status" in move.get("flags") and defender.status == "":
            if attacker.ability == "Serene Grace":
                move["chance"] = move.get("chance") * 2
            if uniform(0, 1) <= move.get("chance"):
                self.give_status(attacker, defender, move.get("status"), False)
    # Uproar
    if move.get("name") == "Uproar" and attacker.uproar == 0:
        attacker.uproar = randint(2, 5)
        self.print_txt(f"{attacker.owner.name}'s {attacker.species} caused a uproar!")
    # Outrage
    if "Outrage" in move.get("flags"):
        if attacker.outraging == 0:
            attacker.outraging = randint(3, 4)
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
        self.deal_dmg(attacker, (floor(attacker.hp * move.get("hp changes"))))
    if "Changes Attacker Stats" in move.get("flags") or "Changes Defender Stats" in move.get("flags"):
        if defender.ability == "Shield Dust" and "Changes Defender Stats" in move.get("flags"):
            pass
        elif defender.chp <= 0 and "Changes Defender Stats" in move.get("flags"):
            pass
        else:
            self.change_stats(attacker, defender, move)
    if "Leech" in move.get("flags"):
        if floor(dmg * 0.5) == 0:
            self.deal_dmg(attacker, -1)
        else:
            self.deal_dmg(attacker, -floor(dmg * 0.5))
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
                hits = (choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5], k=1))[0]
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
            self.deal_dmg(attacker, (floor(dmg * move.get("amount"))))
            self.print_txt(f"{attacker.owner.name}'s {attacker.species} is hit with recoil!")
    # Knock off, Thief, Covet
    # Binding Moves
    if "Trapping" in move.get("flags") and defender.chp > 0 and attacker.chp > 0:
        attacker.trapping[0] = randint(2, 5)
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
