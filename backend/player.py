from backend import message
from backend import helpers
from backend.stage import event
from backend import observed_collection

import collections


class Player(message.MessageDelegate):

    conditions = ['health', 'antihunger']
    MAX_CONDITIONS = {'health': 100.0, 'antihunger': 100.0}
    MIN_CONDITIONS = {'health': 0.0, 'antihunger': 0.0}

    ANTIHUNGER_PER_FOOD = 50.0
    HEALTH_PER_BANDAGE = 35.0

    def __init__(self, id, *args, **kwargs):
        # call super
        super().__init__(*args, **kwargs)

        # player vars
        self.id = id

        # game management vars
        self.current_game = None

        # game state vars (will be initialized once we join game)
        self.current_job = None
        self._inventory = None
        self._condition = None

        # event handling
        self.event_handler = event.EventHandler(self)

    def __str__(self):
        return self.id

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

    def quit(self):
        from backend import game_controller
        game_controller.universal_controller.quit_game(self)

    @message.forward('self.current_game.current_stage')
    def after_client_setup(self) -> None:
        pass

    def item_activated(self, item_name: str) -> None:
        if item_name == 'log':
            pass
        elif item_name == 'food':
            self.add_inventory(food=-1)
            self.add_condition(antihunger=self.ANTIHUNGER_PER_FOOD)
            self.event_handler.schedule_event(event.NotificationEvent(self, text='It\'s so yummyyy'), location='immediately')
        elif item_name == 'bandage':
            self.add_inventory(bandage=-1)
            self.add_condition(health=self.HEALTH_PER_BANDAGE)
            self.event_handler.schedule_event(event.NotificationEvent(self, text='The bandage stinks a bit, but you feel better.'), location='immediately')
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
    def refresh(self):
        pass

    @message.sending
    def stage_begin(self, stage_type: str, callback: collections.Callable) -> None:
        pass

    @message.sending
    def update_job_selections(self, job_selections: dict) -> None:
        pass

    @message.sending
    def display_event(self, title: str, image_name: str, text: str, responses: list, inputs: list, callback: collections.Callable) -> None:
        pass

    ### operational methods

    @property
    def inventory(self):
        return self._inventory.copy()

    @property
    def condition(self):
        return self._condition.copy()

    def add_inventory(self, **items):
        for r, count in items.items():
            self._inventory[r] += count

    def subtract_inventory(self, **items):
        for r, count in items.items():
            self._inventory[r] -= count

    def add_condition(self, **condition):
        for r, count in condition.items():
            new_r = self.condition[r] + count
            self._condition[r] = min(new_r, self.MAX_CONDITIONS[r])

    def subtract_condition(self, **condition):
        for r, count in condition.items():
            new_r = self.condition[r] - count
            self._condition[r] = max(new_r, self.MIN_CONDITIONS[r])

    ### event handler delegate methods

    def event_queue_did_empty(self, event_queue):
        if self.current_game.current_stage.stage_type == 'Day':
            self.current_game.current_stage.ready(self)

    ### message delegate methods ###

    def on_open(self):
        pass

    def on_close(self):
        # if in a game (e.g. caused by disconnect), stash player
        if self.current_game:
            self.current_game.stash_player(self)
        # else probably caused by leaving (rather, the resulting refreshing)

    ### event methods ###

    def notify(self, title='', text='', on_dismiss=None):
        """Convenience method to send a NotificationEvent to client"""

        self.event_handler.schedule_event(event.NotificationEvent(self, title=title, text=text, on_dismiss=on_dismiss), location='immediately')

    ### game management methods ###

    def player_info_updated(self, info, update_type):
        self.update_player_info(self.inventory, self.condition)

    def display_main_menu(self):
        self.event_handler.schedule_event(event.MainMenuEvent(self), location='immediately')

    def will_join_game(self, game):
        # initialize game state vars
        self.current_game = game
        self.current_job = None
        self._inventory = observed_collection.ObservedDict()
        self._condition = observed_collection.ObservedDict()
        self._inventory.add_observer(self, self.player_info_updated)
        self._condition.add_observer(self, self.player_info_updated)
        self._inventory.update(dict((r, 4) for r in game.resources))
        self._condition.update(dict(zip(Player.conditions, [100, 100])))

    def did_quit_game(self, game):
        # clean up vars
        self.current_game = None
        self.current_job = None
        self._inventory = None
        self._condition = None

        # tell client to refresh
        self.refresh()

    def will_be_stashed(self, game):
        pass

    def will_be_unstashed(self, game):
        # hack: initiate first update
        self._inventory.update(self.inventory)
