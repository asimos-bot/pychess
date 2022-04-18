import threading

from game_board_controller import GameBoardController, GameBoardPlayer
from game_board_graphical import GameBoardGraphical
from player import Player


# makes a bridge between the graphical and logical part of the game board
# while processing inputs
class GameBoard():
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            color: (int, int, int),
            player_black: Player,
            player_white: Player):
        self.controller: GameBoardController = GameBoardController()
        self.graphical: GameBoardGraphical = GameBoardGraphical(
                dims,
                coords,
                color)
        self.players = {
                GameBoardPlayer.WHITE: player_white,
                GameBoardPlayer.BLACK: player_black
                }
        self.piece_info_func = self.controller.piece_info
        self.tile_info_func = self.graphical.tile_info
        self._start_game()

    def draw(self, surface):
        self.graphical.draw(
                surface,
                self.controller.piece_info)
        # draw player control feedback
        self.player.draw(
                surface,
                self.controller.piece_info,
                self.graphical.tile_info)

    def _make_moves_async(self):

        while self.controller.winner is None:
            valid = False
            old_pos = None
            new_pos = None
            while not valid:
                old_pos, new_pos = self.player.make_move(self.piece_info_func)
                valid_moves = self.controller.get_valid_moves(old_pos)
                if new_pos in valid_moves:
                    valid = True

            self.controller.move_piece(old_pos, new_pos)
            self.controller.finish_turn()

    def event_capture(self, event):
        self.player.event_capture(
                event,
                self.piece_info_func,
                self.tile_info_func)

    def _start_game(self):
        threading.Thread(target=self._make_moves_async).start()

    @property
    def player(self):
        return self.players[self.controller.turn]
