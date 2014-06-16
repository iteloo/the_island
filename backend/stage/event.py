class Event():
    """Subclass of an event should implement `handle_response` and specify `title`, `image_name`, `text`, and `responses`

    """

    def __init__(self, player):
        self.title = ""
        self.image_name = ""
        self.text = ""
        self.responses = []
        self.player = ""

    def handle_response(self, response_chosen_id):
        self.player.next_event()

    def evoke(self):
        self.player.display_event(title=self.title, image_name=self.image_name, text=self.text, responses=self.responses, callback=self.handle_response)

class AnimalAttackEvent(Event):

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

        self.title = "A wild animal attacked!"
        self.image_name = 'assets/owlbear.png'
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

    def handle_response(self, response_chosen_id):
        if response_chosen_id is 'shoot':
            # client will need to check if enough bullets, maybe grey out option otherwise
            assert self.player.inventory['bullet'] > 0
            self.player.inventory['bullet'] -= 1
        elif response_chosen_id is 'ignore':
            self.game.damage('watchtower')

        super(AnimalAttackEvent, self).handle_response(response_chosen_id)