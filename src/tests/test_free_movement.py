import unittest
from game_board_controller import GameBoardController
from piece import PieceCode, PieceColor


class PieceFreeMovementTest(unittest.TestCase):
    def setUp(self):
        self.controller = GameBoardController()
        self.controller.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

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
        legal_moves = self.controller.get_legal_moves(pos)
        self.assertEqual(
                legal_moves,
                expected_moves,
                "\n{}:\n\t".format(label) +
                "illegal movement set for {} {} at {}:\n".format(
                    piece_color.name.lower(),
                    piece_type.name.lower(),
                    pos) +
                "\t\texpected: {}\n".format(expected_moves) +
                "\t\treceived: {}\n".format(legal_moves)
               )

    def movement_dict_check(self, moves):
        for move in moves:
            label = move["label"]
            pos = move["pos"]
            piece_type = move["type"]
            piece_color = move["color"]
            legal_moves = move["moves"]
            fens = move["fens"]
            for fen in fens:
                self.controller.fen = fen
                self.movement_check(
                        label,
                        pos,
                        piece_type,
                        piece_color,
                        legal_moves
                        )

    def test_pawn_middle_forward(self):
        moves = [
                # white pawn in the middle of the board
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
                # black pawn in the middle of the board
                {
                    "label": "pawn in the middle of the board",
                    "pos": (3, 3),
                    "type": PieceCode.PAWN,
                    "color": PieceColor.BLACK,
                    "moves": {(4, 3)},
                    "fens": {
                        # pawn alone in the middle
                        "8/8/8/3p4/8/8/8/8 w KQkq - 0 0",
                        # same color piece in both front diagonals
                        "8/8/8/3p4/2r1r3/8/8/8 w KQkq - 0 0",
                        # different color piece both back diagonals
                        "8/8/2R1R3/3p4/8/8/8/8 w KQkq - 0 0",
                        }
                },
            ]
        self.movement_dict_check(moves)

    def test_pawn_double_start(self):
        moves = [
                # white pawn with initial double start
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
                # black pawn with initial double start
                {
                    "label": "pawn with initial double start",
                    "pos": (1, 2),
                    "type": PieceCode.PAWN,
                    "color": PieceColor.BLACK,
                    "moves": {(2, 2), (3, 2)},
                    "fens": {
                        # pawn alone
                        "8/2p5/8/8/8/8/8/8 w KQkq - 0 0",
                        }
                },
            ]
        self.movement_dict_check(moves)

    def test_pawn_en_passant_ready(self):
        moves = [
                # white pawn with en passant ready
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
                # black pawn with en passant ready
                {
                    "label": "pawn with en passant ready",
                    "pos": (4, 3),
                    "type": PieceCode.PAWN,
                    "color": PieceColor.BLACK,
                    "moves": {(5, 3), (5, 4)},
                    "fens": {
                        # pawn next to white pawn
                        "8/8/8/8/3pP3/8/8/8 w KQkq e3 0 0",
                        }
                },
            ]
        self.movement_dict_check(moves)

    def test_pawn_double_forward_obstructed(self):
        moves = [
                # white pawn with initial double start
                {
                    "label": "pawn with initial double start obstructed",
                    "pos": (6, 2),
                    "type": PieceCode.PAWN,
                    "color": PieceColor.WHITE,
                    "moves": {(5, 2)},
                    "fens": {
                        "8/8/8/8/2r5/8/2P5/8 w KQkq - 0 0",
                        }
                },
                # black pawn with initial double start
                {
                    "label": "pawn with initial double start",
                    "pos": (1, 2),
                    "type": PieceCode.PAWN,
                    "color": PieceColor.BLACK,
                    "moves": {(2, 2)},
                    "fens": {
                        "8/2p5/8/2R5/8/8/8/8 w KQkq - 0 0",
                        }
                },
            ]
        self.movement_dict_check(moves)


if __name__ == "__main__":
    unittest.main()
