import threading

from game_board_controller import GameBoardController
from game_board_graphical import GameBoardGraphical
from game_board_timer import GameBoardTimer
from game_board_claim_draw_button import GameBoardClaimDrawButton
from player import Player
from piece import PieceColor
from pygame import mixer
from pathlib import Path


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
            settings: dict(),
            game_over_func,
            bottom_color: PieceColor = PieceColor.WHITE,
            headless: bool = False):

        self.game_over_func = game_over_func
        self.settings = settings

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
                bottom_color,
                self.settings)

        self.timer: GameBoardTimer = GameBoardTimer(
                dims,
                coords,
                bottom_color,
                self.settings,
                out_of_time_func=self.out_of_time
                )

        self.claim_draw_buttons = GameBoardClaimDrawButton(
                    dims,
                    coords,
                    bottom_color,
                    self.settings,
                    claim_draw_func=self.claim_draw
                    )
        self.players = {
                PieceColor.WHITE: player_white,
                PieceColor.BLACK: player_black
                }

        self._start_game()

    def out_of_time(self):
        self.pause(from_timer=True)
        winner_color = self.controller.opposite_color(
                self.player.color)
        self.game_over_func(
                title="Out of time",
                message="{} Wins!".format(
                    winner_color.name.capitalize()
                    )
                )

    def claim_draw(self):
        self.pause(from_timer=False)
        self.game_over_func(
                title="Draw Claimed",
                message="more than 50 moves were made")

    def pause(self, from_timer=False):
        if not from_timer:
            self.timer.pause()
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

        if self.timer.bottom_color == PieceColor.WHITE:
            self.timer.bottom_color = PieceColor.BLACK
        else:
            self.timer.bottom_color = PieceColor.WHITE

    def draw(self, surface):
        if self.headless:
            return
        self.graphical.draw(
                surface,
                self.controller.piece_info)
        self.timer.draw(
                surface
                )
        self.claim_draw_buttons.draw(surface)
        # draw player control feedback
        self.player.draw(
                surface,
                self.controller.piece_info,
                self.graphical.tile_info,
                self.graphical.adjust_idxs,
                self.controller.get_legal_moves,
                self.controller.is_promotion_valid)

    def _make_moves_async(self):
        self.timer.unpause()
        while self.controller.winner is None:
            if self.controller.stalemate_rule():
                self.timer.pause()
                self.game_over_func(
                        title="Stalemate",
                        message="Looks like that\'s a draw!")
                return
            valid_move = False
            old_pos = None
            new_pos = None
            promotion = None
            while not valid_move:
                move = self.player.make_move(
                        self.controller.piece_info,
                        self.graphical.adjust_idxs,
                        self.controller.get_legal_moves,
                        self.controller.is_promotion_valid,
                        self.controller.fen)
                if move is not None:
                    old_pos, new_pos, promotion = move
                    valid_moves = self.controller.get_legal_moves(old_pos)
                    if new_pos in valid_moves:
                        valid_move = True
                else:
                    return

            self.controller.fifty_move_rule(old_pos, new_pos)

            self.controller.move_piece(old_pos, new_pos, promotion)

            self.controller.threefold_repetition_rule(old_pos, new_pos)
            if self.controller.is_check_valid(new_pos):
                if self.controller.is_checkmate_valid(new_pos):
                    self.timer.pause()
                    self.game_over_func(
                            title="Match is over",
                            message="{} Wins!".format(
                                self.player.color.name.capitalize()
                                )
                            )
                    return

            self.controller.insufficient_checkmate_material_rule()

            if self.controller.insufficent_cmr_draw:
                self.timer.pause()
                self.game_over_func(
                        title="Draw",
                        message="not gonna happen"
                        )
                return

            if not self.headless:
                mixer.music.stop()
                mixer.music.play()
                if self.controller.claim_draw:
                    self.claim_draw_buttons.active = True
            self.finish_turn()

    def finish_turn(self):
        self.controller.finish_turn()
        self.timer.current_player = self.controller.turn

    def resize(self, x, y):
        self.graphical.dims = (x, y)
        self.timer.dims = (x, y)
        self.claim_draw_buttons.dims = (x, y)

    def event_capture(self, event):
        self.player.event_capture(
                event,
                self.controller.piece_info,
                self.graphical.tile_info,
                self.graphical.adjust_idxs,
                self.controller.is_promotion_valid)
        self.claim_draw_buttons.event_capture(event)

    def _start_game(self):
        self._async_thread = threading.Thread(target=self._make_moves_async)
        self._async_thread.start()

    @property
    def player(self):
        return self.players[self.controller.turn]
