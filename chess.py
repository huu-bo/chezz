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
    out = []
    split = s.split(':')
    if len(split) != 2:
        raise NotaSyntaxException("missing ':'")


print(nota_rule('wp,y-1.:y-1'))

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
