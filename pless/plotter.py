from pless.data import background, black, white, image_dir
from pless.board import Piece, Board
from pless.move import PawnMove, KingMove, KnightMove, QueenMove, BishopMove, RookMove
import cv2
import numpy as np

move_map = {"Rook": RookMove, "Queen": QueenMove, "Bishop": BishopMove, "Knight": KnightMove, "King": KingMove}

char_piece_map = {"R": "Rook", "Q": "Queen", "B": "Bishop", "N": "Knight", "K": "King"}


def add_piece(img, position, piece_image, alpha, width, height):
    cv_image = cv2.imread(piece_image, cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(cv_image, (width, height))
    resized.astype(float)
    posx = position[0] * height
    posy = position[1] * width
    alpha_mask = np.expand_dims(resized[:, :, 3], axis=2).repeat(3, 2) / 255 * alpha
    actual = resized[:, :, :3]
    img[posx : posx + height, posy : posy + width] = (
        img[posx : posx + height, posy : posy + width] * (1 - alpha_mask) + actual * alpha_mask
    )


def plot(board, width=720, height=720):
    img = cv2.imread(background)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)
    resized.astype(float)
    for row_index in range(8):
        for col_index in range(8):
            cell_pos = (row_index, col_index)
            color = board.color(cell_pos)
            if color == "Blank":
                continue
            if color == "Black":
                add_piece(resized, cell_pos, black[board.piece(cell_pos)], 1, width // 8, height // 8)
            else:
                add_piece(resized, cell_pos, white[board.piece(cell_pos)], 1, width // 8, height // 8)
    return resized


def consruct_initial_board():
    board = Board()
    pieces = {
        (0, 0): "Rook",
        (0, 1): "Knight",
        (0, 2): "Bishop",
        (0, 3): "Queen",
        (0, 4): "King",
        (0, 5): "Bishop",
        (0, 6): "Knight",
        (0, 7): "Rook",
        (1, 0): "Pawn",
        (1, 1): "Pawn",
        (1, 2): "Pawn",
        (1, 3): "Pawn",
        (1, 4): "Pawn",
        (1, 5): "Pawn",
        (1, 6): "Pawn",
        (1, 7): "Pawn",
    }
    for k, v in pieces.items():
        board.data[k[0]][k[1]] = Piece(v, "Black")
        board.data[7 - k[0]][k[1]] = Piece(v, "White")
    return board


def notating_to_pair(notation):
    x = ord(notation[1]) - ord("1")
    y = ord(notation[0]) - ord("a")
    return (7 - x, y)


def extract_pawn_move(move_string, turn, board):
    dx, dy = notating_to_pair(move_string)
    if turn == "Black":
        if board.empty((dx - 1, dy)):
            return PawnMove((dx - 2, dy), (dx, dy), turn)
        else:
            return PawnMove((dx - 1, dy), (dx, dy), turn)
    else:
        if board.empty((dx + 1, dy)):
            return PawnMove((dx + 2, dy), (dx, dy), turn)
        else:
            return PawnMove((dx + 1, dy), (dx, dy), turn)


def extract_pawn_capture(move_string, turn, board):
    dx, dy = notating_to_pair(move_string[-2:])
    sy = ord(move_string[0]) - ord("a")
    if turn == "Black":
        sx = dx - 1
    else:
        sx = dx + 1
    return PawnMove((sx, sy), (dx, dy), turn)


def extract_normal_move(move_string, turn, board):
    if move_string[-1] == "#":
        move_string = move_string[:-1]
    move_string1 = move_string
    dx, dy = notating_to_pair(move_string[-2:])
    move_string = move_string[:-2]
    if move_string[-1] == "x":
        move_string = move_string[:-1]
    move_piece = char_piece_map[move_string[0]]
    move_string = move_string[1:]
    sx, sy = None, None
    if len(move_string) >= 1:
        c = move_string[0]
        if ord(c) >= ord("a") and ord(c) <= ord("h"):
            sy = ord(c) - ord("a")
        else:
            sx = 7 - (ord(c) - ord("1"))
    if len(move_string) >= 2:
        c = move_string[1]
        if ord(c) >= ord("a") and ord(c) <= ord("h"):
            sy = ord(c) - ord("a")
        else:
            sx = 7 - (ord(c) - ord("1"))
    print(move_string1, sx, sy, dx, dy, move_piece)
    for i in range(8):
        for j in range(8):
            if sx is not None and sx != i or sy is not None and sy != j:
                continue
            piece = board.piece((i, j))
            if piece != move_piece:
                continue
            if move_string1 == "Qb6":
                print(i, j)
            move_class = move_map[piece]
            move = move_class((i, j), (dx, dy), turn)
            if move.is_valid(board):
                return move
    return None


def animate_moves(moves_strings):
    board = consruct_initial_board()
    turn = "White"
    imgs = []
    for move_string in moves_strings:
        if move_string[-1] == "+":
            move_string = move_string[0:-1]
        move = None
        if move_string == "O-O":
            if turn == "Black":
                move = KingMove((0, 4), (0, 6), turn, "short")
            else:
                move = KingMove((7, 4), (7, 6), turn, "short")
        elif move_string == "O-O-O":
            if turn == "Black":
                move = KingMove((0, 4), (0, 2), turn, "long")
            else:
                move = KingMove((7, 4), (7, 2), turn, "long")
        elif move_string[-2] == "=":
            if turn == "Black":
                move = PawnMove((6, ord(move_string[0]) - ord("a")), notating_to_pair(move_string[-4:-2]), turn)
            else:
                move = PawnMove((1, ord(move_string[0]) - ord("a")), notating_to_pair(move_string[-4:-2]), turn)
        elif len(move_string) == 2:
            move = extract_pawn_move(move_string, turn, board)
        elif move_string[0].islower():
            move = extract_pawn_capture(move_string, turn, board)
        else:
            move = extract_normal_move(move_string, turn, board)
        # print(move.source, move.destination, turn)
        animations = board.move(move)
        imgs.extend(animate_move(board, animations))
        board.print()
        turn = "White" if turn == "Black" else "Black"
    generate_video(imgs)


def add_piece_with_cor(img, position, piece_image, alpha, width, height):
    cv_image = cv2.imread(piece_image, cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(cv_image, (width, height))
    resized.astype(float)
    posx = position[0]
    posy = position[1]
    actual = resized[:, :, :3]
    alpha_mask = np.expand_dims(resized[:, :, 3], axis=3).repeat(3, 2) / 255 * alpha
    img[posx : posx + height, posy : posy + width] = (
        img[posx : posx + height, posy : posy + width] * (1 - alpha_mask) + actual * alpha_mask
    )


def plot_except(board, pieces, width=720, height=720):
    img = cv2.imread(background)
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)
    resized.astype(float)
    for row_index in range(8):
        for col_index in range(8):
            if board.data[row_index][col_index] in pieces:
                continue
            cell_pos = (row_index, col_index)
            color = board.color(cell_pos)
            if color == "Blank":
                continue
            if color == "Black":
                add_piece(resized, cell_pos, black[board.piece(cell_pos)], 1, width // 8, height // 8)
            else:
                add_piece(resized, cell_pos, white[board.piece(cell_pos)], 1, width // 8, height // 8)
    return resized


def animate_move(board, animations, width=720, height=720):
    animated_pieces = []
    for e in animations:
        animated_pieces.append(e.piece)
    pwidth = width // 8
    pheight = height // 8
    imgs = []
    fps = 15
    dist = 0
    for e in animations:
        dist = max(dist, max(abs(e.source[0] - e.destination[0]), abs(e.source[1] - e.destination[1])))
    fps = dist * 3
    for i in range(fps):
        img = plot_except(board, animated_pieces)
        for e in animations:

            posx = int(e.source[0] * pheight + (e.destination[0] - e.source[0]) * pheight * i / (fps - 1))
            posy = int(e.source[1] * pwidth + (e.destination[1] - e.source[1]) * pwidth * i / (fps - 1))
            if e.create == 1:
                op = i / (fps - 1)
            elif e.create == 0:
                op = 1
            else:
                op = ((fps - 1) - i) / (fps - 1)
            if e.piece.color == "Black":
                piece_image = black[e.piece.piece_name]
            else:
                piece_image = white[e.piece.piece_name]

            add_piece_with_cor(img, (posx, posy), piece_image, op, width // 8, height // 8)
            imgs.append(img)
    for i in range(45):
        imgs.append(img)
    return imgs


def generate_video(imgs, format="XVID"):
    """
    Create a video from a list of images.
 
    @param      outvid      output video
    @param      images      list of images to use in the video
    @param      fps         frame per second
    @param      size        size of each frame
    @param      is_color    color
    @param      format      see http://www.fourcc.org/codecs.php
    @return                 see http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
 
    The function relies on http://opencv-python-tutroals.readthedocs.org/en/latest/.
    By default, the video will have the size of the first image.
    It will resize every image to this size before adding them to the video.
    """
    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize

    fourcc = VideoWriter_fourcc(*format)
    vid = None
    for img in imgs:
        if vid is None:
            size = img.shape[1], img.shape[0]
            vid = VideoWriter("../video/outvid.mp4", fourcc, 30, size, True)
        vid.write(img)
    vid.release()
    return vid
