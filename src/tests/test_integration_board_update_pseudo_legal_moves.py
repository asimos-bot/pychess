import unittest
from unittest.mock import MagicMock
from piece import PieceColor, Rook
from game_board_controller import GameBoardController
from piece import PieceCode


class IntegrationBoardUpdatePseudoLegalMovesTest(unittest.TestCase):
    def get_piece(_, pos):
        if pos[0] == 7 and (pos[1] == 0 or pos[1] == 7):
            return PieceCode.ROOK, None
        else:
            return None

    def setUp(self):
        self.gb = GameBoardController()
        self.gb.pieces = []
        self.gb.piece_info = MagicMock(side_effect=self.get_piece)
        self.gb.get_color_castlings = MagicMock()
        self.gb.opposite_color = MagicMock(return_value=PieceColor.WHITE)
        self.gb.pieces_by_color = {
            PieceColor.WHITE: set(), PieceColor.BLACK: set()}
        for i in range(8):
            line = []
            for j in range(8):
                line.append(None)
            self.gb.pieces.append(line)
        r1 = Rook(PieceColor.BLACK, (7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((7, 0))
        r2 = Rook(PieceColor.BLACK, (7, 7))
        self.gb.pieces_by_color[PieceColor.BLACK].add((7, 7))
        self.gb.pieces[7][7] = r2
        self.gb.pieces[7][0] = r1

    def test_board(self):
        self.gb.update_pseudo_legal_moves()
        self.assertSetEqual(self.gb.attackable_tiles_from[PieceColor.BLACK], {(7, 1), (7, 2), (7, 3), (
            7, 4), (7, 5), (7, 6), (6, 7), (5, 7), (4, 7), (3, 7), (2, 7), (1, 7), (0, 7), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)})
        self.assertSetEqual(
            self.gb.attackable_tiles_from[PieceColor.WHITE], set())

    if __name__ == "__main__":
        unittest.main()
