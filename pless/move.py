class Move:
    #     def __init__(self, move_text, board, turn):
    #         self.piece = get_piece()
    #         self.capture = "x" in move_text
    #         self.promotion = "=" in move_text
    #         self.castle = 'O-O' in move_text
    #         self.piece_moves = []
    #         self.eliminated_pieces = []

    #     def get_piece(self, move_text, board):
    #         piece_map = {"N": "Knight", "B": "Bishop", "Q": "Queen", "R": "Rook", "K": "King"}
    #         if move_tett[0] in piece_map:
    #             return piece_map[move_text[0]]
    #         else:
    #             return "Pawn"

    #     def get_source_cell(self, move_text, board, turn):
    #         candidates = []
    #         for row_index, row in enumerate(board.data):
    #             for col_index, col in enumerate(row):
    #                 cell_pos = (row_index, col_index)
    #                 if board.piece(cell_pos) == self.piece:
    #                     candidates.append(cell_pos)
    def __init__(self, source, destination, turn):
        self.source = source
        self.destination = destination
        self.turn = turn
        self.dx = destination[0] - source[0]
        self.dy = destination[1] - source[1]

    def is_valid(self, board):
        in_board = self.destination[0] < 8 and self.destination[1] >= 0 and self.source[0] >= 0 and self.source[1] < 8

        return (
            board.color(self.source) == self.turn
            and in_board
            and board.king_not_in_check_after_move(self)
            and board.piece(self.destination) != "King"
            and board.color(self.destination) != self.turn
        )


class NonPassingMove(Move):
    def __init__(self, source, destination, turn):
        super().__init__(source, destination, turn)

    def is_valid(self, board):
        return super().is_valid(board) and board.is_clear_path(self.source, self.destination)


class PawnMove(NonPassingMove):
    def __init__(self, source, destination, turn, promtion_piece=None):
        super().__init__(source, destination, turn)
        self.promotion_piece = promtion_piece
        self.promotion = self.is_promotion()
        self.capture = self.is_capture()

    def is_valid(self, board):
        if not super().is_valid(board):
            return False
        if board.piece(self.source) != "Pawn":
            return False
        if self.turn == "Black" and not (self.dy == 1 or self.dy == 2 and self.source[0] == 1):
            return False
        if self.turn == "White" and not (self.dy == -1 or self.dy == -2 and self.source[0] == 6):
            return False
        if abs(self.dy) == 2 and self.dx != 0:
            return False
        if self.capture:
            if self.is_en_passant(board) and not board.valid_en_passant(self):
                return False
            if not self.is_en_passant(board) and board.empty(self.destination):
                return False
        if self.is_promotion:
            if self.turn == "Black" and not self.destination[1] != 7:
                return False
            if self.turn == "White" and not self.destination[1] != 0:
                return False
        return True

    def is_promotion(self):
        return self.promotion_piece is not None

    def is_capture(self):
        return self.dy != 0

    def is_en_passant(self, board):
        return self.capture and board.empty(self.destination)


class KnightMove(Move):
    def __init__(self, source, destination, turn):
        super().__init__(source, destination, turn)

    def is_valid(self, board):
        return super().is_valid(board) and (
            abs(self.dx) == 1 and abs(self.dy) == 2 or abs(self.dx) == 2 and abs(self.dy) == 1
        )


class KingMove(NonPassingMove):
    def __init__(self, source, destination, turn, castle=None):
        super().__init__(source, destination, turn)
        self.castle = castle

    def is_valid(self, board):
        if not super().is_valid(board):
            return False
        if board.piece(self.source) != "King":
            return False
        if self.castle is not None and not (
            board.king_moved(self.turn) is False
            and board.rook_at_moved(self.source) is False
            and board.is_clear_path(self.source, self.destination)
            and board.empty(self.destination)
        ):
            return False
        if self.castle is None and not (abs(self.dx) <= 1 and abs(self.dy) <= 1):
            return False
        return True


class RookMove(NonPassingMove):
    def __init__(self, source, destination, turn):
        super().__init__(source, destination, turn)

    def is_valid(self, board):
        if board.piece(self.source) != "Rook":
            return False
        return super().is_valid(board) and (self.dx == 0 or self.dy == 0)


class QueenMove(NonPassingMove):
    def __init__(self, source, destination, turn):
        super().__init__(source, destination, turn)

    def is_valid(self, board):
        if board.piece(self.source) != "Queen":
            return False
        return (self.dx == 0 or self.dy == 0 or abs(self.dx) == abs(self.dy)) and super().is_valid(board)


class BishopMove(NonPassingMove):
    def __init__(self, source, destination, turn):
        super().__init__(source, destination, turn)

    def is_valid(self, board):
        if board.piece(self.source) != "Bishop":
            return False
        return abs(self.dx) == abs(self.dy) and super().is_valid(board)
