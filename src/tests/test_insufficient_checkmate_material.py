import unittest

from game_board_controller import GameBoardController
from piece import Bishop, King, Knight, Pawn, PieceColor


class InsufficientCheckTest(unittest.TestCase):
    def setUp(self):
        self.gb = GameBoardController()
        self.gb.pieces = []
        self.gb.pieces_by_color = {
            PieceColor.WHITE: set(), PieceColor.BLACK: set()}
        for i in range(8):
            line = []
            for j in range(8):
                line.append(None)
            self.gb.pieces.append(line)

    def test_two_kings(self):
        self.gb.pieces[0][0] = King(PieceColor.BLACK, (0, 0))
        self.gb.pieces[7][0] = King(PieceColor.WHITE, (7, 0))
        self.gb.pieces_by_color[PieceColor.WHITE].add((7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 0))
        self.gb.insufficient_checkmate_material_rule()
        self.assertTrue(self.gb.insufficent_cmr_draw)

    def test_king_and_bishop(self):
        self.gb.pieces[0][0] = King(PieceColor.BLACK, (0, 0))
        self.gb.pieces[0][1] = Bishop(PieceColor.BLACK, (0, 1))
        self.gb.pieces[7][0] = King(PieceColor.WHITE, (7, 0))
        self.gb.pieces_by_color[PieceColor.WHITE].add((7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 1))
        self.gb.insufficient_checkmate_material_rule()
        self.assertTrue(self.gb.insufficent_cmr_draw)

    def test_king_and_knight(self):
        self.gb.pieces[0][0] = King(PieceColor.BLACK, (0, 0))
        self.gb.pieces[0][1] = Knight(PieceColor.BLACK, (0, 1))
        self.gb.pieces[7][0] = King(PieceColor.WHITE, (7, 0))
        self.gb.pieces_by_color[PieceColor.WHITE].add((7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 1))
        self.gb.insufficient_checkmate_material_rule()
        self.assertTrue(self.gb.insufficent_cmr_draw)

    def test_king_and_two_knights(self):
        self.gb.pieces[0][0] = King(PieceColor.BLACK, (0, 0))
        self.gb.pieces[0][1] = Knight(PieceColor.BLACK, (0, 1))
        self.gb.pieces[0][2] = Knight(PieceColor.BLACK, (0, 2))
        self.gb.pieces[7][0] = King(PieceColor.WHITE, (7, 0))
        self.gb.pieces_by_color[PieceColor.WHITE].add((7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 1))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 2))
        self.gb.insufficient_checkmate_material_rule()
        self.assertTrue(self.gb.insufficent_cmr_draw)

    def test_king_and_pawn(self):
        self.gb.pieces[0][0] = King(PieceColor.BLACK, (0, 0))
        self.gb.pieces[0][1] = Pawn(PieceColor.BLACK, (0, 1))
        self.gb.pieces[7][0] = King(PieceColor.WHITE, (7, 0))
        self.gb.pieces_by_color[PieceColor.WHITE].add((7, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 0))
        self.gb.pieces_by_color[PieceColor.BLACK].add((0, 1))
        self.gb.insufficient_checkmate_material_rule()
        self.assertFalse(self.gb.insufficent_cmr_draw)
