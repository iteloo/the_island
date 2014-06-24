from backend import game


class GameController(object):
    """Controller for managing multiple games.

    Right now only supports a single staticGame

    """

    def __init__(self):
        self.games = []
        self._player_with_id = {}  # dictionary of all players (might not be in a game)

    def register_player(self, player):
        assert player.id not in self._player_with_id
        self._player_with_id[player.id] = player

    def deregister_player(self, player):
        """Not used atm"""
        assert player.id in self._player_with_id
        self._player_with_id.pop(player.id)

    def new_game(self, player):
        new_game = game.Game(owner=player)
        new_game.begin()
        self.games.append(new_game)
        player.will_join_game(new_game)
        new_game.add_player(player)

    def join_game(self, owner, player):
        game_to_join = self.game_with_owner(owner)
        if game_to_join:
            player.will_join_game(game_to_join)
            game_to_join.add_player(player)
            return True
        else:
            return False

    def quit_game(self, player):
        # todo: implement this; call this when client choose to quit using in-game menu

        game_to_quit = player.current_game
        game_to_quit.remove_player(self)
        player.did_quit_game(game_to_quit)

    #### convenience ####

    def game_with_owner(self, owner):
        # todo: inefficient; add database structure
        games = [g for g in self.games if g.owner is owner]
        return games[0] if games else None

    def game_with_player(self, player):
        # todo: inefficient; add database structure
        games = [g for g in self.games if player in g.players]
        return games[0] if games else None

    def player_with_id(self, name):
        try:
            return self._player_with_id[name]
        except KeyError:
            return None

universal_controller = GameController()