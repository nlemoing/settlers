from server.constants import *


class Land:
    # Fields
    # player: number corresponding to player ID. 0 if not claimed
    # dev: number corresponding to development: 0 if undeveloped, 1 if settlement, 2 if city
    # bonus: e.g. 2 for 1. depends on land_id
    def __init__(self, land_id):
        self.id = land_id
        self.player_id = None
        self.built = False
        self.structure = EMPTY

    def build(self, player_id, structure):
        if structure == SETTLEMENT:
            self.built = True
            self.player_id = player_id
        self.structure = structure

    def can_build(self, player_id, structure):
        if structure == SETTLEMENT:
            return not self.built
        elif structure == CITY:
            return self.built and self.structure == SETTLEMENT and self.player_id == player_id
        return False

    def get_state(self):
        return {
            "id": self.id,
            "developed": self.built,
            "structure": self.structure,
            "player_id": self.player_id
        }

