from backend import server

import math
import random


class Event():
    """Subclass of an event should implement `handle_response` and specify `title`, `image_name`, `text`, and `responses`

    """

    def __init__(self, player):
        self.title = ''
        self.image_name = ''
        self.text = ''
        self.responses = []
        self.player = player
        self.facility = player.current_job
        self.game = player.current_game

    def should_happen(self):
        """override to use to decide if event happens (e.g. based on some risk or condition)"""
        return True

    def evoke(self):
        if self.should_happen():
            self.player.display_event(title=self.title, image_name=self.image_name, text=self.text, responses=self.responses, callback=self.handle_response)
        else:
            self.end()

    def handle_response(self, response_chosen_id):
        self.end()

    def end(self):
        server.ioloop.add_callback(self.player.event_did_end, self)


class DismissibleEvent(Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responses += [
            {
                'id': 'dismiss',
                'display': 'background'
            }
        ]

    def handle_response(self, response_chosen_id):
        if response_chosen_id == 'dismiss':
            pass
        super().handle_response(response_chosen_id)


class MessageEvent(DismissibleEvent):

    def __init__(self, title="", text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.text = text


class FacilityRepairEvent(Event):

    def __init__(self, player):
        super().__init__(player)

        self.text = 'The %s is looking %s. ' % (self.player.current_job, self.describe(self.game.facility_condition[self.facility]))
        self.responses += [
            {
                'id': 'okay',
                'text': 'Okay'
            },
            {
                'id': 'repair',
                'text': 'Repair (costs 1 log)'
            }
        ]

    def handle_response(self, response_chosen_id):
        if response_chosen_id == 'repair':
            # client will need to check if enough log, maybe grey out option otherwise
            assert self.player.inventory['log'] > 0
            self.player.inventory['log'] -= 1
            # hack
            self.player.inventory = self.player.inventory

            # repair facility
            self.player.current_game.repair(self.facility)

            # insert another repair event into player event queue
            self.player.schedule_event(FacilityRepairEvent(self.player), immediately=True)
        elif response_chosen_id == 'ignore':
            # nothing happens
            pass

        super().handle_response(response_chosen_id)

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


class ResourceHarvestEvent(DismissibleEvent):

    def __init__(self, player):
        super().__init__(player)

        resource = self.player.current_game.resource_with_job(self.facility)

        # calculate resource yield
        condition = self.player.current_game.facility_condition[self.facility]
        resource_yield = math.ceil(condition * self.game.RESOURCE_HARVEST_YIELD_AT_FULL_CONDITION)

        # configure message
        self.text = 'You received %d more %s. ' % (resource_yield, resource)

        # give player resource
        self.player.inventory[resource] += resource_yield
        # hack
        self.player.inventory = self.player.inventory


class AnimalAttackEvent(Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "A wild animal attacked!"
        self.image_name = 'assets/owlbear.jpeg'
        self.text = 'What are you going to doooo!?'
        self.responses = [
            {
                'id': 'shoot',
                'text': 'Shoot (costs 1 bullet)'
            },
            {
                'id': 'ignore',
                'text': 'Ignore'
            }
        ]

    def should_happen(self):
        condition = self.player.current_game.facility_condition[self.facility]
        risk = self.game.MAX_ANIMAL_ATTACK_RISK * (1 - condition) if self.facility != 'watchtower' else 1.0
        return random.random() < risk

    def handle_response(self, response_chosen_id):
        if response_chosen_id == 'shoot':
            # client will need to check if enough bullets, maybe grey out option otherwise
            assert self.player.inventory['bullet'] > 0
            self.player.inventory['bullet'] -= 1
            # hack
            self.player.inventory = self.player.inventory
        elif response_chosen_id == 'ignore':
            # damage the facility the player is currently at
            self.player.current_game.damage(self.player.current_job, type='animal attack')
            # damage player health
            new_health = max(self.player.condition['health'] - self.game.ANIMAL_ATTACK_HEALTH_DAMAGE, 0.0)
            self.player.condition['health'] = new_health
            # hack
            self.player.condition = self.player.condition

        super().handle_response(response_chosen_id)