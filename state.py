class GameState:
    def __init__(self, name, attrs=None):
        self.name = name
        self.attributes = attrs if attrs is not None else {}

    def __repr__(self):
        return "{0.name}, {0.attributes}".format(self)
