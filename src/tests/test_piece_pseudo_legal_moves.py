import unittest
from piece import Bishop, King, Knight, Pawn, PieceColor, Queen, Rook


class PieceUpdatePseudoLegalMovesTest(unittest.TestCase):
    def get_piece(self, pos):
        piece = self.pieces[pos[0]][pos[1]]
        if piece is not None:
            return piece.type, piece.color
        else:
            return None

    def setUp(self):
        self.pieces = []
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
                elif i == 4 and j == 4:
                    line.append(Queen(PieceColor.BLACK, (i, j)))
                elif i == 6 and not j == 0:
                    line.append(Pawn(PieceColor.BLACK, (i, j)))
                elif i == 7:
                    if j == 0 or j == 7:
                        line.append(Rook(PieceColor.BLACK, (i, j)))
                    elif j == 1 or j == 6:
                        line.append(Knight(PieceColor.BLACK, (i, j)))
                    elif j == 2 or j == 5:
                        line.append(Bishop(PieceColor.BLACK, (i, j)))
                    elif j == 4:
                        line.append(King(PieceColor.BLACK, (i, j)))
                else:
                    line.append(None)
            self.pieces.append(line)
        self.queen = self.pieces[4][4]
        self.knight = self.pieces[7][1]
        self.king = self.pieces[7][4]
        self.rook = self.pieces[7][0]

    def test_queen(self):
        self.queen.update_pseudo_legal_moves(self.get_piece, None, None)
        self.assertSetEqual(self.queen.pseudo_legal_moves, {(4, 0), (3, 4), (4, 3), (5, 4), (4, 6), (2, 2), (
            4, 2), (4, 5), (3, 3), (5, 3), (2, 4), (4, 1), (4, 7), (3, 5), (5, 5), (1, 1), (1, 4), (1, 7), (2, 6)})
    
    def test_rook(self):
        self.rook.update_pseudo_legal_moves(self.get_piece, None, None)
        print()
        self.assertSetEqual(self.rook.pseudo_legal_moves, {(6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0)})


    def test_knight(self):
        self.knight.update_pseudo_legal_moves(self.get_piece, None, None)
        self.assertSetEqual(self.knight.pseudo_legal_moves, {(5, 0), (5, 2)})

    def test_king(self):
        self.king.update_pseudo_legal_moves(self.get_piece, None, None)
        self.assertSetEqual(self.king.pseudo_legal_moves, set())


    if __name__ == "__main__":
        unittest.main()
