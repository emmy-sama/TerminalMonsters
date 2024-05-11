from bearlibterminal import terminal
from Helpers import print_txt
from random import choice
from Battle_Engine


class Player:
    def __init__(self):
        print_txt("What is your name?: ", 0)
        self.name = terminal.read_str(21, 20, "", 12)[1]
        self.team = []
        self.active = None
        self.opponent = None
        self.reflect = False
        self.light_screen = False
        self.mist = 0


class Ai:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.active = None
        self.opponent = None
        self.reflect = False
        self.light_screen = False
        self.mist = 0

    def ai_select_move(self):
        return choice(self.active.moves)
