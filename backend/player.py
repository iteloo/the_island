from backend import message
from backend import game_controller
from backend import helpers
from backend import game

import collections


class Player(message.MessageDelegate):
    _currentId = 0
    conditions = ['health', 'antihunger']

    def __init__(self, *args, **kwargs):
        # call super
        super(Player, self).__init__(*args, **kwargs)

        # general vars
        self.id = self._currentId
        Player._currentId += 1

        # game management vars
        self.current_game = None

        # game state vars
        self.current_job = None
        self._inventory = dict((r, 0) for r in game.Game.resources)
        self._condition = dict(zip(Player.conditions, ['3','2']))

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

    @message.forward('self.current_game')
    def item_activated(self, item_name: str) -> None:
        pass

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
        return self._inventory

    @inventory.setter
    def inventory(self, value):
        self._inventory = value
        self.update_player_info(self._inventory, self._condition)

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        self._condition = value
        self.update_player_info(self._inventory, self._condition)

    def addInventory(self, items):
        self.inventory = dict((r, self.inventory[r] + count) for r, count in items.items())


    def subtractInventory(self, items):
        self.inventory = dict((r, self.inventory[r] - count) for r, count in items.items())

    ### messageDelegate methods ###

    def on_open(self):
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
        game.add_player(self)

    def quit_game(self):
        self.current_game.remove_player(self)
        self.current_game = None