def eliminate_comments(pgn_defintion):
    res = ""
    in_comment = False
    comment_type = ";"
    for c in pgn_defintion:
        if in_comment:
            if comment_type == ";" and c == "\n":
                if c == "\n":
                    res += "\n"
                in_comment = False
            elif comment_type == "{" and c == "}":
                in_comment = False
        else:
            if c == "{":
                in_comment = True
                comment_type = "{"
            elif c == ";":
                in_comment = True
                comment_type = ";"
            else:
                res += c
    return res


def extract_moves(pgn_defintion):
    without_comments = eliminate_comments(pgn_defintion)
    moves = without_comments.replace("\n", " ").split(" ")
    result = []
    for e in moves:
        if e and not e[0].isdigit():
            result.append(e)
    return result


def parse_pgn(game_description):
    pgn_defintion = ""
    for line in game_description.split("\n"):
        if not line or line[0] == "[":
            continue
        else:
            pgn_defintion += line + "\n"

    moves = extract_moves(pgn_defintion)
    return moves
