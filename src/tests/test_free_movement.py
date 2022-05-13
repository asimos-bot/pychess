import unittest
from game_board_controller import GameBoardController
from piece import PieceCode, PieceColor


class PieceFreeMovementTest(unittest.TestCase):
    def setUp(self):
        self.controller = GameBoardController()

    def movement_check(
            self,
            label,
            pos,
            expected_type: PieceCode,
            expected_color: PieceColor,
            expected_moves):

        piece_info = self.controller.piece_info(pos)
        if piece_info is None:
            self.assertFalse(
                piece_info is None,
                "\n{}:\n\t".format(label) +
                "invalid piece position given to be checked: None encountered")

        piece_type, piece_color = self.controller.piece_info(pos)
        self.assertEqual(
                piece_type,
                expected_type,
                "\n{}:\n\t".format(label) +
                "expected {}, got {}".format(
                    expected_type.name.lower(),
                    piece_type.name.lower()))
        self.assertEqual(
                piece_color,
                expected_color,
                "\n{}:\n\t".format(label) +
                "expected {} {}, but this one is {}".format(
                    expected_color.name.lower(),
                    expected_type.name.lower(),
                    piece_color.name.lower()))
        valid_moves = self.controller.get_valid_moves(pos)
        self.assertEqual(
                valid_moves,
                expected_moves,
                "\n{}:\n\t".format(label) +
                "illegal movement set for {} {} at {}:\n".format(
                    piece_color.name.lower(),
                    piece_type.name.lower(),
                    pos) +
                "\t\texpected: {}\n".format(expected_moves) +
                "\t\treceived: {}\n".format(valid_moves)
               )

    def movement_dict_check(self, moves):
        for move in moves:
            label = move["label"]
            pos = move["pos"]
            piece_type = move["type"]
            piece_color = move["color"]
            valid_moves = move["moves"]
            fens = move["fens"]
            for fen in fens:
                self.controller.fen = fen
                self.movement_check(
                        label,
                        pos,
                        piece_type,
                        piece_color,
                        valid_moves
                        )

    def test_white_pawn(self):
        moves = [
            # pawn in the middle of the board
            {
                "label": "pawn in the middle of the board",
                "pos": (3, 3),
                "type": PieceCode.PAWN,
                "color": PieceColor.WHITE,
                "moves": {(2, 3)},
                "fens": {
                    # pawn alone in the middle
                    "8/8/8/3P4/8/8/8/8 w KQkq - 0 0",
                    # same color piece in both front diagonals
                    "8/8/2R1R3/3P4/8/8/8/8 w KQkq - 0 0",
                    # different color piece both back diagonals
                    "8/8/8/3P4/2r1r3/8/8/8 w KQkq - 0 0",
                    }
            },
            # pawn in the middle of the board, path obstructed
            {
                "label": "pawn in the middle of the board, path obstructed",
                "pos": (3, 3),
                "type": PieceCode.PAWN,
                "color": PieceColor.WHITE,
                "moves": set(),
                "fens": {
                    # same color piece in front
                    "8/8/3R4/3P4/8/8/8/8 w KQkq - 0 0",
                    # different color piece in front
                    "8/8/3r4/3P4/8/8/8/8 w KQkq - 0 0",
                    # different color piece in front,
                    # same color piece in front diagonals
                    "8/8/2BrB3/3P4/8/8/8/8 w KQkq - 0 0",
                    }
            },
            # pawn with initial double start
            {
                "label": "pawn with initial double start",
                "pos": (6, 2),
                "type": PieceCode.PAWN,
                "color": PieceColor.WHITE,
                "moves": {(5, 2), (4, 2)},
                "fens": {
                    # pawn alone
                    "8/8/8/8/8/8/2P5/8 w KQkq - 0 0",
                    }
            },
            # pawn with en passant ready
            {
                "label": "pawn with en passant ready",
                "pos": (3, 4),
                "type": PieceCode.PAWN,
                "color": PieceColor.WHITE,
                "moves": {(2, 3), (2, 4)},
                "fens": {
                    # pawn next to black pawn
                    "8/8/8/3pP3/8/8/8/8 w KQkq d6 0 0",
                    }
            },
            ]
        self.movement_dict_check(moves)


if __name__ == "__main__":
    unittest.main()
