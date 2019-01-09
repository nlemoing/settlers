

class Tile:
    # Fields
    # Resource: number corresponding to constants in resources.py
    # Roll: number corresponding to roll (0 for desert)
    def __init__(self, tile_id, resource, roll):
        self.id = tile_id
        self.resource = resource
        self.roll = roll

    def __repr__(self):
        return "ID: {0}, Resource {1}".format(self.id, self.resource)

    def get_state(self):
        return {
            "id": self.id,
            "resource": self.resource,
            "roll": self.roll
        }