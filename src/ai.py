from player import Player
from piece import PieceColor, PieceCode
from game_board_controller import GameBoardController

import random


class AI(Player):
    def __init__(self, color: PieceColor, settings: dict()):
        super(AI, self).__init__(color, settings)

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):

        if not self.playing:
            return None

        legal_moves = set()
        for i in range(8):
            for j in range(8):
                piece_info = piece_info_func((i, j))
                if piece_info is not None and piece_info[1] == self.color:
                    for move in get_legal_moves_func((i, j)):
                        legal_moves.add(((i, j), move))
        choosen_move = random.sample(legal_moves, 1)[0]
        random_promotion = [
                PieceCode.QUEEN,
                PieceCode.KNIGHT,
                PieceCode.BISHOP,
                PieceCode.ROOK][random.randint(0, 3)]
        choosen_move = (choosen_move[0], choosen_move[1], random_promotion)
        return choosen_move

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        pass

    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            is_promotion_valid_func):
        pass


class RandomAI(AI):

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func,
            fen_code):

        if not self.playing:
            return None

        legal_moves = set()
        for i in range(8):
            for j in range(8):
                piece_info = piece_info_func((i, j))
                if piece_info is not None and piece_info[1] == self.color:
                    for move in get_legal_moves_func((i, j)):
                        legal_moves.add(((i, j), move))
        choosen_move = random.sample(legal_moves, 1)[0]
        random_promotion = [
                PieceCode.QUEEN,
                PieceCode.KNIGHT,
                PieceCode.BISHOP,
                PieceCode.ROOK][random.randint(0, 3)]
        choosen_move = (choosen_move[0], choosen_move[1], random_promotion)
        return choosen_move


class MinMaxAI(AI):
    def __init__(self, color: PieceColor, settings: dict()):
        super(MinMaxAI, self).__init__(color, settings)
        self.controller = GameBoardController()

    def piece_score(self, piece_type: PieceCode):
        if piece_type == PieceCode.PAWN:
            return 4
        elif piece_type == PieceCode.KNIGHT:
            return 7
        elif piece_type == PieceCode.BISHOP:
            return 9
        elif piece_type == PieceCode.ROOK:
            return 10
        elif piece_type == PieceCode.KING:
            return 10e4
        elif piece_type == PieceCode.QUEEN:
            return 25

    def board_state_score(
            self,
            fen: str):
        self.controller.fen = fen
        score = 0
        enemy_color = self.controller.opposite_color(self.color)
        for enemy in self.controller.pieces_by_color[enemy_color]:
            score -= self.piece_score(self.controller.piece_info(enemy)[0])
        for my_piece in self.controller.pieces_by_color[self.color]:
            score += self.piece_score(self.controller.piece_info(my_piece)[0])
        return score

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func,
            fen_code) -> ((int, int), (int, int), PieceCode):

        return self.minimax(fen_code, 1, None, True)[0]

    def get_child_states(self, fen, parent_is_max):

        controller = GameBoardController()
        controller.fen = fen
        node_color = [controller.opposite_color(self.color), self.color][parent_is_max]
        for piece_pos in controller.pieces_by_color[node_color]:
            piece_type, piece_color = controller.piece_info(piece_pos)
            # iterate over all possible moves for this piece
            for move in controller.get_legal_moves(piece_pos):
                # iterate over all possible promotions
                # (ignore rook and bishop: queen is already a megazord of them)
                for promotion in "QN":
                    # check if we should skip the first promotion
                    if promotion == "Q":
                        # if this piece is not a pawn, not reason to iterate twice
                        if piece_type != PieceCode.PAWN:
                            continue
                        # if this piece is a pawn, not reason to go over promotion
                        # if not reaching edge of board
                        if piece_type == PieceCode.PAWN and ((move[1] != 7 and node_color == PieceColor.WHITE) or (move[1] != 0 and node_color == PieceColor.BLACK)):
                            continue

                    # create child with copy of board where move is made
                    copy = controller.copy()
                    copy.move_piece(piece_pos, move, promotion)
                    copy.finish_turn()
                    yield ((piece_pos, move, promotion), copy.fen)

    def minimax(
            self,
            fen,
            depth,
            move,
            is_max) -> (((int, int), (int, int), str), float):
        if depth == 0:
            return (move, self.board_state_score(fen))

        if is_max:
            max_score = (None, float('-inf'))
            for child_move, child_fen in self.get_child_states(fen, is_max):
                score = self.minimax(child_fen, depth - 1, child_move, False)
                if max_score[1] < score[1]:
                    max_score = (child_move, score[1])
            return max_score
        else:
            min_score = (None, float('inf'))
            for child_move, child_fen in self.get_child_states(fen, is_max):
                score = self.minimax(child_fen, depth - 1, child_move, True)
                if score[1] < min_score[1]:
                    min_score = (child_move, score[1])
            return min_score
