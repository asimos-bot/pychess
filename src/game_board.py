import threading

from game_board_controller import GameBoardController, GameBoardPlayer
from game_board_graphical import GameBoardGraphical
from player import Player
from piece import PieceColor


# makes a bridge between the graphical and logical part of the game board
# while processing inputs
class GameBoard():
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            color: (int, int, int),
            player_black: Player,
            player_white: Player,
            bottom_color: PieceColor = PieceColor.BLACK):
        self.controller: GameBoardController = GameBoardController()
        self.graphical: GameBoardGraphical = GameBoardGraphical(
                dims,
                coords,
                color,
                bottom_color)
        self.players = {
                GameBoardPlayer.WHITE: player_white,
                GameBoardPlayer.BLACK: player_black
                }
        self._start_game()

    def pause(self):
        for player in self.players.values():
            player.pause()
        self._async_thread.join()

    def unpause(self):
        for player in self.players.values():
            player.unpause()
        self._async_thread = threading.Thread(
                target=self._make_moves_async)
        self._async_thread.start()

    def spin(self):
        if self.graphical.bottom_color == PieceColor.WHITE:
            self.graphical.bottom_color = PieceColor.BLACK
        else:
            self.graphical.bottom_color = PieceColor.WHITE

    def draw(self, surface):
        self.graphical.draw(
                surface,
                self.controller.piece_info)
        # draw player control feedback
        self.player.draw(
                surface,
                self.controller.piece_info,
                self.graphical.tile_info,
                self.graphical.adjust_idxs,
                self.controller.get_valid_moves)

    def _make_moves_async(self):

        while self.controller.winner is None:
            valid = False
            old_pos = None
            new_pos = None
            while not valid:
                move = self.player.make_move(
                        self.controller.piece_info,
                        self.graphical.adjust_idxs,
                        self.controller.get_valid_moves)
                if move is not None:
                    old_pos, new_pos = move
                    valid_moves = self.controller.get_valid_moves(old_pos)
                    if new_pos in valid_moves:
                        valid = True
                else:
                    return

            self.controller.move_piece(old_pos, new_pos)
            self.controller.finish_turn()

    def event_capture(self, event):
        self.player.event_capture(
                event,
                self.controller.piece_info,
                self.graphical.tile_info,
                self.graphical.adjust_idxs)

    def _start_game(self):
        self._async_thread = threading.Thread(target=self._make_moves_async)
        self._async_thread.start()

    @property
    def player(self):
        return self.players[self.controller.turn]
