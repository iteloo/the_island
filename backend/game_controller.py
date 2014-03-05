from backend import game


class GameController(object):
    """Controller for managing multiple games.

    Right now only supports a single staticGame

    """

    staticGame = game.Game()