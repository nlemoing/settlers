from constants import *
import random
import hand as h


class Bank:
    # Fields
    # resources: cards remaining in the bank
    # development cards: deck of dev cards
    def __init__(self):
        self.resources = h.Resources(wood=19, clay=19, sheep=19, wheat=19, rock=19)
        dev = [SOLDIER] * 14
        dev.extend([VICTORY_POINT] * 5)
        dev.extend([YEAR_OF_PLENTY] * 2)
        dev.extend([MONOPOLY] * 2)
        dev.extend([ROAD_BUILDING])
        random.shuffle(dev)
        self.development = dev

    def get_state(self):
        return {
            "resources": self.resources,
            "dev_cards": len(self.development)
        }

    def deposit(self, hand):
        self.resources.add_hand(hand)

    def get_dev_card(self):
        return self.development.pop()

    def apply_transactions(self, trs):
        player_hands = {}
        for resource in self.resources.keys():
            trs_for_resource = [tr for tr in trs if tr.resource == resource]
            if not trs_for_resource:
                continue
            resources_requested = sum([amt_for_structure(tr.structure) for tr in trs_for_resource])
            if self.resources.has(resource, resources_requested):
                self.resources.subtract(resource, resources_requested)
                for tr in trs_for_resource:
                    if tr.player_id not in player_hands:
                        player_hands[tr.player_id] = h.Resources()
                    player_hands[tr.player_id].add(tr.resource, amt_for_structure(tr.structure))
        return player_hands


def amt_for_structure(structure):
    if structure == CITY:
        return 2
    elif structure == SETTLEMENT:
        return 1
    return 0

