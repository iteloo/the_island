from . import helpers


class Game(object):
    """The game logic

    The game is made up of independent stages, which are subclasses of `Stage`. The upcoming stages is kept in a list. The game then go through the stages in the list sequentially - instantiating, maintaining, and killing each stage when appropriate.

    The game object is also responsible for keeping game-wide state variables, such as a list of players and their current jobs.

    A detailed description for the lifecycle of each stage can be found in the `Stage` documentations.


    Attributes:
        Game.players: a list of `Player` objects representing players in the game

        Game.stage_queue: a list of upcoming stage classes

        Game.current_stage: the current stage instance

    """

    resources = ['log', 'food', 'bandage', 'bullet']
    jobs = ['production', 'farm', 'hospital', 'watchtower']

    def __init__(self):
        self.players = []

        # stage management variables
        self.stage_queue = []
        self.current_stage = None

        # start the first stage
        # self.next_stage()

    ### stage management ###

    def next_stage(self):

        # hack: keeping track of title stages
        ending_notification_stage = False

        # end current stage if it exists
        if self.current_stage:

            # if end a title stage
            # if self.current_stage.__class__ is notification.NotificationStage:
            #     ending_notification_stage = True

            # clean up stage
            self.current_stage.end()

        # retrieve new stage
        try:
            next_stage = self.stage_queue.pop(0)
        except IndexError:
            self.current_stage = None
            return

        # initialize empty parameter dictionary
        params = {}

        # if the next stage requires a title screen, and we haven't already displayed it, then display it
        if next_stage.title() and not ending_notification_stage:
            # push stage back up
            self.stage_queue.insert(0, next_stage)
            # display title screen instead
            params = {'title': next_stage.title()}
            # next_stage = notification.NotificationStage

        # instantiate stage object
        self.current_stage = next_stage(self, **params)

        # begin new stage
        self.current_stage.begin()
        # hack?: run after_begin
        self.current_stage.after_begin()

    ### convenience ###

    def players_with_job(self, job):
        return [p for p in self.players if p.currentJob == job]

    def resource_with_job(self, job):
        return dict(list(zip(self.jobs, self.resources)))[job]

    ### player management methods ###

    def add_player(self, new_player):
        self.players.append(new_player)

        # logging
        helpers.print_header("==> %s joined" % new_player)
        # tell current stage to modify any data
        # self.current_stage.handle_add_player(newPlayer)

        # notify all players that player count has increased
        for player in self.players:
            player.update_game_info(player_count=len(self.players))

        # todo: handle global state changes!

    def remove_player(self, player):
        # remove players from self.players
        self.players.remove(player)

        # logging
        helpers.print_header("==> %s left" % player)

        # tell current stage to modify any data
        # self.current_stage.handle_remove_player(player)

        # notify all players that player count has decreased
        for player in self.players:
            player.update_game_info(player_count=len(self.players))

        # todo: handle global state changes!