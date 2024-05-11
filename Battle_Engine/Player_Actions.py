from bearlibterminal import terminal
from Battle_Engine.Battle_UI_Functions import print_ui, print_txt_battle
from Helpers import get_input
from Battle_Engine.Status_Checks import can_swap
from Data_Builders import moves


def player_turn(self, player):
    while True:
        terminal.clear_area(45, 20, 60, 4)
        terminal.printf(45, 20, "1 Fight\n2 Pokemon")
        print_txt_battle("What will you do?", 0)
        i = get_input(2)
        if i == 0:
            print_moves(player.active)
            while True:
                print_txt_battle("What move would you like to use?(1-4)", 0)
                i = get_input(4, is_backspace_used=True)
                if i == 42:
                    break
                else:
                    move = moves.get(player.active.moves[i])
                    print_txt_battle(f"Use {move.get("name")}?(Enter/Backspace) {move.get("description")}", 0)
                    while True:
                        i = get_input(is_enter_used=True, is_backspace_used=True)
                        if i == 40:
                            return move.copy()
                        elif i == 42:
                            break
        elif i == 1:
            a = player_swap(self, False, player)
            if a is not None:
                return a


def print_moves(mon):
    terminal.clear_area(45, 20, 42, 4)
    y = 19
    for num in range(0, 4):
        y += 1
        if num <= len(mon.moves) - 1:
            move = moves.get(mon.moves[num])
            terminal.printf(45, y, f"{num + 1} {move.get("name")} {move.get("type")} "
                                   f"Pwr:{move.get("power")} Acc:{move.get("accuracy")}")
        else:
            terminal.printf(45, y, "Empty Slot")


def player_swap(self, must_swap, player):
    while True:
        terminal.layer(0)
        terminal.put(0, 0, 0xF8FD)
        terminal.layer(1)
        terminal.clear_area(45, 17, 42, 7)
        y = 17
        for num in range(0, 6):
            y += 1
            if num <= len(player.team) - 1:
                terminal.printf(45, y, f"{num + 1} {player.team[num]}")
            else:
                terminal.printf(45, y, "Empty Slot")
        print_txt_battle("What Pokemon would you like to view/swap? (1-6)", 0)
        i = get_input(6, is_backspace_used=True)
        if i == 42 and not must_swap:
            terminal.clear_area(45, 17, 42, 7)
            print_ui(self)
            break
        elif i + 1 <= len(player.team):
            while True:
                terminal.clear_area(45, 17, 42, 7)
                print_ui(self)
                print_moves(self, i)
                print_txt_battle(f"Swap to {player.team[i].species}?(Enter/Backspace)"
                                 f"{player.team[i].info}", 0)
                x = get_input(is_enter_used=True, is_backspace_used=True)
                if x == 40:
                    if not must_swap and not can_swap(player.active, ai.active):
                        print_txt_battle(f"{player.active.species} is trapped and cant switch out!")
                        break
                    if player.active == player.team[i]:
                        print_txt_battle(f"{player.team[i].species} is already out")
                        break
                    if player.active is not None:
                        if player.active.ability == "Natural Cure" and player.active.status != "":
                            # print pop up
                            print_txt_battle(f"{player.name}'s {player.active.species}'s cured it's status")
                            player.active.status = ""
                        player.active.reset_temp()
                    return player.team[i]
                if x == 42:
                    break


def select_lead(self):
    terminal.clear()
    terminal.put(0, 0, 0xF8FC)
    terminal.printf(22, 1, "What pokemon would you like to lead?")
    print_player_pokemon()
    terminal.refresh()
    slot = get_input(len(self.player.team))
    terminal.clear()
    return self.player.team[slot]