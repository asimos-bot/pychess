import unittest
from unittest.mock import MagicMock
from piece import PieceColor, Rook
from game_board_controller import GameBoardController
from piece import PieceCode


class MovePiecesTest(unittest.TestCase):

    def setUp(self):
        self.gb = GameBoardController()
        self.gb.pieces = []
        self.gb.promote = MagicMock()
        self.gb.update_pseudo_legal_moves = MagicMock()
        self.gb.process_move_notification = MagicMock()
        self.gb.opposite_color = MagicMock(return_value=PieceColor.WHITE)
        self.gb.pieces_by_color = {
            PieceColor.WHITE: set(), PieceColor.BLACK: set()}
        for i in range(8):
            line = []
            for j in range(8):
                line.append(None)
            self.gb.pieces.append(line)
        self.r1 = Rook(PieceColor.BLACK, (7, 0))
        self.r1.notify_move = MagicMock(return_value=(None, None))
        self.gb.pieces_by_color[PieceColor.BLACK].add((7, 0))
        self.r2 = Rook(PieceColor.BLACK, (7, 7))
        self.r2.notify_move = MagicMock(return_value=(None, None))
        self.gb.pieces_by_color[PieceColor.BLACK].add((7, 7))
        self.gb.pieces[7][7] = self.r2
        self.gb.pieces[7][0] = self.r1

    def test_move(self):
        self.gb.move_piece((7,7),(7,3),None)
        self.assertIsNone(self.gb.pieces[7][7])
        self.assertEqual(self.gb.pieces[7][3], self.r2)
        self.assertNotIn((7,7), self.gb.pieces_by_color[PieceColor.BLACK])
        self.assertIn((7,3), self.gb.pieces_by_color[PieceColor.BLACK])

    if __name__ == "__main__":
        unittest.main()
