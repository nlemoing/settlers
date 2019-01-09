from server.board import Board
from server.player import Player
from server.bank import Bank
from server.state import GameState
from server import hand as h
from server.constants import *

# Need: Concept of game state
# Client should have some idea of what to do in each state
# Game should return t/f if an action failed

# Map of states to list of actions
# Game.action: action, params
#   Check if action in map
#   If it is, validate parameters
#
class Game:
    # Fields
    # players: list of Players in the game
    # board: Board object
    # bank: Bank object
    # other game vars as needed

    # STATE:
    # Active Player
    # Roll: (0 at start of turn)
    # Board
        # Resource, roll of each tile
        # Status of each path and plot of land
        # Position of Robber
    # Bank
        # Number of each card available
        # Number of dev cards in deck
    # Players
        # Number of cards in hand
        # Number of pieces remaining
        # Number of VPs
    # Game states
        # START_TURN, player_id
            # Actions: ROLL (IN_TURN if not 7, SEVEN if players need to give away cards, otherwise ROB_TILE)
        # IN_TURN, player_id
            # Actions: BUILD structure,
            #          TRADE p1_id, p1_giving_hand, p2_id, p2_giving_hand
            #          PLAY_DEV card, SEA_TRADE ..., PASS
        # BUILDING, player_id, structure
            # Actions: LOCATION location_id, CANCEL
            # Options: list of location_ids
        # PLAYING_DEV_CARD, player_id
            # Monopoly: Actions: RESOURCE resource, CANCEL (to IN_TURN)
            # Year of plenty Actions: RESOURCE resource1, resource2, CANCEL (to IN_TURN)
            # Road building: LOCATION location1, location2 (to IN_TURN) CANCEL (to IN_TURN)
                # Options: list of location_ids
        # ROBBING_TILE, player_id
            # Actions: ROB_TILE tile_id (to ROBBING_PLAYER if players to rob, else to IN_TURN), CANCEL (only if not 7)
            # Options: list of tile_ids
        # ROBBING_PLAYER, player_id, tile_id
            # Actions: ROB_PLAYER player_id (to IN_TURN, CANCEL (back to ROBBING_TILE)
            # Options: list of player_id
        # SEVEN, player_id, players_over_seven
            # Actions: GIVE_AWAY hand (go to ROBBING_TILE if players_over_7 empty, else SEVEN again)
            # Options: any valid hand
    # Client should handle trade UI, only come with a proposal
    # API
    # Roll
    # Trade
    # Build
    # Play Dev Card
    # Pass
    # Start/Quit
    def __init__(self, num_players, dice):
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.board = Board()
        self.bank = Bank()
        self.dice = dice
        self.turn = 1
        self.starting_id = 0
        self.active_id = 0
        self.last_roll = (0, 0)
        self.longest_road_size = 4
        self.longest_road_player = None
        self.largest_army_size = 2
        self.largest_army_player = None
        self.state = GameState("NEW_GAME")

    def __repr__(self):
        return "Board:\n{0}\n".format(self.board)

    def get_state(self):
        return {
            "active_player": self.active_id,
            "roll": self.last_roll,
            "board": self.board.get_state(),
            "bank": self.bank.get_state(),
            "players": [p.get_state() for p in self.players],
            "state": self.state
        }

    def active_player(self):
        return self.players[self.active_id]

    def roll_dice(self):
        self.last_roll = self.dice.roll()

    def players_over_max(self):
        return [player.id for player in self.players if player.num_cards() > 7]

    def distribute_cards(self, roll):
        tr = self.board.transactions(roll)
        hands = self.bank.apply_transactions(tr)
        for player_id, new_cards in hands.items():
            self.players[player_id].hand.add_hand(new_cards)

    def update_longest_road(self, most_recent_road):
        longest = self.board.longest_road(self.active_id, most_recent_road)
        if longest > self.longest_road_size:
            self.longest_road_size = longest
            if self.longest_road_player is not None:
                self.players[self.longest_road_player].longest_road = False
            self.active_player().longest_road = True
            self.longest_road_player = self.active_id

    def update_largest_army(self):
        army = self.active_player().army_size()
        if army > self.largest_army_size:
            self.largest_army_size = army
            if self.largest_army_player is not None:
                self.players[self.largest_army_player].largest_army = False
            self.active_player().largest_army = True
            self.largest_army_player = self.active_id

    # public API
    def roll_to_start(self):
        if self.state.name != "NEW_GAME":
            return False
        self.roll_dice()
        r = sum(self.last_roll)
        self.state.attributes[self.active_id] = r
        if len(self.state.attributes) == self.num_players:
            self.starting_id = max(self.state.attributes, key=self.state.attributes.get)
            self.active_id = self.starting_id
            self.state = GameState("PLACE_PIECES", {"settlements_placed": 0, "structure": SETTLEMENT})
        else:
            self.active_id = (self.active_id + 1) % self.num_players
        return True

    def place_starting_piece(self, location):
        structure = self.state.attributes["structure"]
        if not self.board.can_build(self.active_id, structure, location, game_start=True):
            return False
        self.board.build(self.active_id, structure, location)
        placed = self.state.attributes["settlements_placed"]
        if structure == SETTLEMENT:
            self.state.attributes["settlements_placed"] += 1
            self.state.attributes["structure"] = ROAD
        elif placed == self.num_players * 2:
            self.state = GameState("START_TURN")
        else:
            self.state.attributes["structure"] = SETTLEMENT
            if placed > self.num_players:
                self.active_id = (self.active_id - 1) % self.num_players
            elif placed < self.num_players:
                self.active_id = (self.active_id + 1) % self.num_players
        return True

    def start_turn(self):
        if self.state.name != "START_TURN":
            return False
        self.roll_dice()
        r = sum(self.last_roll)
        if r == 7:
            p_over = self.players_over_max()
            if p_over:
                self.state = GameState("GIVE_AWAY", {"players_over": p_over})
            else:
                self.state = GameState("ROBBING")
        else:
            self.distribute_cards(r)
            self.state = GameState("IN_TURN")

    def give_away(self, p_id, hand):
        if self.state.name != "GIVE_AWAY" or p_id not in self.state.attributes["players_over"]:
            return False
        p = self.players[p_id]
        if hand.size() != p.hand.size() // 2 or not p.hand.has_hand(hand):
            return False
        p.hand.subtract(hand)
        p_over = self.players_over_max()
        if p_over:
            self.state.attributes["players_over"] = p_over
        else:
            self.state = GameState("ROBBING")
        return True

    def buy_dev_card(self):
        if self.state.name != "IN_TURN":
            return False
        cost = h.required_hand(DEV_CARD)
        if self.active_player().can_buy(cost):
            self.active_player().buy(cost)
            self.bank.deposit(cost)
            d = self.bank.get_dev_card()
            self.active_player().development.add(d)
            return True
        return False

    def build_structure(self, structure):
        if self.state.name != "IN_TURN":
            return False
        cost = h.required_hand(structure)
        if self.active_player().can_build(structure, cost):
            self.state = GameState("BUILDING", {"structure": structure})
            return True
        return False

    def build_location(self, location):
        if self.state.name != "BUILDING":
            return False
        structure = self.state.attributes["structure"]
        cost = h.required_hand(structure)
        if not self.board.can_build(self.active_id, structure, location):
            return False
        self.board.build(self.active_id, structure, location)
        self.active_player().build(structure, cost)
        self.bank.deposit(cost)
        if structure == ROAD:
            self.update_longest_road(location)
        self.state = GameState("IN_TURN")
        return True

    def trade(self, other_id, active_res, other_res):
        if self.state.name != "IN_TURN":
            return False
        p1 = self.active_player()
        p2 = self.players[other_id]
        if not (p1.hand.has(active_res) and p2.hand.has(other_res)):
            return False
        p1.hand.subtract(active_res)
        p1.hand.add(other_res)
        p2.hand.subtract(other_res)
        p2.hand.add(active_res)
        return True

    def pass_turn(self):
        if self.state.name != "IN_TURN":
            return False
        self.active_id = (self.active_id + 1) % self.num_players
        if self.active_id == self.starting_id:
            self.turn += 1
        self.state = GameState("START_TURN")
        return True

    def rob_tile(self, tile_id):
        if self.state.name != "ROBBING" or not self.board.can_rob_tile(tile_id):
            return False
        if not self.board.players_on_tile(tile_id):
            self.state = GameState("IN_TURN")
        else:
            self.state = GameState("ROBBING_PLAYER", {"tile": tile_id})
        return True

    def rob_player(self, player_id):
        if self.state.name != "ROBBING_PLAYER":
            return False
        tile_id = self.state.attributes["tile"]
        if player_id not in self.board.players_on_tile(tile_id):
            return False
        self.board.rob_tile(tile_id)
        active_player = self.active_player()
        other_player = self.players[player_id]
        if other_player.num_cards():
            res = other_player.hand.random_card()
            other_player.hand.subtract(res)
            active_player.hand.add(res)
        self.state = GameState("IN_TURN")
        return True

    def play_dev_card(self, card):
        if self.state.name != "IN_TURN" or not self.active_player().development.has(card) or card == VICTORY_POINT:
            return False
        self.active_player().play_dev(card)
        if card == ROAD_BUILDING and not self.active_player().can_place_piece(ROAD):
            return False
        elif card == ROAD_BUILDING:
            self.state = GameState("ROAD_BUILDING", {"remaining_roads": 2})
        elif card == MONOPOLY:
            self.state = GameState("MONOPOLY")
        elif card == YEAR_OF_PLENTY:
            self.state = GameState("YEAR_OF_PLENTY")
        else:
            self.update_largest_army()
            self.state = GameState("ROBBING")
        return True

    def year_of_plenty(self, res1, res2):
        if self.state.name != "YEAR_OF_PLENTY":
            return False
        self.active_player().hand.add(res1)
        self.active_player().hand.add(res2)
        self.state = GameState("IN_TURN")
        return True

    def road_building(self, location):
        if self.state.name != "ROAD_BUILDING" or not self.board.can_build(self.active_id, ROAD, location):
            return False
        self.board.build(self.active_id, ROAD, location)
        self.active_player().place_piece(ROAD)
        self.update_longest_road(location)
        self.state.attributes["remaining_roads"] -= 1
        if self.state.attributes["remaining_roads"] <= 0 or not self.active_player().can_place_piece(ROAD):
            self.state = GameState("IN_TURN")
        return True

    def monopoly(self, res):
        if self.state.name != "MONOPOLY":
            return False
        active = self.active_player()
        other_players = [p for p in self.players if p.id != active.id]
        for p in other_players:
            amt = p.hand.amt(res)
            p.hand.subtract(res, amt)
            active.hand.add(res, amt)
        self.state = GameState("IN_TURN")
        return True
