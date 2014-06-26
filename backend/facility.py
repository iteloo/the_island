import abc


class Facility:

    def __init__(self):
        # default constants
        self.max_condition = 1.0
        self.min_condition = 0.0
        self.damage_of_type = {'natural': .05, 'animal attack': .2}
        self.repair_per_log = .05

        # attribute vars
        self._condition = self.max_condition
        self._players = []

    @property
    def players(self):
        return self._players.copy()

    @property
    def condition(self):
        return self._condition

    def join(self, player):
        self._players.append(player)
        player.current_facility = self

    def leave(self, player):
        self._players.remove(player)
        player.current_facility = None

    def damage(self, amount=None, damage_type='natural'):
        if amount is None:
            amount = self.damage_of_type[damage_type]
        self._condition = max(self._condition - amount, self.min_condition)

    def repair(self, amount=None):
        if amount is None:
            amount = self.repair_per_log
        self._condition = min(self._condition + amount, self.max_condition)


class Production(Facility):
    name = 'production'
    resource_yielded = 'log'


class Farm(Facility):
    name = 'farm'
    resource_yielded = 'food'


class Hospital(Facility):
    name = 'hospital'
    resource_yielded = 'bandage'


class Watchtower(Facility):
    name = 'watchtower'
    resource_yielded = 'bullet'
