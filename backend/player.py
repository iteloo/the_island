from backend import message
from backend import game_controller
from backend import helpers


class Player(message.MessageDelegate):
    _currentId = 0

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
    def server_info(callback):
        """Return information about the current running version of the server"""

        from backend.server import RUN_DATE, VERSION
        callback(start_date=RUN_DATE, version=VERSION)

    @message.forward('self.current_game')
    def item_activated(self, item_name):
        pass

    @message.forward('self.current_game.current_stage')
    def job_selected(self, item_name):
        pass

    @message.forward('self.current_game.current_stage')
    def ready(self, item_name):
        pass

    @message.forward('self.current_game.current_stage')
    def trade_proposed(self, item_name):
        pass

    ### client-side methods ###

    @message.sending
    def update_game_info(self, player_count: int) -> None:
        pass

    @message.sending
    def update_player_info(self, inventory: dict, condition: dict) -> None:
        pass

    @message.sending
    def stage_begin(self, stage_type: str, callback) -> None:
        pass

    @message.sending
    def update_job_selections(self, job_selections: dict) -> None:
        pass

    @message.sending
    def display_event(self, title: str, image_name: str, text: str, responses: list, callback) -> None:
        pass

    ### messageDelegate methods ###

    @helpers.logging()
    def on_open(self):
        # join the only game for now
        self.join_game(game_controller.GameController.staticGame)

    def on_close(self):
        # quit game
        self.quit_game()

    ### game management methods ###

    def join_game(self, game):
        game.add_player(self)
        self.current_game = game

    def quit_game(self):
        self.current_game.remove_player(self)
        self.current_game = None