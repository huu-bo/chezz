from stockfish import Stockfish
from pprint import pprint as print


class NotaSyntaxException(Exception):
    # 'l' is incorrect length
    # 's' is incorrect size (split[0])
    # 'p' is incorrect starting pos

    pass


class State:
    def __init__(self, piece: str, line: bool, l_positions: list):
        self.piece = piece
        self.line = line
        self.l_positions = l_positions


class Nota_l_Position:
    def __init__(self, direction: str, operation: str, value: int, place_value: str, line: bool):
        if type(direction) != str:
            raise ValueError
        if direction not in 'xy':
            raise ValueError
        if type(operation) != str:
            raise ValueError
        if operation not in '-+=':
            raise ValueError
        if type(line) != bool:
            raise ValueError
        if type(value) != int:
            raise ValueError
        if type(place_value) != str:
            raise ValueError
        if place_value not in [' ', '*', '#',
                               ' x', '*x', '#x',
                               ' X', '*X', '#X']:
            raise ValueError

        self.direction = direction
        self.operation = operation
        self.value = value
        self.place_value = place_value
        self.line = line


class Nota_r_Position:
    def __init__(self, direction: str, operation: str, value, line: bool):
        if type(direction) != str:
            raise ValueError
        if direction not in 'xy':
            raise ValueError
        if type(operation) != str:
            raise ValueError
        if operation not in '-+=':
            raise ValueError
        if type(line) != bool:
            raise ValueError
        if type(value) not in [str, int]:
            raise ValueError

        self.direction = direction
        self.value = value
        self.line = line


class Board:
    def __init__(self, start=''):
        if start == '':
            with open('default-start.txt', 'r') as file:
                start = file.read().replace('\n', '')

        print(start)
        # TODO: better error messages
        # TODO: make a file in which users can store Notas with names
        # TODO: parse rules

        split = start.split(' ')
        if len(split) != 4:
            raise NotaSyntaxException('l')

        self.size_raw = split[0]
        size_split = self.size_raw.split('x')
        if len(size_split) != 2:
            raise NotaSyntaxException('s')
        try:
            self.size = (int(size_split[0]), int(size_split[1]))
        except ValueError:
            raise NotaSyntaxException('s')
        if self.size[0] <= 0 or self.size[1] <= 0:
            raise NotaSyntaxException('s')

        self.board = []
        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                row.append('..')
            self.board.append(row)

        if len(split[1]) % 2 != 0:
            raise NotaSyntaxException('p')

        x = 0
        y = 0
        for i in range(0, len(split[1]), 2):
            p = split[1][i:i+2]
            if p[0] != '.' and not p[0].isdigit():
                if y >= self.size[1]:
                    raise NotaSyntaxException(f'py{y}')

                self.board[y][x] = p
            else:
                if p[1] == '.':
                    pass
                else:
                    try:
                        if p[0] == '.':
                            skip = int(p[1])
                        else:
                            skip = int(p)
                    except ValueError:
                        raise NotaSyntaxException('p')
                    y = skip
                    x = 0
                    continue
            x += 1
            if x % self.size[0] == 0:
                x = 0
                y += 1

        rules = split[2].split(';')
        self.rules = []
        for rule in rules:
            self.rules.append(nota_rule(rule))
        print(self.rules)


def nota_rule(s: str):
    split = s.split(':')
    if len(split) != 2 and len(s.split('=')) != 2:
        raise NotaSyntaxException("missing ':'")
    elif len(s.split('=')) == 2 and len(split) != 2:

        out = ['DELAY', s[0:2]]

        try:
            i = 3
            while s[i] != '(':
                i += 1
        except IndexError:
            raise NotaSyntaxException(f"delay with nothing to turn into '{s}'")
        out.append(s[3:i])
        out.append(s[i+1:i+3])

        if s[i+3] != ')':
            raise NotaSyntaxException(f"missing ')' in '{s}'")
    else:
        out = ['RULE', nota_lhs(split[0]), nota_rhs(split[1])]
    return out


def nota_lhs(s: str):
    out = []

    split = s.split(',')
    if len(split) == 0:
        raise NotaSyntaxException('no lhs')

    for subs in split:
        out.append(nota_lhs_rule(subs))

    return out


