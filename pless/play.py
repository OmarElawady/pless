import numpy as np
import cv2
from pless.board import Board, Piece
from pless.plotter import plot, animate_moves
from pless.pgn import parse_png


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

"""
img = plot(board)
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
"""

moves_strings = parse_png(
    """[Event "Casual Classical game"]
[Site "https://lichess.org/aBCEL1Zq"]
[Date "2018.07.11"]
[Round "-"]
[White "mie00"]
[Black "Omar_Elawady"]
[Result "0-1"]
[UTCDate "2018.07.11"]
[UTCTime "21:14:35"]
[WhiteElo "1579"]
[BlackElo "1614"]
[Variant "Standard"]
[TimeControl "900+15"]
[ECO "D06"]
[Opening "Queen's Gambit Refused: Marshall Defense"]
[Termination "Normal"]
[Annotator "lichess.org"]

1. d4 d5 2. c4 Nf6 { D06 Queen's Gambit Refused: Marshall Defense } 3. Nc3 Nc6 4. Bg5 e5 5. dxe5 Nxe5 6. Nxd5 Nxd5 7. Qxd5 Qxg5 8. a3 Bd6 9. c5 Bxc5 10. f4 Bf2+ 11. Kd1 Qxf4 12. Nf3 Nxf3 13. gxf3 O-O 14. Rg1 Bxg1 { White resigns. } 0-1
"""
)

animate_moves(moves_strings)
