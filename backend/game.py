from backend import helpers
from backend.stage import job_stage
from backend.stage import day_stage
from backend.stage import trading_stage
from backend import observed_collection
from backend import facility


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

    DEFAULT_HEALTH_DAMAGE = 5.0
    ANIMAL_ATTACK_HEALTH_DAMAGE = 35.0
    RESOURCE_HARVEST_YIELD_AT_FULL_CONDITION = 3
    MAX_ANIMAL_ATTACK_RISK = 1.0

    def __init__(self, owner, delegate):
        self.owner = owner
        self._delegate = delegate
        self._players = observed_collection.ObservedList()
        self._players.add_observer(observer=self, callback=self.players_list_updated)
        self._stashed_players = []

        # stage management variables
        self.stage_queue = 3 * [job_stage.JobStage, day_stage.DayStage, trading_stage.TradingStage]
        self.current_stage = None

        # game state management variables
        self.facilities = dict((f.name, f()) for f in [
            facility.Production,
            facility.Farm,
            facility.Hospital,
            facility.Watchtower]
        )

    def __str__(self):
        return "%s's game" % self.owner

    ### main logic / stage management ###

    def begin(self):
        # todo: add more refined game state handling
        # load first stage
        self.next_stage()
        # notify delegate
        self._delegate.game_did_begin(self)

    def end(self):
        # notify all players, and refresh browser when they dismiss the message
        for p in self.players:
            p.notify(title='The game ended', text='since the owner of the game left', on_dismiss=p.refresh)
        # notify delegate
        self._delegate.game_did_end(self)

    def stage_can_end(self, stage):
        assert self.current_stage is stage
        self.next_stage()

    def next_stage(self):

        # hack: keeping track of title stages
        # ending_notification_stage = False

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
        # if next_stage.title() and not ending_notification_stage:
        #     # push stage back up
        #     self.stage_queue.insert(0, next_stage)
        #     # display title screen instead
        #     params = {'title': next_stage.title()}
        #     # next_stage = notification.NotificationStage

        # instantiate stage object
        self.current_stage = next_stage(self, **params)

        # begin new stage
        self.current_stage.begin()

    ### player management ###

    @property
    def players(self):
        return self._players.copy()

    def players_list_updated(self, data, update_type):
        # notify all players that player count has changed
        for p in self.players:
            p.update_game_info(player_count=len(self.players))

    def add_player(self, new_player):
        self._players.append(new_player)

        # logging
        helpers.print_header("==> %s joined" % new_player)

        # tell current stage to modify any data
        if self.current_stage:
            self.current_stage.handle_add_player(new_player)

    def remove_player(self, player):
        # remove players from self.players
        self._players.remove(player)

        # logging
        helpers.print_header("==> %s left" % player)

        # tell current stage to modify any data
        if self.current_stage:
            self.current_stage.handle_remove_player(player)

        # if the owner left, game should terminate itself
        if player is self.owner:
            self.end()

    def stash_player(self, player):
        # todo: finish implementing this
        assert player in self.players and player not in self._stashed_players

        # notify player
        player.will_be_stashed(self)

        # modify data
        self._players.remove(player)
        self._stashed_players.append(player)

        # tell current stage to modify any data
        if self.current_stage:
            self.current_stage.handle_stash_player(player)

        # logging
        helpers.print_header("==> %s is stashed" % player)

    def unstash_player(self, player):
        # todo: finish implementing this
        assert player in self._stashed_players and player not in self.players

        # notify player
        player.will_be_unstashed(self)

        # modify data
        self._stashed_players.remove(player)
        self._players.append(player)

        # tell current stage to modify any data
        if self.current_stage:
            self.current_stage.handle_unstash_player(player)

        # logging
        helpers.print_header("==> %s is unstashed" % player)
