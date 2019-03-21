import random

number_emotes = (
    "0\N{COMBINING ENCLOSING KEYCAP}",
    "1\N{COMBINING ENCLOSING KEYCAP}",
    "2\N{COMBINING ENCLOSING KEYCAP}",
    "3\N{COMBINING ENCLOSING KEYCAP}",
    "4\N{COMBINING ENCLOSING KEYCAP}",
    "5\N{COMBINING ENCLOSING KEYCAP}",
    "6\N{COMBINING ENCLOSING KEYCAP}",
    "7\N{COMBINING ENCLOSING KEYCAP}",
    "8\N{COMBINING ENCLOSING KEYCAP}",
    "9\N{COMBINING ENCLOSING KEYCAP}",
)

bomb_emote = "\N{BOMB}"


def get_cell(mines, x, y):
    if (x, y) in mines:
        return bomb_emote
    else:
        bombs = 0
        for cy in (y+1, y, y-1):
            for cx in (x+1, x, x-1):
                if (cx, cy) in mines:
                    bombs = bombs+1
        return number_emotes[bombs]


def generate_board(size_x, size_y, minecount: int):
    mines = [(random.randrange(0, size_x), random.randrange(0, size_y)) for _ in range(minecount)]
    field = [[get_cell(mines, x, y) for x in range(size_x)] for y in range(size_y)]
    return "\n".join(("||"+"||||".join(row)+"||") for row in field)
