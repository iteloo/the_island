from backend.stage.job_stage import JobStage
from backend.game import Game

from unittest import TestCase
from unittest.mock import Mock, patch


class TestJobStage(TestCase):

    def setUp(self):
        pass

    def test_end(self):
        pass

    def test_job_selected(self):
        pass

    def test_ready_true(self):
        """`ready` should call `can_end` if all players are ready"""

        mock_player = Mock()
        mock_stage = Mock()
        mock_stage._ready_list = []
        mock_stage.game.players = [mock_player]

        JobStage.ready(mock_stage, mock_player)
        mock_stage.can_end.assert_called_once_with()

    def test_ready_false(self):
        """`ready` should not call `can_end` if not all players are ready"""

        mock_player = Mock()
        mock_stage = Mock()
        mock_stage._ready_list = []
        mock_stage.game.players = [mock_player, Mock()]

        JobStage.ready(mock_stage, mock_player)
        self.assertFalse(mock_stage.can_end.called)

    def test__job_selections(self):
        pass

    def test__update_job_selections_to_all(self):
        pass

    def test_handle_add_player(self):
        pass

    def test_handle_remove_player(self):
        pass