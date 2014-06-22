from backend.stage import ready_stage
from backend.stage import event


class DayStage(ready_stage.ReadyStage):
    stage_type = 'Day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def after_begin(self):
        # damage facilities
        for facility in self.game.jobs:
            self.game.damage(facility, type='natural')

        # load and invoke events
        self.load_events()
        for p in self.game.players:
            p.next_event()

    ### event management

    def load_events(self):
        # determine sequence of events for each player, and load the sequence
        for player in self.game.players:
            # facility repair + possible animal attack
            player.event_queue += [event.FacilityRepairEvent(player), event.AnimalAttackEvent(player)]
            # todo: job related action
            # harvest + possible animal attack
            player.event_queue += [event.ResourceHarvestEvent(player), event.AnimalAttackEvent(player)]





