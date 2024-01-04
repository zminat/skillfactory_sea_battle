from random import randint
from enum import Enum

SEPARATOR_SYMBOL_COUNT = 28
SHIP_PLACE_ATTEMPT_COUNT = 5000


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Ой! Попробуй еще раз. Доска только 6Х6. "


class BoardUsedException(BoardException):
    def __str__(self):
        return "Сюда ты уже стрелял! Попробуй еще раз."


class BoardWrongShipException(BoardException):
    pass


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Ship:
    def __init__(self, bow_point, size, orientation):
        self.bow_point = bow_point
        self.size = self.lives = size
        self.orientation = orientation

    @property
    def points(self):
        ship_points = []
        for i in range(self.size):
            ship_point_x = self.bow_point.x
            ship_point_y = self.bow_point.y

            if self.orientation == Orientation.HORIZONTAL:
                ship_point_x += i

            elif self.orientation == Orientation.VERTICAL:
                ship_point_y += i

            ship_points.append(Point(ship_point_x, ship_point_y))

        return ship_points


class Board:
    def __init__(self, hidden=False, size=6):
        self.size = size
        self.hidden = hidden

        self.destroyed_ship_count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.__occupied_points = []
        self.ships = []

    def add_ship(self, ship):
        for p in ship.points:
            if self.__is_point_out(p) or p in self.__occupied_points:
                raise BoardWrongShipException()
        for p in ship.points:
            self.field[p.x][p.y] = "■"
            self.__occupied_points.append(p)

        self.ships.append(ship)
        self.__mark_contour(ship)

    def __mark_contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for p in ship.points:
            for dx, dy in near:
                current_point = Point(p.x + dx, p.y + dy)
                if not (self.__is_point_out(current_point)) and current_point not in self.__occupied_points:
                    if verb:
                        self.field[current_point.x][current_point.y] = "T"
                    self.__occupied_points.append(current_point)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hidden:
            res = res.replace("■", "O")
        return res

    def __is_point_out(self, p):
        return not ((0 <= p.x < self.size) and (0 <= p.y < self.size))

    def shot(self, p):
        if self.__is_point_out(p):
            raise BoardOutException()

        if p in self.__occupied_points:
            raise BoardUsedException()

        self.__occupied_points.append(p)

        for ship in self.ships:
            if p in ship.points:
                ship.lives -= 1
                self.field[p.x][p.y] = "X"
                if ship.lives == 0:
                    self.destroyed_ship_count += 1
                    self.__mark_contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[p.x][p.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.__occupied_points = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def move(self):
        while True:
            try:
                target_point = self._ask()
                repeat = self.enemy_board.shot(target_point)
                return repeat
            except BoardException as e:
                print(e)

    def _ask(self):
        raise NotImplementedError()


class AI(Player):
    def _ask(self):
        while True:
            x, y = randint(0, 5), randint(0, 5)
            if self.enemy_board.field[x][y] != "O" and self.enemy_board.field[x][y] != "■":
                continue

            print(f"Ход ИИ: {x + 1} {y + 1}")
            return Point(x, y)


class User(Player):
    def _ask(self):
        while True:
            coords = input("Твой ход: ").split()

            if len(coords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Point(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size

        ai_board = self.random_board()
        ai_board.hidden = True

        user_board = self.random_board()

        self.ai = AI(ai_board, user_board)
        self.user = User(user_board, ai_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.__random_place()
        return board

    def __random_place(self):
        ship_sizes = [3, 2, 2, 1, 1, 1, 1]
        self.__ship_count = len(ship_sizes)
        board = Board(size=self.size)
        attempts = 0
        for ship_size in ship_sizes:
            while True:
                attempts += 1
                if attempts > SHIP_PLACE_ATTEMPT_COUNT:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), ship_size, Orientation(randint(0, 1)))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def __print_rules():
        print('    Игра "Морской бой"     ')
        Game.__print_separation_line()
        print("       Правила игры:       ")
        print("У каждого игрока (ты и ИИ) ")
        print("есть доска 6х6, на которой ")
        print("расставлены корабли:")
        print("1 корабль на 3 клетки;")
        print("2 корабля на 2 клетки;")
        print("4 корабля на 1 клетку.")
        print("Для того, чтобы сделать ")
        print("выстрел, введите координаты")
        print("ячейки в формате x y,")
        print("где x - номер строки,")
        print("а y - номер столбца.")
        print("За 1 ход игрок может указать")
        print("координаты только одной ячейки.")
        Game.__print_separation_line()
        print("Побеждает тот, кто быстрее ")
        print("всех разгромит корабли ")
        print("противника.")

    def __print_boards(self):
        num = 0
        while True:
            Game.__print_separation_line()
            print("Твое поле:")
            print(self.user.board)
            print("-" * SEPARATOR_SYMBOL_COUNT)
            print("Поле ИИ:")
            print(self.ai.board)

            if num % 2 == 0:
                current_player = self.user
                enemy_player = self.ai
            else:
                current_player = self.ai
                enemy_player = self.user

            Game.__print_separation_line()
            repeat = current_player.move()
            if repeat:
                num -= 1

            if enemy_player.board.destroyed_ship_count == self.__ship_count:
                Game.__print_separation_line()
                win_string = "Ты выиграл!" if enemy_player == self.ai else "Ты проиграл!"
                print(win_string)
                break

            num += 1

    def start(self):
        Game.__print_rules()
        self.__print_boards()

    @staticmethod
    def __print_separation_line():
        print("-" * SEPARATOR_SYMBOL_COUNT)


g = Game()
g.start()
