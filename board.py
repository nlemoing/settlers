from server.constants import *
import random
from server.tile import Tile
from server.land import Land
from server.path import Path
from server.transaction import Transaction
from server import adjacency as adj


class Board:
    # Fields
    # tiles: list of 19 Tiles
    # plots: list of 54 Land
    # paths: list of 72 Paths
    def __init__(self):
        tile_resources = [DESERT, SHEEP, WOOD, WHEAT]
        tile_resources.extend([WOOD, CLAY, SHEEP, WHEAT, ROCK] * 3)
        random.shuffle(tile_resources)
        rolls = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
        desert = tile_resources.index(DESERT)
        rolls.insert(desert, 0)
        self.tiles = [Tile(i, tile_resources[i], rolls[i]) for i in range(19)]
        self.land = [Land(i) for i in range(54)]
        self.paths = [Path(i) for i in range(72)]
        self.robber = [t.resource for t in self.tiles].index(DESERT)

    def __repr__(self):
        return ("Tiles: {0}\n"
                "Land: {1}\n"
                "Path: {2}\n").format(self.tiles, self.land, self.paths)

    def get_state(self):
        return {
            "Tiles": [t.get_state() for t in self.tiles],
            "Land": [l.get_state() for l in self.land],
            "Paths": [p.get_state() for p in self.paths]
        }

    def transactions(self, roll):
        tile_ids = [tile.id for tile in self.tiles if tile.roll == roll and tile.id != self.robber]
        trs = []
        for tile_id in tile_ids:
            resource = self.tiles[tile_id].resource
            if resource == DESERT:
                continue
            for land_id in adj.land_for_tile[tile_id]:
                land = self.land[land_id]
                if land.built:
                    trs.append(Transaction(land.player_id, resource, land.structure))
        return trs

    def can_build(self, player_id, structure, location, game_start=False):
        if structure == ROAD:
            if not self.paths[location].can_build():
                return False
            if game_start:
                for land_id in adj.land_for_path[location]:
                    if self.land[land_id].built and self.land[land_id].player_id == player_id:
                        return True
                return False
            else:
                for path_id in adj.path_neighbors(location):
                    if self.paths[path_id].built and self.paths[path_id].player_id == player_id:
                        return True
                return False
        if not self.land[location].can_build(player_id, structure):
            return False
        if structure == SETTLEMENT:
            if not game_start:
                adjacent_roads = False
                for path_id in adj.path_for_land[location]:
                    if self.paths[path_id].built and self.paths[path_id].player_id == player_id:
                        adjacent_roads = True
                if not adjacent_roads:
                    return False
            for land_id in adj.land_neighbors(location):
                if self.land[land_id].built:
                    return False
            return True
        return True

    def build(self, player_id, structure, location):
        if structure == ROAD:
            path = self.paths[location]
            path.build(player_id)
        elif structure == SETTLEMENT or structure == CITY:
            land = self.land[location]
            land.build(player_id, structure)

    def can_rob_tile(self, tile_id):
        return tile_id != self.robber

    def rob_tile(self, tile_id):
        self.robber = tile_id

    def players_on_tile(self, tile_id):
        players = []
        for land_id in adj.land_for_tile[tile_id]:
            land = self.land[land_id]
            if land.built and land.player_id not in players:
                players.append(land.player_id)
        return players

    def longest_road(self, player_id, most_recent_road):
        def longest_road_from_land(land_id, visited):
            paths = adj.path_for_land(land_id)
            outgoing_roads = []
            for path_id in paths:
                path = self.paths[path_id]
                if path.built and path.player_id == player_id and path_id not in visited:
                    next_land = adj.next_land(land_id, path_id)
                    outgoing_roads.append(longest_road_from_land(next_land, visited + [path_id]))
            if not outgoing_roads:
                return visited
            return max(outgoing_roads, key=len)
        land = adj.land_for_path[most_recent_road]
        first_path = longest_road_from_land(land[0], [most_recent_road])
        second_path = longest_road_from_land(land[1], first_path)
        return second_path
