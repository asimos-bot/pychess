import unittest
from game_board_controller import GameBoardController
from piece import PieceCode, PieceColor


class PieceInitialMovementTest(unittest.TestCase):
    def setUp(self):
        self.controller = GameBoardController()
        self.controller.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

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
        legal_moves = self.controller.get_legal_moves(pos)
        self.assertEqual(
                legal_moves,
                expected_moves,
                "illegal movement set for {} {} at {}"
                .format(
                    piece_color.name.lower(),
                    piece_type.name.lower(),
                    pos))

    def test_initial_white_pawns(self):
        for i in range(8):
            self.movement_check(
                    (6, i),
                    PieceCode.PAWN,
                    PieceColor.WHITE,
                    {(5, i), (4, i)})

    def test_initial_black_pawns(self):
        self.controller.finish_turn()
        for i in range(8):
            self.movement_check(
                    (1, i),
                    PieceCode.PAWN,
                    PieceColor.BLACK,
                    {(2, i), (3, i)})

    def test_initial_white_rook(self):
        self.movement_check(
                (7, 0),
                PieceCode.ROOK,
                PieceColor.WHITE,
                set())
        self.movement_check(
                (7, 7),
                PieceCode.ROOK,
                PieceColor.WHITE,
                set())

    def test_initial_black_rook(self):
        self.controller.finish_turn()
        self.movement_check(
                (0, 0),
                PieceCode.ROOK,
                PieceColor.BLACK,
                set())
        self.movement_check(
                (0, 7),
                PieceCode.ROOK,
                PieceColor.BLACK,
                set())

    def test_initial_white_knights(self):
        self.movement_check(
                (7, 1),
                PieceCode.KNIGHT,
                PieceColor.WHITE,
                {(5, 0), (5, 2)})
        self.movement_check(
                (7, 6),
                PieceCode.KNIGHT,
                PieceColor.WHITE,
                {(5, 5), (5, 7)})

    def test_initial_black_knights(self):
        self.controller.finish_turn()
        self.movement_check(
                (0, 1),
                PieceCode.KNIGHT,
                PieceColor.BLACK,
                {(2, 0), (2, 2)})
        self.movement_check(
                (0, 6),
                PieceCode.KNIGHT,
                PieceColor.BLACK,
                {(2, 5), (2, 7)})

    def test_initial_white_bishop(self):
        self.movement_check(
                (7, 2),
                PieceCode.BISHOP,
                PieceColor.WHITE,
                set())
        self.movement_check(
                (7, 5),
                PieceCode.BISHOP,
                PieceColor.WHITE,
                set())

    def test_initial_black_bishop(self):
        self.controller.finish_turn()
        self.movement_check(
                (0, 2),
                PieceCode.BISHOP,
                PieceColor.BLACK,
                set())
        self.movement_check(
                (0, 5),
                PieceCode.BISHOP,
                PieceColor.BLACK,
                set())

    def test_intial_white_queen(self):
        self.movement_check(
                (7, 3),
                PieceCode.QUEEN,
                PieceColor.WHITE,
                set())

    def test_intial_black_queen(self):
        self.controller.finish_turn()
        self.movement_check(
                (0, 3),
                PieceCode.QUEEN,
                PieceColor.BLACK,
                set())

    def test_intial_white_king(self):
        self.movement_check(
                (7, 4),
                PieceCode.KING,
                PieceColor.WHITE,
                set())

    def test_intial_black_king(self):
        self.controller.finish_turn()
        self.movement_check(
                (0, 4),
                PieceCode.KING,
                PieceColor.BLACK,
                set())


if __name__ == "__main__":
    unittest.main()
