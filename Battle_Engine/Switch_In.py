from bearlibterminal import terminal

from Battle_Engine.Status_Checks import check_for_status_cure


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
