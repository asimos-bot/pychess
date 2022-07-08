import unittest
from piece import PieceColor
from game_board_controller import GameBoardController


class FinishTurnTest(unittest.TestCase):

    def setUp(self):
        self.gb = GameBoardController()

    def test_end_white_turn(self):
        self.gb._turn = PieceColor.WHITE
        self.gb.fullmoves = 1
        self.gb.halfmoves = 2
        self.gb.finish_turn()
        self.assertEqual(self.gb.fullmoves, 1)
        self.assertEqual(self.gb.halfmoves, 3)
        self.assertEqual(self.gb._turn, PieceColor.BLACK)

    def test_end_black_turn(self):
        self.gb._turn = PieceColor.BLACK
        self.gb.fullmoves = 1
        self.gb.halfmoves = 2
        self.gb.finish_turn()
        self.assertEqual(self.gb.fullmoves, 2)
        self.assertEqual(self.gb.halfmoves, 3)
        self.assertEqual(self.gb._turn, PieceColor.WHITE)

    if __name__ == "__main__":
        unittest.main()
