from backend import message
from backend import helpers
from backend.stage import event

import collections


class Player(message.MessageDelegate):

    _currentId = 0
    conditions = ['health', 'antihunger']
    MAX_CONDITIONS = {'health': 100.0, 'antihunger': 100.0}
    MIN_CONDITIONS = {'health': 0.0, 'antihunger': 0.0}

    ANTIHUNGER_PER_FOOD = 50.0
    HEALTH_PER_BANDAGE = 35.0

    def __init__(self, *args, **kwargs):
        # call super
        super(Player, self).__init__(*args, **kwargs)

        # general vars
        self.id = self._currentId
        Player._currentId += 1

        # game management vars
        self.current_game = None

        # game state vars (will be initialized once we join game)
        self.current_job = None
        self._inventory = None
        self._condition = None

        # event handling
        self.event_handler = event.EventHandler(self)

    def __str__(self):
        return "Player%d" % self.id

    ### server-side methods ###

    @staticmethod
    def echo(callback, *args, **kwargs):
        """Echo args back to callback

        For testing purposes only.

        """

        callback(*args, **kwargs)

    @staticmethod
    def server_info(callback: collections.Callable) -> None:
        """Return information about the current running version of the server"""

        from backend.server import RUN_DATE, VERSION
        callback(start_date=RUN_DATE, version=VERSION)

    @message.forward('self.current_game.current_stage')
    def after_client_setup(self) -> None:
        pass

    def item_activated(self, item_name: str) -> None:
        if item_name == 'log':
            pass
        elif item_name == 'food':
            self.add_inventory(food=-1)
            self.add_condition(antihunger=self.ANTIHUNGER_PER_FOOD)
            self.event_handler.schedule_event(event.MessageEvent(self, text='It\'s so yummyyy'), location='immediately')
        elif item_name == 'bandage':
            self.add_inventory(bandage=-1)
            self.add_condition(health=self.HEALTH_PER_BANDAGE)
            self.event_handler.schedule_event(event.MessageEvent(self, text='The bandage stinks a bit, but you feel better.'), location='immediately')
        elif item_name == 'bullet':
            pass
        else:
            raise "Item not recognized!"

    @message.forward('self.current_game.current_stage')
    def job_selected(self, job: str) -> None:
        pass

    @message.forward('self.current_game.current_stage')
    def ready(self) -> None:
        pass

    @message.forward('self.current_game.current_stage')
    def trade_proposed(self, items: dict, callback: collections.Callable) -> None:
        pass

    ### client-side methods ###

    @message.sending
    def echo(self, callback: collections.Callable, *args, **kwargs):
        pass

    @message.sending
    def update_game_info(self, player_count: int) -> None:
        pass

    @message.sending
    def update_player_info(self, inventory: dict, condition: dict) -> None:
        pass

    @message.sending
    def stage_begin(self, stage_type: str, callback: collections.Callable) -> None:
        pass

    @message.sending
    def update_job_selections(self, job_selections: dict) -> None:
        pass

    @message.sending
    def display_event(self, title: str, image_name: str, text: str, responses: list, callback: collections.Callable) -> None:
        pass

    ### operational methods

    @property
    def inventory(self):
        return self._inventory.copy()

    @inventory.setter
    def inventory(self, value):
        self._inventory = value
        self.update_player_info(self.inventory, self.condition)

    @property
    def condition(self):
        return self._condition.copy()

    @condition.setter
    def condition(self, value):
        self._condition = value
        self.update_player_info(self.inventory, self.condition)

    def add_inventory(self, **items):
        for r, count in items.items():
            self._inventory[r] += count
        # hack: notify client
        self.inventory = self.inventory

    def subtract_inventory(self, **items):
        for r, count in items.items():
            self._inventory[r] -= count
        # hack: notify client
        self.inventory = self.inventory

    def add_condition(self, **condition):
        for r, count in condition.items():
            new_r = self.condition[r] + count
            self._condition[r] = min(new_r, self.MAX_CONDITIONS[r])
        # hack: notify client
        self.condition = self.condition

    def subtract_condition(self, **condition):
        for r, count in condition.items():
            new_r = self.condition[r] - count
            self._condition[r] = max(new_r, self.MIN_CONDITIONS[r])
        # hack: notify client
        self.condition = self.condition

    ### event handling methods

    def event_queue_did_empty(self, event_queue):
        # todo: fix this; this is day stage specific
        if self.current_game.current_stage.stage_type == 'Day':
            self.current_game.current_stage.ready(self)

    ### message delegate methods ###

    def on_open(self):
        from backend import game_controller

        # join the only game for now
        self.join_game(game_controller.GameController.staticGame)

        # hack: initiate first update
        self.inventory = self.inventory
        self.condition = self.condition

    def on_close(self):
        # quit game
        self.quit_game()

    ### game management methods ###

    def join_game(self, game):
        self.current_game = game

        # initialize game state vars
        self.current_job = None
        self._inventory = dict((r, 4) for r in game.resources)
        self._condition = dict(zip(Player.conditions, [100, 100]))

        game.add_player(self)

    def quit_game(self):
        self.current_game.remove_player(self)
        self.current_game = None