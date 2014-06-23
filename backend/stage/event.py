import math
import random


class EventHandler():
    """The event handler can be in either of two states:
        - processing: whenever the stack depletes, the handler will automatically push the next event (if any) in the queue into the stack
        - idle: it does nothing except wait for the events in the stack to respond

    """

    def __init__(self, delegate):
        self.delegate = delegate
        self._event_queue = []  # queue waiting to be processed (in order)
        self._event_stack = []  # stack of event currently displaying on client (bottom-up)
        self._processing = False

    @property
    def processing(self):
        return self._processing

    def start_processing(self):
        # if not processing, start processing
        if not self.processing:
            self._processing = True
            # push event from queue if event stack is empty
            if not self._event_stack:
                self._push_next_event()

    def stop_processing(self):
        # if processing, stop it
        if self.processing:
            self._processing = False

    def schedule_events(self, events: list, location='last'):
        """Schedule events in the queue at `location`. Note the handler might not be currently processing.

            location = 'immediately' | 'next up' | 'last'

        """

        # hack
        event_queue_was_empty = not self._event_queue

        if location == 'immediately':
            for event in events:
                self._push_event(event)
        elif location == 'next up':
            self._event_queue = events + self._event_queue
        elif location == 'last':
            self._event_queue += events

        # hack: this gets checked every time an event is scheduled
        if self.processing and event_queue_was_empty and (location == 'next up' or location == 'last'):
            self._push_next_event()

    def schedule_event(self, event, **kwargs):
        self.schedule_events([event], **kwargs)

    def event_did_end(self, event):
        assert event in self._event_stack
        # remove from stack
        self._event_stack.remove(event)
        # if stack is now empty, process next event in queue
        if not self._event_stack and self.processing:
            self._push_next_event()

    def _push_next_event(self):
        """Push the next event in the queue into the stack"""

        if self._event_queue:
            # retrieve next event on queue and push into stack
            self._push_event(self._event_queue.pop(0))
        else:
            self.delegate.event_queue_did_empty(self)

    def _push_event(self, event):
        """Push event into stack and evoke it"""

        self._event_stack.append(event)
        event.evoke()


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
        self.delegate = player.event_handler

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
        from backend import server
        server.ioloop.add_callback(self.delegate.event_did_end, self)


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
            }
        ]
        if self.player.inventory['log'] > 0:
            self.responses += [
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
            self.delegate.schedule_event(FacilityRepairEvent(self.player), location='next up')
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
                'id': 'ignore',
                'text': 'Ignore'
            }
        ]
        if self.player.inventory['bullet'] > 0:
            self.responses += [
                {
                    'id': 'shoot',
                    'text': 'Shoot (costs 1 bullet)'
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