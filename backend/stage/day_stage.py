from backend.stage import ready_stage
from backend.stage import event


class DayStage(ready_stage.ReadyStage):
    stage_type = 'Day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # damage facilities
        for facility in self.game.jobs:
            self.game.damage(facility, type='natural')

    def after_client_setup(self, sender):
        # determine sequence of events for each sender, and load the sequence

        # facility repair + possible animal attack
        events = [event.FacilityRepairEvent(sender), event.AnimalAttackEvent(sender)]
        # todo: job related action
        # harvest + possible animal attack
        events += [event.ResourceHarvestEvent(sender), event.AnimalAttackEvent(sender)]

        # start the queue after scheduling all the events
        sender.event_handler.schedule_events(events)
        sender.event_handler.start_processing()

    # todo: day stage needs to handle stashing; this may require additional logic pertaining to when the player is stashed