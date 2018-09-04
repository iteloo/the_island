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
        proposal1 = TradeProposal(sender, items, callback)
        # get previous proposal
        proposal2 = self._last_recorded_proposal

        # if there is already a recorded proposal with similar time, then facilitate trading
        if proposal2 and proposal1.close_to(proposal2):
            # send items to respective players through callback
            proposal1.callback(items=proposal2.items)
            proposal2.callback(items=proposal1.items)

            # update inventories (will result in call to update in client, which must come AFTER invoking callback to proposed trade)
            for i, count in proposal1.items.items():
                proposal1.player.inventory[i] -= count
                proposal2.player.inventory[i] += count
            for i, count in proposal2.items.items():
                proposal2.player.inventory[i] -= count
                proposal1.player.inventory[i] += count

        # otherwise, record as first
        else:
            print("Trade proposed by %s." % proposal1.player)
            self._last_recorded_proposal = proposal1


class TradeProposal(object):
    def __init__(self, player, items: dict, callback: collections.Callable) -> None:
        self.player = player
        self.time = int(round(time.time() * 1000))
        self.items = items
        self.callback = callback

    def close_to(self, other) -> bool:
        return abs(self.time - other.time) < 100
