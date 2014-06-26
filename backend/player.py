from backend import message
from backend import helpers
from backend.stage import event
from backend import observed_collection

import collections


class Player(message.MessageDelegate):
    conditions = ['health', 'antihunger']

    def __init__(self, id, *args, **kwargs):
        # call super
        super().__init__(*args, **kwargs)

        # player stats
        self.max_condition = {'health': 100.0, 'antihunger': 100.0}
        self.min_condition = {'health': 0.0, 'antihunger': 0.0}
        self.antihunger_per_food = 50.0
        self.health_per_bandage = 35.0

        # player vars
        self.id = id

        # game management vars
        self.current_game = None

        # game state vars (will be initialized once we join game)
        self.current_facility = None
        self._inventory = None
        self._condition = None

        # event handling
        self.event_handler = event.EventHandler(self)

    def __str__(self):
        return self.id

    ### player status ###

    @property
    def inventory(self):
        return self._inventory

    @property
    def condition(self):
        return self._condition

    def player_info_updated(self, info, update_type):
        # need to use copy to pass in regular (unobserved) dictionaries
        self.update_player_info(self.inventory.copy(), self.condition.copy())

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

    ### convenience methods ###

    def notify(self, title='', text='', on_dismiss=None):
        """Convenience method to send a NotificationEvent to client"""

        self.event_handler.schedule_event(event.NotificationEvent(self, title=title, text=text, on_dismiss=on_dismiss), location='immediately')

    def display_main_menu(self):
        self.event_handler.schedule_event(event.MainMenuEvent(self), location='immediately')

    ### game management methods ###

    def will_join_game(self, game):
        # initialize game state vars
        self.current_game = game
        self.current_facility = None
        self._inventory = observed_collection.ObservedDict()
        self._condition = observed_collection.ObservedDict()
        self._inventory.add_observer(self, self.player_info_updated)
        self._condition.add_observer(self, self.player_info_updated)
        self._inventory.update(dict((f.resource_yielded, 4) for f in game.facilities.values()))
        self._condition.update(dict(zip(Player.conditions, [100, 100])))

    def did_quit_game(self, game):
        # clean up vars
        self.current_game = None
        self.current_facility = None
        self._inventory = None
        self._condition = None

        # tell client to refresh
        self.refresh()

    def will_be_stashed(self, game):
        pass

    def will_be_unstashed(self, game):
        # hack: initiate first update
        self._inventory.update(self.inventory)

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
            self._inventory['food'] -= 1
            self._condition['antihunger'] += self.antihunger_per_food
            self.event_handler.schedule_event(event.NotificationEvent(self, text='It\'s so yummyyy'), location='immediately')
        elif item_name == 'bandage':
            self._inventory['bandage'] -= 1
            self._condition['health'] += self.health_per_bandage
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

