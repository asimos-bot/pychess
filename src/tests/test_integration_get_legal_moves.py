import unittest
from unittest.mock import MagicMock

from game_board_controller import GameBoardController
from piece import King, PieceCode, PieceColor, Rook


class IntegrationGetLegalMovesTest(unittest.TestCase):
    def setUp(self):
        self.gb = GameBoardController()
        self.gb.fen = "8/8/8/2KR2r1/8/8/8/8 w - - 0 1"

    def test_check_block(self):
        r = self.gb.get_legal_moves((3, 3))
        self.assertSetEqual(r, {(3, 4), (3, 5), (3, 6)})
