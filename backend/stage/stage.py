class Stage(object):
    stage_type = None

    def __init__(self, game):
        self.game = game
        pass

    @classmethod
    def title(cls):
        return None

    def begin(self):
        for player in self.game:
            player.stage_begin(stage_type=self.stage_type)

    def after_begin(self):
        pass

    def can_end(self):
        self.game.next_stage()

    def end(self):
        pass

    def handle_add_player(self, new_player):
        new_player.stage_begin(stage_type=self.stage_type)

    def handle_remove_player(self, player_removed):
        pass