from stockfish import Stockfish


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

        i = 0
        state = 'LHS piece'
        piece = ''
        rules = split[2]
        rule = []
        while i < len(rules):
            c = rules[i]

            print(i, c, state)

            if state == 'LHS piece':
                piece = rules[i:i+2]
                i += 2
                state = 'LHS comma'
                continue
            elif state == 'LHS comma':
                if c == ',':
                    state = 'LHS'
                elif c == ':':
                    state = 'RHS'
                else:
                    raise NotaSyntaxException('r,')
            elif state == 'LHS':
                rule = []

                if c not in 'xy':
                    raise NotaSyntaxException('rxy')

                if rules[i+1] == 'l':
                    raise NotImplementedError
                else:
                    if rules[i+1] not in '-+=':
                        raise NotaSyntaxException('rLHS-+=' + rules[i+1])
            else:
                print(state)
                assert False

            i += 1


def nota_rule(s: str):
    split = s.split(':')
    if len(split) != 2:
        raise NotaSyntaxException("missing ':'")
    out = [nota_lhs(split[0]), nota_rhs(split[1])]
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
    rule = []
    state = 'dir'
    for i, c in enumerate(s):
        if state == 'dir':
            if c not in 'lxy':
                raise NotaSyntaxException(f"unknown direction '{c}'")
            rule.append(c)
            state = 'op'
        elif state == 'op':
            if c not in '+-=':
                if c.isdigit():
                    state = 'abspos'
                    rule.append(c)
                    continue
                else:
                    raise NotaSyntaxException(f"unknown operation '{c}'")
            rule.append(c)
            rule.append('')
            state = 'num'
        elif state == 'num':
            if not c.isdigit():
                if c in ' #*':
                    out.append(rule)
                    out = ['POS', out, c]
                    return out
                if c == '=':
                    state = 'piece'
                    out.append(rule)
                    rule = ['']
                    continue
                if c != '+':
                    raise NotaSyntaxException(f"unexpected token '{c}'")
                out.append(rule)
                rule = []
                state = 'dir'
            else:
                rule[-1] += c
        elif state == 'abspos':
            if not c.isdigit():
                if c not in '+=':
                    raise NotaSyntaxException(f"unknown operation '{c}'")

                if s[i+1].isdigit():
                    state = 'num'
                elif c == '+':
                    out.append(rule)
                    rule = []
                    state = 'dir'
                else:
                    out.append(rule)
                    rule = ['']
                    state = 'piece'
                continue

            if not s[i+1].isdigit():
                state = 'op'
            else:
                rule[-1] += c
        elif state == 'piece':
            rule[-1] += c
            if len(rule[-1]) == 2:
                out = ['POS', out, rule[0]]
                return out
        # elif state == 'com':
        #     if c != '+':
        #         raise NotaSyntaxException(f"unexpected token '{c}'")
        #     state = 'dir'
        else:
            assert False


def nota_rhs(s: str):
    out = []

    split = s.split(',')
    if len(split) == 0:
        raise NotaSyntaxException('no rhs')

    for subs in split:
        out.append(nota_rhs_rule(subs))

    return out


def nota_rhs_rule(s: str):
    if s[0] not in 'lxy':
        raise NotaSyntaxException(f"unexpected direction '{s[0]}'")
    if s[1].isdigit():
        return nota_rhs_abs_pos(s)
    elif s[1] not in '+-=':
        raise NotaSyntaxException(f"unexpected operation '{s[1]}'")

    if s[1] == '=':
        if len(s[2:]) != 2:
            raise NotaSyntaxException(f"literal of unexpected length '{s[2:]}'")
    else:
        if not s[2:].isdigit():
            raise NotaSyntaxException(f"unexpected non-number literal '{s[2:]}'")

    return ['MOVE', s[0], s[1], s[2:]]


def nota_rhs_abs_pos(s: str):
    i = 0
    out = ['MOVE', []]
    while i < len(s):
        if s[i] not in 'xy':
            raise NotaSyntaxException(f"unexpected direction '{s[i]}'")

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
                raise NotaSyntaxException(f"expected piece but got '{piece}' (should have a length of 2)")

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

# board = Board()
