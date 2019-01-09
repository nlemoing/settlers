import random


class FairDice:
    def roll(self):
        r1 = random.randint(1, 6)
        r2 = random.randint(1, 6)
        return r1, r2


class FixedDice:
    def __init__(self, fname):
        self.f = open(fname, "r")
