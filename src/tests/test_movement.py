import unittest
from game_board_controller import GameBoardController


class PieceMovementTest(unittest.TestCase):
    def setUp(self):
        self.controller = GameBoardController()

    def movement_check(self, pos, expected):
        piece_info = self.controller.piece_info(pos)
        if piece_info is None:
            self.assertFalse(
                piece_info is None,
                "invalid piece position given to be checked: None encountered")

        piece_type, piece_color = self.controller.piece_info(pos)
        valid_moves = self.controller.get_valid_moves(pos)
        self.assertEqual(
                valid_moves,
                expected,
                "illegal movement set for {} {} at {}"
                .format(
                    piece_color.name.lower(),
                    piece_type.name.lower(),
                    pos))

    def test_initial_white_pawns(self):
        for i in range(8):
            self.movement_check((6, i), {(6, i), (4, i)})


if __name__ == "__main__":
    unittest.main()
