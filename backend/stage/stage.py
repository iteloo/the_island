from backend import server


class Stage(object):
    stage_type = None

    def __init__(self, game):
        self.game = game
        pass

    @classmethod
    def title(cls):
        return None

    def begin(self):
        for player in self.game.players:
            player.stage_begin(stage_type=self.stage_type, callback=player.after_client_setup)

    def after_client_setup(self, sender):
        pass

    def can_end(self):
        server.ioloop.add_callback(self.game.stage_can_end, self)

    def end(self):
        pass

    def handle_add_player(self, new_player):
        new_player.stage_begin(stage_type=self.stage_type, callback=new_player.after_client_setup)

    def handle_remove_player(self, player_removed):
        pass
