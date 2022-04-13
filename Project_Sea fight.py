from random import randint

class BoardException(Exception): #Создание общего Исключений???
    pass

class BoardOutException(BoardException): #Создание Исключения выстрела вне поля
    def __str__(self):
        return 'Вы выстрелили за доску!'

class BoardUsedException(BoardException): #Создания Исключения повторного выстрела
    def __str__(self):
        return 'Данная клетка уже обстреливалась!'

class BoardShipException(BoardException): #Создание Исключения для безошибочного размещения короблей
    pass
# -------------------------------------------

class Dot: # Класс точки
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):# Проверка совпадения координат
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

#------------------------------------------------------

class Ship: #Создание класса корабль

    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self): # Создание координат коробля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return  ship_dots

    def shooten(self, shot): #Проверка совпадения координат выстрела с координатами коробля
        return shot in self.dots
#-----------------------------------------------------

class Board: #Создание класса доска

    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.zone = [[' '] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self): #Вывод игрового поля
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |\n'
        for i, j in enumerate(self.zone):
            res +='---------------------------\n'
            res += f'{i + 1} | {" | ".join(j)} |\n'

        if self.hid:
            res = res.replace('N', ' ')
        return res

    def out(self, d): #Проверка надодятся ли координаты точки в перделах поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False): #Очерчивает контур коробля по кругу на 1 деление
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
            ] # Список смещений вокруг исходной точки
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.zone[cur.x][cur.y] = '*'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardShipException()
        for d in ship.dots:
            self.zone[d.x][d.y] = 'N'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d): #Выстрел по доске

        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise  BoardUsedException()

        self.busy.append(d)

        for ship in self.ships: #Проверка выстрела
            if ship.shooten(d):
                ship.lives -= 1
                self.zone[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Убил!')
                    return False
                else:
                    print("Ранил")
                    return True

        self.zone[d.x][d.y] = '*'
        print('Промазал!')
        return False

    def begin(self):
        self.busy = []

#--------------------------------------------------------------------------------------

class Player: #Создания класса играка

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise  NotImplementedError()

    def move(self): #бесконечный цикл для выстрела
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BaseException as e:
                print(e)

class AI(Player): #Создания класса Игрок-Компьютер

    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход противник: {d.x + 1} {d.y + 1}')
        return d

class User(Player): #Создания класса Игрок-Пользователь

    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print('Введите 2 (две) координаты! ')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x) - 1, int(y) - 1

            return Dot(x, y)

#----------------------------------------------------------------------

class Game: #Создание класса игры

    def __init__(self, size = 6): #создание тгрофх полей для 2 игроков
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True #скрывание короблей на поле Компьютера

        self.ai = AI(co, pl)
        self.us = User(pl, co)



    def try_board(self): #создание поля с короблями
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardShipException:
                    pass

        board.begin()
        return board

    def random_board(self): # генератор поля для исключения случая не создания поля
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print('Приветсвуем Вас в игре \n'
              '   "Морской бой"! \n'
              'Форма ввода:\n'
              'X - номер строки;'
              'Y - номер столбца.\n'
              'Нажмите Enter чтобы начать\n'
              '_____________________________')
        start = input()  # Старт игры полсе прочтения правил

    def loop(self): #игровой цикл

        num = 0

        while True:
            print('-' * 20)
            print('Доска пользователя')
            print(self.us.board)
            print('-' * 20)
            print('Доска компьютера')
            print(self.ai.board)
            print('-' * 20)
            if num%2 == 0:
                print('Ход пользователя')
                repeat = self.us.move()
            else:
                print('Ход компьютер')
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print('-' * 20)
                print('Выйграл - Пользователь')
                print(self.ai.board)
                break

            if self.us.board.count == 7:
                print('-' * 20)
                print('Выйграл - Компьютер')
                print(self.us.board)
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()