from pless.move import KingMove, KnightMove, PawnMove, BishopMove, RookMove, QueenMove


class Board:
    piece_map = {"N": "Knight", "B": "Bishop", "Q": "Queen", "R": "Rook", "K": "King", "P": "Pawn"}
    colors_map = {"B": "Black", "W": "White"}

    def __init__(self, data=[]):
        data = data if data else [[None for i in range(8)] for j in range(8)]
        self.data = data
        self.black_king_moved = False
        self.white_king_moved = False
        self.last_move = None

    def move(self, move):
        self.last_move = move
        # assert move.is_valid(self)
        sx, sy = move.source
        dx, dy = move.destination
        to_be_animated = []
        if isinstance(move, PawnMove) and move.promotion:
            created_piece = Piece(move.promotion_piece, move.turn)
            to_be_animated.append(self.create_piece(move.destination, created_piece))
            to_be_animated.append(self.remove_piece(move.source))
        elif isinstance(move, PawnMove) and move.is_en_passant(self):
            to_be_animated.append(self.move_piece(move.source, move.destination))
            if move.turn == "Black":
                to_be_animated.append(self.remove_piece((dx, dy - 1)))
            else:
                to_be_animated.append(self.remove_piece((dx, dy + 1)))
        else:
            to_be_animated.append(self.move_piece(move.source, move.destination))

        if isinstance(move, KingMove) and move.castle:
            if move.turn == "Black":
                if move.castle == "short":
                    to_be_animated.append(self.move_piece((0, 7), (0, 5)))
                else:
                    to_be_animated.append(self.move_piece((0, 0), (0, 3)))
            else:
                if move.castle == "short":
                    to_be_animated.append(self.move_piece((7, 7), (7, 5)))
                else:
                    to_be_animated.append(self.move_piece((7, 0), (7, 3)))
        self.last_move = move
        return to_be_animated

    def move_piece(self, source, destination):
        sx, sy = source
        dx, dy = destination
        piece = self.data[sx][sy]
        self.data[dx][dy] = self.data[sx][sy]
        self.data[sx][sy] = None
        self.data[dx][dy].moved = True
        return PieceAnimation(piece, source, destination, 0)

    def remove_piece(self, cell):
        x, y = cell
        piece = self.data[x][y]
        self.data[x][y] = None
        return PieceAnimation(piece, cell, cell, -1)

    def create_piece(self, cell, piece):
        x, y = cell
        self.data[x][y] = piece
        return PieceAnimation(piece, cell, cell, 1)

    def piece(self, cell):
        piece_object = self.data[cell[0]][cell[1]]
        if not piece_object:
            return "Blank"
        else:
            return piece_object.piece_name

    def king_in_check(self, color):
        kx, ky = 0, 0
        for i in range(8):
            for j in range(8):
                if (
                    self.data[i][j] is not None
                    and self.data[i][j].color == color
                    and self.data[i][j].piece_name == "King"
                ):
                    kx, ky = i, j
        for i in range(8):
            for j in range(8):
                if self.data[i][j] is not None and self.data[i][j].color != color:
                    if self.data[i][j].piece_name == "Pawn":
                        if self.data[i][j].color == "White" and i - kx == 1 and abs(j - ky) == 1:
                            return True
                        if self.data[i][j].color == "Black" and kx - i == 1 and abs(j - ky) == 1:
                            return True
                    elif self.data[i][j].piece_name == "Rook":
                        if (i == kx or j == ky) and self.is_clear_path((i, j), (kx, ky)):
                            return True
                    elif self.data[i][j].piece_name == "Queen":
                        if (i == kx or j == ky or i + j == kx + ky or i - j == kx - ky) and self.is_clear_path(
                            (i, j), (kx, ky)
                        ):
                            return True
                    elif self.data[i][j].piece_name == "King":
                        if abs(i - kx) <= 1 and abs(j - ky) <= 1:
                            return True
                    elif self.data[i][j].piece_name == "Bishop":
                        if (i + j == kx + ky or i - j == kx - ky) and self.is_clear_path((i, j), (kx, ky)):
                            return True
                    elif self.data[i][j].piece_name == "Knight":
                        dx = i - kx
                        dy = j - ky
                        if abs(dx) == 1 and abs(dy) == 2 or abs(dx) == 2 and abs(dy) == 1:
                            return True
            return False

    def king_not_in_check_after_move(self, move):
        copy = self.copy_board()
        copy.move(move)
        return not copy.king_in_check(move.turn)

    def valid_en_passant(self, move):
        last_move = self.last_move
        if not isinstance(last_move, PawnMove):
            return False
        if abs(last_move.dy) != 2:
            return False
        if move.turn == "Black":
            return (
                move.destination[0] == last_move.destination[0] + 1 and move.destination[1] == last_move.destination[1]
            )
        else:
            return (
                move.destination[0] == last_move.destination[0] - 1 and move.destination[1] == last_move.destination[1]
            )

    def copy_board(self):
        board = Board()
        board.last_move = self.move
        for i in range(8):
            for j in range(8):
                if self.data[i][j] is not None:
                    board.data[i][j] = Piece(self.data[i][j].piece_name, self.data[i][j].color)
                    board.data[i][j].moved = self.data[i][j].moved
        return board

    def is_clear_path(self, source, destination):
        dx, dy = destination[0] - source[0], destination[1] - source[1]
        num_of_moves = max(abs(dx), abs(dy))
        x_step = 0 if not dx else dx // abs(dx)
        y_step = 0 if not dy else dy // abs(dy)
        current_cell = source
        for i in range(num_of_moves - 1):
            current_cell = (current_cell[0] + x_step, current_cell[1])
            current_cell = (current_cell[0], current_cell[1] + y_step)
            if not self.empty(current_cell):
                return False
        return True

    def color(self, cell):
        piece_object = self.data[cell[0]][cell[1]]
        if not piece_object:
            return "Blank"
        else:
            return piece_object.color

    def empty(self, cell):
        return self.data[cell[0]][cell[1]] is None

    def print(self):
        for i in range(8):
            for j in range(8):
                if self.data[i][j] is not None:
                    if self.data[i][j].piece_name == "Knight":
                        print("N", end=" ")
                    else:
                        print(self.data[i][j].piece_name[0], end=" ")
                else:
                    print("-", end=" ")
            print("")


class Piece:
    def __init__(self, piece_name, color):
        self.moved = False
        self.piece_name = piece_name
        self.color = color


class PieceAnimation:
    def __init__(self, piece, source, destination, create=None):
        self.piece = piece
        self.source = source
        self.destination = destination
        self.create = create or 0