def nota_lhs_rule(s: str) -> list:
    if len(s) == 2:
        return ['PIECE', s]

    out = []
    state = ''
    t = []
    i = 0
    while i < len(s):
        if i != 0 and s[i] == '+':
            i += 1

        if s[i] in '.#*':
            out.append(t)
            state = s[i]
            break

        if s[i] not in 'xyld':
            raise NotaSyntaxException(f"unknown direction '{s[i]}' in lhs rule '{s}'")
        t.append(s[i])
        if s[i] in 'xyd':
            if s[i+1] == 'l':
                t.append('l')
                i += 2
            elif s[i+1] == 'L':
                t.append('L')
                if s[i+2] not in '-+' and (s[i] == 'd' and s[i+2] not in '0123'):
                    raise NotaSyntaxException(f"unknown direction '{s[i+2]}' in lhs rule '{s}'")
                t.append(s[i+2])
                i += 3
            elif s[i+1] in '+-':
                t.append(s[i+1])
                i += 1
            elif s[i+1] == '=':
                i += 1
            else:
                raise NotaSyntaxException(f"unexpected token '{s[i+1]}' in lhs rule '{s}'")
        else:
            raise NotaSyntaxException(f"unknown direction '{s[i]}' in lhs rule '{s}'")

        if s[i] in '-+':
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            t.append(s[i+1:j])
            i = j
        elif s[i] == '=':
            t.append('=')
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            t.append(s[i+1:j])
            i = j
        elif s[i] in '.#*':
            pass
        else:
            raise NotaSyntaxException(f"unknown token '{s[i]}' in lhs rule '{s}'")

        out.append(t)
        t = []

    out = list([o for o in out if o])

    return ['POS', out, state]


def nota_rhs(s: str):
    out = []

    split = s.split(',')
    if len(split) == 0:
        raise NotaSyntaxException('no rhs')

    for subs in split:
        out.append(nota_rhs_rule(subs))

    return out


def nota_rhs_rule(s: str):
    if len(s) == 2:
        return ['PIECE', s]
    if s[0] not in 'lxy':
        raise NotaSyntaxException(f"unexpected direction '{s[0]}' in rhs rule '{s}'")

    if s[0] == 'l':
        if len(s) != 1:
            raise NotaSyntaxException(f"unexpected token(s) '{s[1:]}' in rhs rule '{s}'")

        return ['LINE']

    if s[1].isdigit():
        return nota_rhs_abs_pos(s)
    elif s[1] not in '+-=':
        raise NotaSyntaxException(f"unexpected operation '{s[1]}' in rhs rule '{s}'")

    if s[1] == '=':
        if len(s[2:]) != 2:
            raise NotaSyntaxException(f"literal of unexpected length '{s[2:]}' in rhs rule '{s}'")
    else:
        if not s[2:].isdigit():
            i = 2
            while s[i].isdigit():
                i += 1
            offset = s[2:i]
            piece = s[i+1:]
            if len(piece) != 2:
                raise NotaSyntaxException(f"expected piece but got '{piece}' (should have a length of 2) in rhs rule '{s}'")

            return ['SET', s[0], s[1], offset, piece]

            # raise NotaSyntaxException(f"unexpected non-number literal '{s[2:]}' in rhs rule '{s}'")

    return ['MOVE', s[0], s[1], s[2:]]


def nota_rhs_abs_pos(s: str):
    i = 0
    out = ['MOVE', []]
    while i < len(s):
        if s[i] not in 'xy':
            raise NotaSyntaxException(f"unexpected direction '{s[i]}' in rhs abs rule '{s}'")

        j = i + 1
        while s[j].isdigit():
            j += 1
        pos = s[i+1:j]

        out[-1].append([s[i], pos])
        if s[j] != '=':
            if s[j] == '+':
                j += 1
            i = j
        else:
            piece = s[j+1:]
            if len(piece) != 2:
                raise NotaSyntaxException(f"expected piece but got '{piece}' (should have a length of 2) in rhs abs rule '{s}'")

            return out + [piece]


# print(nota_lhs('wp,y-1+x+1#,x1+y2=bp'))
# print(nota_lhs('wp,y-1+x+1=wp'))
# print(nota_rule('wp,y-1+x+1#,x1+y2=bp:y-1,x+1,x1+y1=..'))

# stockfish = Stockfish(depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
# print(stockfish.get_fen_position())
#
# stockfish.set_position(["e2e4", "e7e6"])
#
# # print(stockfish.get_best_move())
# print(stockfish.get_fen_position())
#
# print(stockfish.get_evaluation())

board = Board()
