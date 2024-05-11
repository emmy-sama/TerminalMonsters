from Data_Builders import moves, types
from bearlibterminal import terminal

class Battle:
    def __init__(self, player, ai):
        self.moves = moves
        self.types = types
        self.player = player
        self.ai = ai
        self.ai.active = self.ai.team[0]
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

