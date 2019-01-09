from constants import *
import hand as h


class Player:
    # Fields
    # id: player id
    def __init__(self, player_id):
        self.id = player_id
        self.hand = h.Resources()
        self.development = h.Development()
        self.played_development = h.Development()
        self.remaining_pieces = h.Pieces(city=4, settlement=5, road=15)
        self.played_pieces = h.Pieces()
        self.longest_road = False
        self.largest_army = False

    def get_state(self):
        return {
            "id": self.id,
            "hand": self.hand,
            "development_cards": self.development,
            "remaining_pieces": self.remaining_pieces
        }

    def victory_points(self):
        city_pts = self.played_pieces.amt(CITY) * 2
        settlement_pts = self.played_pieces.amt(SETTLEMENT)
        dev_pts = self.development.amt(VICTORY_POINT)
        lr = 2 if self.longest_road else 0
        la = 2 if self.largest_army else 0
        return city_pts + settlement_pts + dev_pts + lr + la

    def num_cards(self):
        return self.hand.size()

    def can_place_piece(self, structure):
        return self.remaining_pieces.has(structure)

    def place_piece(self, structure):
        self.remaining_pieces.subtract(structure)
        self.played_pieces.add(structure)

    def can_buy(self, cost):
        return self.hand.has_hand(cost)

    def buy(self, cost):
        self.hand.subtract_hand(cost)

    def can_build(self, structure, cost):
        return self.can_place_piece(structure) and self.can_buy(cost)

    def build(self, structure, cost):
        self.place_piece(structure)
        self.buy(cost)

    def play_dev(self, card):
        if card != VICTORY_POINT:
            self.development.subtract(card)
            self.played_development.add(card)

    def army_size(self):
        return self.played_development.amt(SOLDIER)
