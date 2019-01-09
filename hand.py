from constants import *
import random


class Hand:
    def __init__(self, keys):
        self.hand = {}
        for key in keys:
            self.hand[key] = 0

    def keys(self):
        return self.hand.keys()

    def size(self):
        return sum(self.hand.values())

    def amt(self, key):
        if key in self.hand.keys():
            return self.hand[key]
        else:
            return 0

    def add(self, key, amt=1):
        self.hand[key] += amt

    def subtract(self, key, amt=1):
        self.hand[key] -= amt

    def has(self, key, amt=1):
        return key in self.hand.keys() and self.hand[key] >= amt

    def add_hand(self, other):
        for key in self.hand.keys():
            self.hand[key] += other.hand[key]

    def subtract_hand(self, other):
        for key in self.hand.keys():
            self.hand[key] += other.hand[key]

    def has_hand(self, other):
        for key in other.hand.keys():
            if self.hand[key] < other.hand[key]:
                return False
        return True

    def random_card(self):
        if not self.size() > 0:
            return None
        flat_hand = []
        for card in self.hand.keys():
            flat_hand.extend([card] * self.hand[card])
        return random.choice(flat_hand)


class Resources(Hand):
    def __init__(self, wood=0, clay=0, sheep=0, wheat=0, rock=0):
        super().__init__([WOOD, CLAY, SHEEP, WHEAT, ROCK])
        self.add(WOOD, wood)
        self.add(CLAY, clay)
        self.add(SHEEP, sheep)
        self.add(WHEAT, wheat)
        self.add(ROCK, rock)


class Pieces(Hand):
    def __init__(self, city=0, settlement=0, road=0):
        super().__init__([CITY, SETTLEMENT, ROAD])
        self.add(CITY, city)
        self.add(SETTLEMENT, settlement)
        self.add(ROAD, road)


class Development(Hand):
    def __init__(self, soldier=0, vp=0, monopoly=0, year_of_plenty=0, road_building=0):
        super().__init__([SOLDIER, VICTORY_POINT, MONOPOLY, YEAR_OF_PLENTY, ROAD_BUILDING])
        self.add(SOLDIER, soldier)
        self.add(VICTORY_POINT, vp)
        self.add(MONOPOLY, monopoly)
        self.add(YEAR_OF_PLENTY, year_of_plenty)
        self.add(ROAD_BUILDING, road_building)


def required_hand(structure):
    if structure == ROAD:
        return Resources(wood=1, clay=1)
    elif structure == SETTLEMENT:
        return Resources(wood=1, clay=1, sheep=1, wheat=1)
    elif structure == CITY:
        return Resources(wheat=2, rock=3)
    elif structure == DEV_CARD:
        return Resources(sheep=1, wheat=1, rock=1)

