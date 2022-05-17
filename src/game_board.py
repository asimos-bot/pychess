import threading

from game_board_controller import GameBoardController, GameBoardPlayer
from game_board_graphical import GameBoardGraphical
from player import Player
from piece import PieceColor
from pygame import mixer
from pathlib import Path
from time import sleep


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
            bottom_color: PieceColor = PieceColor.WHITE,
            headless: bool = False):

        # load sound effects
        piece_down_sound = Path(__file__).parent.parent.joinpath("assets")
        piece_down_sound = piece_down_sound.joinpath("piece_down.wav")
        if not headless:
            mixer.init()
            mixer.music.load(piece_down_sound)
            mixer.music.set_volume(0.7)

        self.headless = headless
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
        if self.headless:
            return
        self.graphical.draw(
                surface,
                self.controller.piece_info)
        # draw player control feedback
        self.player.draw(
                surface,
                self.controller.piece_info,
                self.graphical.tile_info,
                self.graphical.adjust_idxs,
                self.controller.get_legal_moves)

    def _make_moves_async(self):

        while self.controller.winner is None:
            valid_move = False
            old_pos = None
            new_pos = None
            while not valid_move:
                move = self.player.make_move(
                        self.controller.piece_info,
                        self.graphical.adjust_idxs,
                        self.controller.get_legal_moves)
                if move is not None:
                    old_pos, new_pos = move
                    valid_moves = self.controller.get_legal_moves(old_pos)
                    if new_pos in valid_moves:
                        valid_move = True
                else:
                    return

            self.controller.move_piece(old_pos, new_pos)

            if not self.headless:
                mixer.music.stop()
                mixer.music.play()
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
