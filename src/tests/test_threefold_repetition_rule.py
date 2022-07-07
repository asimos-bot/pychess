import unittest

from game_board_controller import GameBoardController
from piece import Bishop, King, Knight, Pawn, PieceColor, Queen, Rook


class ThreefoldRuleTest(unittest.TestCase):
    def setUp(self):
        self.gb = GameBoardController()
        self.gb.pieces = []
        for i in range(8):
            line = []
            for j in range(8):
                if i == 0:
                    if j == 0 or j == 7:
                        line.append(Rook(PieceColor.WHITE, (i, j)))
                    elif j == 1 or j == 6:
                        line.append(Knight(PieceColor.WHITE, (i, j)))
                    elif j == 2 or j == 5:
                        line.append(Bishop(PieceColor.WHITE, (i, j)))
                    elif j == 3:
                        line.append(Queen(PieceColor.WHITE, (i, j)))
                    elif j == 4:
                        line.append(King(PieceColor.WHITE, (i, j)))
                elif i == 1:
                    line.append(Pawn(PieceColor.WHITE, (i, j)))
                elif i == 6:
                    line.append(Pawn(PieceColor.BLACK, (i, j)))
                elif i == 7:
                    if j == 0 or j == 7:
                        line.append(Rook(PieceColor.BLACK, (i, j)))
                    elif j == 1 or j == 6:
                        line.append(Knight(PieceColor.BLACK, (i, j)))
                    elif j == 2 or j == 5:
                        line.append(Bishop(PieceColor.BLACK, (i, j)))
                    elif j == 3:
                        line.append(Queen(PieceColor.BLACK, (i, j)))
                    elif j == 4:
                        line.append(King(PieceColor.BLACK, (i, j)))
                else:
                    line.append(None)
            self.gb.pieces.append(line)

    def test_initial_board(self):
        self.gb._turn = PieceColor.BLACK
        self.gb.threefold_repetition_rule((7, 1), (5, 0))
        self.assertFalse(self.gb.threefold_draw)

    def test_black_threefold(self):
        self.gb._turn = PieceColor.BLACK
        self.gb.black_moved_times = 4
        self.gb.black_threefold = [(5, 0), (7, 1), (5, 0), (7, 1)]
        self.gb.black_last_moved_piece = self.gb.pieces[7][1]
        self.gb.pieces[5][0] = self.gb.pieces[7][1]
        self.gb.pieces[7][1] = None
        self.gb.black_last_old_and_new = [(5, 0), (7, 1)]
        self.gb.threefold_repetition_rule((7, 1), (5, 0))
        self.assertTrue(self.gb.threefold_draw)

    def test_black_not_threefold(self):
        self.gb._turn = PieceColor.BLACK
        self.gb.black_moved_times = 4
        self.gb.black_threefold = [(5, 0), (7, 1), (5, 0), (7, 1)]
        self.gb.black_last_moved_piece = self.gb.pieces[7][1]
        self.gb.pieces[5][2] = self.gb.pieces[7][1]
        self.gb.pieces[7][1] = None
        self.gb.black_last_old_and_new = [(5, 0), (7, 1)]
        self.gb.threefold_repetition_rule((7, 1), (5, 2))
        self.assertFalse(self.gb.threefold_draw)

    if __name__ == "__main__":
        unittest.main()
