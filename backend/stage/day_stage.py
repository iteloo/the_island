from backend.stage import ready_stage
from backend.stage import event

import math
import random


class DayStage(ready_stage.ReadyStage):
    stage_type = 'Day'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load and invoke events
        self.load_events()
        
        # start events
        for p in self.game.players:
            p.next_event()

    ### event management

    def load_events(self):
        # determine sequence of events for each player, and load the sequence
        # todo: incomplete
        for player in self.game.players_with_job('watchtower'):
            player.event_queue.append(AnimalAttackEvent(player))

    #### helpers ####

    @staticmethod
    def describe(condition: float) -> str:
        """Describes a number between 0 and 1 using some funny words

        A big number is interpreted as a good thing, and small bad.

        """

        assert 0 <= condition <= 1

        if condition == 1:
            condition = .999

        small_adverbs = ['a little bit', 'fairly', 'somewhat', 'mildly']
        big_adverbs = ['very', 'extremely', 'horrifyingly']

        good_adjectives = ['shiny', 'amazing', 'clean', 'well-kept', 'normal']
        medium_adjectives = ['bad', 'broken', 'smelly', 'rusty', 'windy']
        bad_adjectives = ['dilapidated', 'gross', 'infected', 'dangerous', 'terrible']

        adverbs = [small_adverbs, big_adverbs]
        adjectives = [bad_adjectives, medium_adjectives, good_adjectives]

        # It has six levels of detail, so we need to get the value from 0-5:
        number = int(math.floor(condition * 6.0))

        if number > 4:
            return random.choice(adverbs[number % 2]) + ' ' + random.choice(good_adjectives)
        else:
            return random.choice(adverbs[1 - (number % 2)]) + ' ' + random.choice(
                adjectives[int(math.floor(number / 3.0))])
