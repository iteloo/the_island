from backend.stage import ready_stage
from backend.stage import event


class DayStage(ready_stage.ReadyStage):
    stage_type = 'Day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # damage facilities
        for facility in self.game.jobs:
            self.game.damage(facility, type='natural')

    def after_begin(self, sender):
        # load and invoke events
        self.load_events(sender)
        sender.next_event()

    ### event management

    def load_events(self, player):
        # determine sequence of events for each player, and load the sequence
        # facility repair + possible animal attack
        player.event_queue += [event.FacilityRepairEvent(player), event.AnimalAttackEvent(player)]
        # todo: job related action
        # harvest + possible animal attack
        player.event_queue += [event.ResourceHarvestEvent(player), event.AnimalAttackEvent(player)]





