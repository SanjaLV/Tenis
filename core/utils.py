class GraphData(object):

    def __init__(self, game_number, *args):
        self.game_number = game_number
        self.values = ""
        for a in args:
            self.values += str(a) + ","
