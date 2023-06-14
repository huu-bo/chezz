from stockfish import Stockfish


class NotaSyntaxException(Exception):
    # 'l' is incorrect length
    # 's' is incorrect size (split[0])
    # 'p' is incorrect starting pos

    pass


class Board:
    def __init__(self, start=''):
        if start == '':
            with open('default-start.txt', 'r') as file:
                start = file.read().replace('\n', '')

        print(start)
        # TODO: nota currently does not support en passant
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
