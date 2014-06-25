from backend import message
from backend import helpers
from backend import player

import collections


class Zombie(message.MessageDelegate):

    _currentId = 0

    def __init__(self, *args, **kwargs):
        # call super
        super().__init__(*args, **kwargs)

        # general vars
        self.id = self._currentId
        Zombie._currentId += 1

    def __str__(self):
        return "Zombie%d" % self.id

    ### server-side methods ###

    @staticmethod
    def server_info(callback: collections.Callable) -> None:
        """Return information about the current running version of the server"""

        from backend.server import RUN_DATE, VERSION
        callback(start_date=RUN_DATE, version=VERSION)

    def name_entered(self, name: str) -> None:
        from backend import game_controller

        # attempt to identify player object
        p = game_controller.universal_controller.player_with_id(name)

        # todo: handle case where player with same id is actually playing
        # case 3: if new player
        if not p:
            # make new player object
            p = player.Player(name)
            # register player with game controller
            game_controller.universal_controller.register_player(p)

        # replace zombie by player object, this will properly set the handler on player
        self._message_handler.delegate = p
        # this zombie should now be living a free life

        # case 1: if existing player that is already in game
        if p and p.current_game:
            p.current_game.unstash_player(p)
        # case 2: if existing player not in a game
        # case 3: if new player
        elif (not p) or (p and not p.current_game):
            # display main menu
            p.display_main_menu()

    ### client-side methods ###

    @message.sending
    def echo(self, callback: collections.Callable, *args, **kwargs):
        pass

    ### message delegate methods ###

    def on_open(self):
        pass

    def on_close(self):
        pass