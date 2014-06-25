from backend import message

import math
import random
import functools


class EventHandler():
    """The event handler can be in either of two states:
        - processing: whenever the stack depletes, the handler will automatically push the next event (if any, inputs=None) in the queue into the stack
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

    def schedule_event(self, event, location='last'):
        self.schedule_events([event], location)

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

    def __init__(self, player, callback=None):
        """If a callback is specified it must accept two arguments: response_chosen_id and inputs"""

        self.title = ''
        self.image_name = ''
        self.text = ''
        self.responses = []
        self.inputs = []
        self.player = player
        self.delegate = player.event_handler
        self.callback = callback

    def should_happen(self):
        """override to use to decide if event happens (e.g. based on some risk or condition)"""
        return True

    def evoke(self):
        if self.should_happen():
            self.player.display_event(title=self.title, image_name=self.image_name, text=self.text, responses=self.responses, inputs=self.inputs, callback=self.handle_response)
        else:
            self.end()

    def handle_response(self, response_chosen_id, inputs=None):
        # invoke callback, if any
        if self.callback is not None:
            from backend import server
            server.ioloop.add_callback(self.callback, response_chosen_id=response_chosen_id, inputs=inputs)
        # terminate
        self.end()

    def end(self):
        from backend import server
        server.ioloop.add_callback(self.delegate.event_did_end, self)


#### menu events ####

class MainMenuEvent(Event):

    def __init__(self, player):
        super().__init__(player)
        self.title = 'Main Menu'
        self.responses = [
            {
                'id': 'new',
                'text': 'New Game'
            },
            {
                'id': 'join',
                'text': 'Join Game'
            }
        ]

    def handle_response(self, response_chosen_id, inputs=None):
        from backend import game_controller

        if response_chosen_id == 'new':
            # create and join new game
            game_controller.universal_controller.new_game(self.player)
        elif response_chosen_id == 'join':
            # todo: how to implement 'back' feature?
            self.delegate.schedule_event(JoinMenuEvent(self.player), location='immediately')

        super().handle_response(response_chosen_id, inputs=None)


class JoinMenuEvent(Event):
    def __init__(self, player):
        super().__init__(player)
        self.title = 'Join Game'
        self.text = 'Whose game would you like to join?'
        self.responses = [
            {
                'id': 'join',
                'text': 'Join Game'
            }
        ]
        self.inputs = [
            {
                'id': 'owner_id',
                'type': 'textbox'
            }
        ]

    def handle_response(self, response_chosen_id, inputs=None):
        assert response_chosen_id == 'join'
        try:
            owner_id = inputs['owner_id']
        except (AttributeError, KeyError):
            # todo: adopt new exception handling mechanism
            raise message.InvalidArgumentError

        from backend import game_controller
        owner = game_controller.universal_controller.player_with_id(owner_id)
        success = game_controller.universal_controller.join_game(owner, self.player)
        # todo: client should wait for server's permission before dismissing a message (so that the server need not resend the event if something's wrong)
        # if game with matching name not found, display this message again
        if not success:
            self.delegate.schedule_events(
                [JoinMenuEvent(self.player), NotificationEvent(self.player, title='Game not found', text='Try again')],
                location='immediately'
            )

        super().handle_response(response_chosen_id, inputs=None)


#### general events ####

class DismissibleEvent(Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responses += [
            {
                'id': 'dismiss',
                'display': 'background'
            }
        ]

    def handle_response(self, response_chosen_id, inputs=None):
        if response_chosen_id == 'dismiss':
            pass
        super().handle_response(response_chosen_id, inputs=None)


class NotificationEvent(DismissibleEvent):

    def __init__(self, player, title="", text="", *args, on_dismiss=None, **kwargs):
        super().__init__(player, *args, **kwargs)
        self.title = title
        self.text = text

        # replace standard callback with on_dismiss
        if on_dismiss:
            @functools.wraps(on_dismiss)
            def wrapped_on_dismiss(*args, **kwargs):
                on_dismiss()
            self.callback = wrapped_on_dismiss


#### game events ####

class GameEvent(Event):

    def __init__(self, player):
        super().__init__(player)
        self.facility = player.current_job
        self.game = player.current_game


class FacilityRepairEvent(GameEvent):

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

    def handle_response(self, response_chosen_id, inputs=None):
        if response_chosen_id == 'repair':
            # client will need to check if enough log, maybe grey out option otherwise
            assert self.player.inventory['log'] > 0
            self.player.subtract_inventory(log=1)

            # repair facility
            self.player.current_game.repair(self.facility)

            # insert another repair event into player event queue
            self.delegate.schedule_event(FacilityRepairEvent(self.player), location='next up')
        elif response_chosen_id == 'ignore':
            # nothing happens
            pass

        super().handle_response(response_chosen_id, inputs=None)

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


class ResourceHarvestEvent(GameEvent, DismissibleEvent):

    def __init__(self, player):
        super().__init__(player)

        resource = self.player.current_game.resource_with_job(self.facility)

        # calculate resource yield
        condition = self.player.current_game.facility_condition[self.facility]
        resource_yield = math.ceil(condition * self.game.RESOURCE_HARVEST_YIELD_AT_FULL_CONDITION)

        # configure message
        self.text = 'You received %d more %s. ' % (resource_yield, resource)

        # give player resource
        self.player.add_inventory(**{resource: resource_yield})


class AnimalAttackEvent(GameEvent):

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

    def handle_response(self, response_chosen_id, inputs=None):
        if response_chosen_id == 'shoot':
            # client will need to check if enough bullets, maybe grey out option otherwise
            assert self.player.inventory['bullet'] > 0
            self.player.add_inventory(bullet=-1)
        elif response_chosen_id == 'ignore':
            # damage the facility the player is currently at
            self.player.current_game.damage(self.player.current_job, type='animal attack')
            # damage player health
            self.player.add_condition(health=-self.game.ANIMAL_ATTACK_HEALTH_DAMAGE)

        super().handle_response(response_chosen_id, inputs=None)