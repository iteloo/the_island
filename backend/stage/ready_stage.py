from backend.stage import stage


class ReadyStage(stage.Stage):
    stage_type = 'Ready'

    def __init__(self, game):
        super().__init__(game)
        self._ready_list = []

    ### method handling ###

    def ready(self, sender) -> None:
        if sender is not None:
            # add sender to ready_list
            self._ready_list.append(sender)
            # if all players are ready, move the to the next stage
            if all([p in self._ready_list for p in self.game.players]):
                self.can_end()