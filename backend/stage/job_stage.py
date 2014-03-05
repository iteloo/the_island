from backend.stage import ready_stage
from backend import message
from backend import helpers


class JobStage(ready_stage.ReadyStage):
    stage_type = 'Job'

    def __init__(self, game) -> None:
        super().__init__(game)
        self._job_selected = {}  # job selected indexed by player

    @classmethod
    def title(cls) -> str:
        return "Select your Job"

    ### stage event handling ###

    def end(self):
        super().end()
        # update player jobs
        for player in self.game.players:
            # the client is responsible for checking that player has a job selected when clicking ready
            assert player in self._job_selected
            player.current_job = self._job_selected[player]

    ### action handling ###

    def job_selected(self, sender, job: str) -> None:
        if job is None:
            # handle deselection
            self._job_selected.pop(sender, None)
        else:
            if job in self.game.jobs:
                # change/add job selections
                self._job_selected[sender] = job
            else:
                raise message.InvalidArgumentError
        # notify all players of change
        self._update_job_selections_to_all()

    ### convenience ###

    @property
    def _job_selections_id(self):
        """Return dictionary of player ids indexed by jobs"""

        return dict((j, [p.id for p in players]) for j, players in helpers.invert(self._job_selected, codomain=self.game.jobs).items())

    def _update_job_selections_to_all(self) -> None:
        for player in self.game.players:
            player.update_job_selections(job_selections=self._job_selections_id)

    ### player handling ###

    def handle_add_player(self, new_player) -> None:
        super().handle_add_player(new_player)
        # update new player's job selection
        new_player.update_job_selections(job_selections=self._job_selections_id)

    def handle_remove_player(self, player_removed) -> None:
        super().handle_remove_player(player_removed)
        # remove player from job selections
        self._job_selected.pop(player_removed, None)
        # update everyone else's job selection data
        self._update_job_selections_to_all()




