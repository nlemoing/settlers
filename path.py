

class Path:
    # Fields
    # player: 0 if undeveloped, player ID if developed
    def __init__(self, path_id):
        self.id = path_id
        self.player_id = None
        self.built = False

    # build: takes a player id and builds on the path if it isn't built already
    # returns true if successful, false otherwise
    def build(self, player_id):
        if self.built:
            return False
        self.player_id = player_id
        self.built = True
        return True

    def can_build(self):
        return not self.built

    def get_state(self):
        return {
            "id": self.id,
            "built": self.built,
            "player_id": self.player_id
        }
