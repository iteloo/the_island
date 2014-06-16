from backend.stage import ready_stage

import time
import collections


class TradingStage(ready_stage.ReadyStage):
    stage_type = 'Trading'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_recorded_proposal = None

    ### trading action handling

    def trade_proposed(self, sender, items: dict, callback: collections.Callable) -> None:

        # create new trade proposal
        new_proposal = TradeProposal(sender, items, callback)

        # if there is already a recorded proposal with similar time, then facilitate trading
        if self._last_recorded_proposal and new_proposal.close_to(self._last_recorded_proposal):
            # send items to respective players through callback
            new_proposal.callback(items=self._last_recorded_proposal.items)
            self._last_recorded_proposal.callback(items=new_proposal.items)

            # update inventory (will result in call to update in client, which must come AFTER invoking callback to proposed trade
            new_proposal.player.subtractInventory(new_proposal.items)
            new_proposal.player.addInventory(self._last_recorded_proposal.items)
            self._last_recorded_proposal.player.subtractInventory(self._last_recorded_proposal.items)
            self._last_recorded_proposal.player.addInventory(new_proposal.items)

        # otherwise, record as first
        else:
            print("Trade proposed by %s." % new_proposal.player)
            self._last_recorded_proposal = new_proposal


class TradeProposal(object):
    def __init__(self, player, items: dict, callback: collections.Callable) -> None:
        self.player = player
        self.time = int(round(time.time() * 1000))
        self.items = items
        self.callback = callback

    def close_to(self, other) -> bool:
        return abs(self.time - other.time) < 100
