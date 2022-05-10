import unittest
from game_board_controller import GameBoardController
from piece import PieceCode, PieceColor


class PieceFreeMovementTest(unittest.TestCase):
    def setUp(self):
        self.controller = GameBoardController()

    def movement_check(
            self,
            pos,
            expected_type: PieceCode,
            expected_color: PieceColor,
            expected_moves):

        piece_info = self.controller.piece_info(pos)
        if piece_info is None:
            self.assertFalse(
                piece_info is None,
                "invalid piece position given to be checked: None encountered")

        piece_type, piece_color = self.controller.piece_info(pos)
        self.assertEqual(
                piece_type,
                expected_type,
                "expected {}, got {}".format(
                    expected_type.name.lower(),
                    piece_type.name.lower()))
        self.assertEqual(
                piece_color,
                expected_color,
                "expected {} {}, but this one is {}".format(
                    expected_color.name.lower(),
                    expected_type.name.lower(),
                    piece_color.name.lower()))
        valid_moves = self.controller.get_valid_moves(pos)
        self.assertEqual(
                valid_moves,
                expected_moves,
                "illegal movement set for {} {} at {}"
                .format(
                    piece_color.name.lower(),
                    piece_type.name.lower(),
                    pos))


if __name__ == "__main__":
    unittest.main()
