from backend import message
from backend import helpers

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

        # game state vars (will be initialized once we join game)
        self.current_job = None
        self._inventory = None
        self._condition = None

        # event management variable
        self._event_queue = []
        self._current_event = None

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

    def add_inventory(self, items):
        for r, count in items.items():
            self.inventory[r] += count
        # hack: notify client
        self.inventory = self.inventory

    def subtract_inventory(self, items):
        for r, count in items.items():
            self.inventory[r] -= count
        # hack: notify client
        self.inventory = self.inventory

    ### event handling methods

    def schedule_events(self, events: list, start_queue=True, immediately=False):
        self._event_queue = events + self._event_queue if immediately else self._event_queue + events
        if start_queue:
            self.next_event()

    def schedule_event(self, event, **kwargs):
        self.schedule_events([event], **kwargs)

    def event_did_end(self, event):
        # if the event that just ended is the current event, then go to the next event
        # otherwise it must have been terminated by the player
        self._current_event = None
        self.next_event()

    def next_event(self, force=False):
        # if there is currently an event, end it; this will result in a event_did_end call after this method has returned
        if self._current_event:
            if force:
                self._current_event.end()
                # make sure we return so that next_event doesn't get called twice
            return

        # retrieve the next event on the queue and evoke it
        if self._event_queue:
            new_event = self._event_queue.pop(0)
            self._current_event = new_event
            new_event.evoke()
        else:
            # todo: fix this; this is day stage specific
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