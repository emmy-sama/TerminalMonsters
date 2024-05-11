from random import randint
from bearlibterminal import terminal
# Battle Function Imports
from Battle_Engine.Battle_UI_Functions import print_ui, print_txt_battle, poke_ball_animation
from Battle_Engine.End_of_Turn import alive_check, end_of_turn_effects
from Battle_Engine.Move_Clearence import move_clearance
from Battle_Engine.Move_Performer import perform_move
from Battle_Engine.Player_Actions import player_turn
from Battle_Engine.Secondarys import change_stats
from Battle_Engine.Speed_Check import speed_check
from Battle_Engine.Status_Checks import check_for_status_cure, can_attack
from Battle_Engine.Switch_In import on_switch_in
from Classes import Pokemon
from Helpers.queue_custom import Queue
from Data_Builders import moves, types


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
        print_ui(self, True)
        self.finished = False
        self.recurse = False
        self.suspend = []
        self.turn_order = Queue()

    # Main Battle Function
    def main(self):
        # Handles bringing in lead pokemon
        # pokeball animation
        poke_ball_animation(self, self.player)
        print_txt_battle(f"{self.player.name} sent out {self.player.active.species}")
        terminal.clear_area(1, 20, 42, 4)
        poke_ball_animation(self, self.ai)
        print_txt_battle(f"{self.ai.name} sent out {self.ai.active.species}")
        # Abilities with entry effects can announce
        if self.player.active.speed < self.ai.active.speed:
            order = [self.player.active, self.ai.active]
        elif self.player.active.speed > self.ai.active.speed:
            order = [self.ai.active, self.player.active]
        else:
            if randint(0, 1) == 0:
                order = [self.ai.active, self.player.active]
            else:
                order = [self.player.active, self.ai.active]
        for mon_1 in order:
            mon_2 = mon_1.owner.opponent.active
            if mon_1.status != "" or mon_1.confused:
                check_for_status_cure(mon_1)
            elif mon_1.ability == "Drizzle":
                self.weather = "rain"
                print_txt_battle("It started to rain!")
                # print pop up
            elif mon_1.ability == "Drought":
                self.weather = "sun"
                print_txt_battle("The sun light got bright!")
                # print pop up
            elif mon_1.ability == "Sand Stream":
                self.weather = "sand"
                print_txt_battle("A sand storm brewed!")
                # print pop up
            elif mon_1.ability == "Intimidate":
                print_txt_battle(f"{mon_1.owner.name}'s {mon_1.species}'s Intimidate cuts {mon_2.species}'s attack!")
                # print pop up
                change_stats(self, mon_1, mon_2, {"chance": 1, "flags": ["Changes Defender Stats"],
                                                  "stat changes": {"attack": -1}})
        # Berries/Berry Juice/White Herb/Mental Herb can be consumed if applicable
        # Forecast and  abilities can announce themselves if applicable, and cause form changes

        while not self.finished:
            # BackUp Check
            if self.ai.active is None or self.player.active is None:
                alive_check(self)
            # Refreshes Ui
            print_ui(self)
            # AI action select
            if can_attack(self, self.ai.active):
                if self.ai.active.recharge:
                    self.ai.active.recharge = False
                    self.ai.active.loafing = False
                    print_txt_battle(f"{self.ai.name}'s {self.ai.active.species} must recharge!")
                else:
                    self.turn_order.put([1, self.ai.active.speed, moves.get(self.ai.ai_select_move()).copy(), self.ai])
            # Player action select
            if can_attack(self, self.player.active):
                if self.player.active.recharge:
                    self.player.active.recharge = False
                    self.player.active.loafing = False
                    print_txt_battle(f"{self.player.name}'s {self.player.active.species} must recharge!")
                else:
                    a = player_turn(self, self.player)
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
                on_switch_in(self, x)
                # pokeball animation
                # entry hazards
                # Abilities with entry effects can announce
                # Berries/Berry Juice/White Herb/Mental Herb can be consumed if applicable
                # Forecast and  abilities can announce themselves if applicable, and cause form changes
            # Focus Punch message
            for item in self.turn_order.focus_punch():
                print_txt_battle(f"{item.name}'s {item.active.species} is tightening its focus!")
            # Calculates Speeds
            if self.turn_order.len() > 1:
                order = speed_check(self, self.turn_order.move_dequeue(), self.turn_order.move_dequeue())
                for item in order:
                    self.turn_order.append(item)
            # Checks if a move is successful then performs it
            while self.turn_order.peek() is not None:
                x = self.turn_order.move_dequeue()
                if x[3].active is not None and x[3].active.chp > 0:
                    try:
                        result = move_clearance(self, x[3].active, x[3].opponent.active, x[2])
                        if result == "Failed":
                            print_txt_battle("But it failed")
                        elif result == "Failed No Text":
                            pass
                        elif result == "Suspend":
                            self.suspend.append([x[2], x[3].active])
                        elif result == "Passed":
                            perform_move(self, x[3].active, x[3].opponent.active, x[2])
                        x[3].active.acted = True
                    except AttributeError:
                        print_txt_battle("But it failed")
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
            end_of_turn_effects(self)
