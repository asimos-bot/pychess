from player import Human, RandomAI
from piece import PieceColor

PLAYERS = {
        PieceColor.WHITE: Human,
        PieceColor.BLACK: RandomAI
        }
BOARD_INITIAL_BOTTOM_COLOR = PieceColor.WHITE
