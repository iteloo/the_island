from backend.stage import ready_stage
from backend.stage import event
from backend import facility


class DayStage(ready_stage.ReadyStage):
    stage_type = 'Day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # vars for keeping track of boat builders
        self._players_who_invested_in_boat = []

        # damage facilities
        for f in self.game.facilities.values():
            f.damage(damage_type='natural')

    def after_client_setup(self, sender):
        # determine sequence of events for each sender, and load the sequence

        # facility repair + possible animal attack
        events = [event.FacilityRepairEvent(sender), event.AnimalAttackEvent(sender)]
        # boat building event for players in production
        if isinstance(sender.current_facility, facility.Production):
            events.append(event.BoatBuildingEvent(sender))
        # harvest + possible animal attack
        events += [event.ResourceHarvestEvent(sender), event.AnimalAttackEvent(sender)]

        # start the queue after scheduling all the events
        sender.event_handler.schedule_events(events)
        sender.event_handler.start_processing()

    def invest_in_boat(self, player):
        # add to list of investors
        self._players_who_invested_in_boat.append(player)
        # if all players in production invested, they can leave
        if all([p in self._players_who_invested_in_boat for p in self.game.facilities[facility.Production.name].players]):
            for p in self._players_who_invested_in_boat:
                # on dismiss, the browser will refresh
                p.event_handler.schedule_event(event.BoatSuccessEvent(p), location='immediately')

    # todo: day stage needs to handle stashing; this may require additional logic pertaining to when the player is stashed