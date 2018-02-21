"""Модуль, реализующий фигуры и доску"""

from .coordinate import Coordinate
from .move import Move
from .constants import Colour, StatesOfGame


class Piece:
    """Шахматная фигура"""
    def __init__(self, x, y, colour, desk):
        self.x = x
        self.y = y
        self._colour = colour
        self._reduction = ''
        self._desk = desk
        self.was_moving = False

    def __str__(self):
        if self._colour == Colour.WHITE:
            color_str = 'w'
        else:
            color_str = 'b'
        return '{0}_{1}'.format(self._reduction, color_str)

    @property
    def colour(self):
        """Цвет фигуры"""
        return self._colour

    @colour.setter
    def colour(self, colour):
        self._colour = colour

    @property
    def reduction(self):
        """Обозначение фигуры"""
        return self._reduction


class Pawn(Piece):
    """Пешка"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = ""

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает список возможных ходов"""
        result = []
        if self._colour == Colour.WHITE:
            d_y = 1
            start_line = 1
        else:
            d_y = -1
            start_line = 6

        def start_move():
            """Если пешка находится на стартовой линии,
                                дополняет список возможных ходов"""
            if self.y == start_line:
                if (not self._desk.desk[self.x][self.y + 2 * d_y].piece and
                        not self._desk.desk[self.x][self.y + 1 * d_y].piece):
                    result.append(Coordinate(self.x, self.y + 2 * d_y))

        def cut_piece():
            """Если есть возможность побить фигуры противника,
                                дополняет список возможных ходов"""
            for d_x in [1, -1]:
                if Coordinate(self.x + d_x,
                              self.y + d_y).is_coordinate_on_desk():
                    if self._desk.desk[self.x + d_x][self.y + d_y].piece:
                        if (self._desk.desk[self.x + d_x][self.y + d_y]
                                .piece.colour != self._colour):
                            result.append(Coordinate(self.x + d_x,
                                                     self.y + d_y))

        def capturing_in_passing():
            """Если есть возможность осуществить взятие на проходе,
                                дополняет список возможных ходов"""
            if self._desk.last_move:
                piece = self._desk.last_move.piece
                coordinate = self._desk.last_move.coordinate
                if piece.reduction == '':
                    if (self.y == coordinate.y and
                        abs(self.x - coordinate.x) == 1 and
                            abs(piece.y - coordinate.y) == 2):
                        result.append(Coordinate(coordinate.x,
                                                 coordinate.y + d_y))

        def defend_():
            """Дополняет список координатами полей, находящихся
                                под защитой пешки"""
            if defend:
                for d_x in [1, -1]:
                    if Coordinate(self.x + d_x,
                                  self.y + d_y).is_coordinate_on_desk():
                        result.append(Coordinate(self.x + d_x,
                                                 self.y + d_y))

        if Coordinate(self.x, self.y + d_y).is_coordinate_on_desk():
            if not self._desk.desk[self.x][self.y + d_y].piece:
                result.append(Coordinate(self.x, self.y + d_y))
        start_move()
        cut_piece()
        capturing_in_passing()
        defend_()
        if check_on_check:
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class Rook(Piece):
    """Ладья"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "R"

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает список возможных ходов"""
        result = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if abs(i + j) == 1:
                    result += self._desk.move_to_direction(self,
                                                           i, j,
                                                           defend=defend)
        if check_on_check:
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class Knight(Piece):
    """Конь"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "N"

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает список возможных ходов"""
        result = []
        for i in range(self.x - 2, self.x + 3):
            for j in range(self.y - 2, self.y + 3):
                if (Coordinate(i, j).is_coordinate_on_desk() and
                   abs(i - self.x) + abs(j - self.y) == 3):
                    if (not self._desk.desk[i][j].piece or
                        self._desk.desk[i][j].piece and
                        self._desk.desk[i][j].piece.colour != self._colour or
                            defend):
                        result.append(Coordinate(i, j))
        if check_on_check:
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class Bishop(Piece):
    """Слон"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "B"

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает координаты возможных ходов"""
        result = []
        for i in [1, -1]:
            for j in [1, -1]:
                result += self._desk.move_to_direction(self,
                                                       i, j,
                                                       defend=defend)
        if check_on_check:
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class Heretic(Bishop):
    """Верблюд"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "H"


class Queen(Piece):
    """Ферзь"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "Q"

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает координаты возможных ходов"""
        result = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not i == j == 0:
                    result += self._desk.move_to_direction(self,
                                                           i, j,
                                                           defend=defend)
        if check_on_check:
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class King(Piece):
    """Король"""
    def __init__(self, x, y, colour, desk):
        super().__init__(x, y, colour, desk)
        self._reduction = "K"

    def possible_moves(self, check_on_check=True, defend=False):
        """Возвращает координаты возможных ходов"""
        result = []
        if defend:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if not i == j == 0:
                        if Coordinate(self.x + i,
                                      self.y + j).is_coordinate_on_desk():
                            result.append(Coordinate(self.x + i,
                                                     self.y + j))
            return result
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not i == j == 0:
                    if Coordinate(self.x + i,
                                  self.y + j).is_coordinate_on_desk():
                        if self._desk.desk[self.x + i][self.y + j].piece:
                            if (self._desk.desk[self.x + i][self.y + j].
                                    piece.colour != self._colour):
                                result.append(Coordinate(self.x + i,
                                                         self.y + j))
                        else:
                            result.append(Coordinate(self.x + i,
                                                     self.y + j))

        def short_castling():
            """Если есть возможность сделать короткую рокировку,
                    дополняет список возможных ходов"""
            if self._colour == Colour.WHITE:
                another_colour = Colour.BLACK
            else:
                another_colour = Colour.WHITE
            if not self._desk.desk[self.x + 3][self.y].piece:
                return
            elif (self._desk.desk[
                          self.x + 3][self.y].piece.reduction != 'R' or
                  self._desk.desk[
                          self.x + 3][self.y].piece.colour != self._colour or
                  self._desk.desk[
                          self.x + 3][self.y].piece.was_moving):
                return
            for step in range(0, 3):
                if (self._desk.check_on_possible(
                        Coordinate(self.x + step,
                                   self.y),
                        another_colour) or
                        (self._desk.desk[self.x + step][self.y].piece and
                            step != 0)):
                    return
            result.append(Coordinate(self.x + 2, self.y))

        def long_casting():
            """Если есть возможность сделать длинную рокировку,
                                дополняет список возможных ходов"""
            if self._colour == Colour.WHITE:
                another_colour = Colour.BLACK
            else:
                another_colour = Colour.WHITE
            if not self._desk.desk[self.x - 4][self.y].piece:
                return
            elif (self._desk.desk[
                          self.x - 4][self.y].piece.reduction != 'R' or
                    self._desk.desk[
                            self.x - 4][self.y].piece.colour != self._colour or
                    self._desk.desk[
                            self.x - 4][self.y].piece.was_moving):
                return
            for step in range(0, 3):
                if (self._desk.check_on_possible(
                        Coordinate(self.x - step,
                                   self.y),
                        another_colour) or
                        (self._desk.desk[self.x - step][self.y].piece and
                            step != 0) or
                        self._desk.desk[self.x - 3][self.y].piece):
                    return
            result.append(Coordinate(self.x - 2, self.y))

        if check_on_check:
            if (not self.was_moving and
                    (self._colour == Colour.WHITE and
                        self.x == 4 and self.y == 0 or
                        self._colour == Colour.BLACK and
                        self.x == 4 and self.y == 7)):
                short_castling()
                long_casting()
            result = self._desk.remove_invalid_moves(
                result,
                self._desk.desk[self.x][self.y].piece)
        return result


class ArrangePieces:
    """Расставить фигуры на доску по заданному шаблону"""
    def __init__(self, is_heretic=False):
        self._start_pieces = ["RNBQKBNR",
                              "pppppppp",
                              "--------",
                              "--------",
                              "--------",
                              "--------",
                              "pppppppp",
                              "RNBQKBNR"]
        self._colours_of_start_pieces = [[Colour.BLACK] * 8,
                                         [Colour.BLACK] * 8,
                                         [Colour.COLORLESS] * 8,
                                         [Colour.COLORLESS] * 8,
                                         [Colour.COLORLESS] * 8,
                                         [Colour.COLORLESS] * 8,
                                         [Colour.WHITE] * 8,
                                         [Colour.WHITE] * 8]
        if is_heretic:
            self._start_pieces[0] = "RNBQKHNR"
            self._start_pieces[7] = "RNHQKBNR"

    def arrange_pieces(self, desk, pieces=None, colours_of_pieces=None):
        """Расставить фигуры на доску по заданному шаблону"""
        for i in range(8):
            for j in range(8):
                desk.desk[i][j].piece = None
        desk.list_of_pieces.clear()
        if not pieces and not colours_of_pieces:
            pieces = self._start_pieces
            colours_of_pieces = self._colours_of_start_pieces
        for i in range(8):
            for j in range(8):
                if pieces[i][j] != '-':
                    desk.add_piece(Coordinate(j, 7 - i),
                                   pieces[i][j], colours_of_pieces[i][j])
        for i in range(8):
            for j in range(8):
                if desk.desk[i][j].piece:
                    desk.desk[i][j].count_visit[
                        desk.desk[i][j].piece.colour] += 1


class Desk:
    """Доска"""
    def __init__(self):
        self.desk = [None] * 8
        for i in range(8):
            self.desk[i] = [None] * 8
        for i in range(8):
            for j in range(8):
                self.desk[i][j] = Square()
        self.list_of_pieces = []
        self.last_move = None
        self._dict_of_pieces = {'p': Pawn,
                                '': Pawn,
                                'R': Rook,
                                'N': Knight,
                                'B': Bishop,
                                'Q': Queen,
                                'K': King,
                                'H': Heretic}

    def clear_desk(self):
        for i in range(8):
            for j in range(8):
                self.desk[i][j] = Square()
        self.list_of_pieces.clear()
        self.last_move = None

    def add_piece(self, coordinate, piece, colour):
        """Добавить фигуру на доску по заданным координатам и в список фигур"""
        x = coordinate.x
        y = coordinate.y
        add_piece = self._dict_of_pieces[piece](x, y, colour, self)
        self.list_of_pieces.append(add_piece)
        self.desk[x][y].piece = add_piece
        return add_piece

    def set_last_move(self, move):
        """Установить последний ход, сделанный на этой доске"""
        piece = self._dict_of_pieces[move.piece.reduction](
            move.piece.x,
            move.piece.y,
            move.piece.colour,
            self)
        self.last_move = Move(piece, Coordinate(move.coordinate.x,
                                                move.coordinate.y))

    def remove_invalid_moves(self, result, piece):
        """Убрать из списка ходов недопустимые"""
        coordinates = []
        for coordinate in result:
            test_desk = self.test_desk()
            test_desk.move_piece(None, test_desk.desk[piece.x][piece.y].piece,
                                 coordinate)
            if not test_desk.check_on_check(piece.colour):
                coordinates.append(coordinate)
        return coordinates

    def check_on_possible(self, coordinate, colour):
        """Проверить, является ли данный ход допустимым"""
        for piece in self.list_of_pieces:
            if piece.colour == colour:
                for possible_coordinate in piece.possible_moves(False):
                    if possible_coordinate == coordinate:
                        return True
        return False

    def add_piece_conversion(self, piece, colour, coordinate):
        """При превращении убрает пешку и добавдяет фигуру"""
        self.list_of_pieces.remove(self.desk[coordinate.x][coordinate.y].piece)
        self.desk[coordinate.x][coordinate.y].piece = None
        add_piece = self.add_piece(coordinate, piece, colour)
        return add_piece

    def move_to_direction(self, piece, d_x, d_y,
                          is_possible=True, defend=False):
        """Добавляет в список ходов координаты,
                        при движении в одном направлении"""
        result = []
        count = 1
        while Coordinate(piece.x + d_x * count,
                         piece.y + d_y * count).is_coordinate_on_desk():
            if self.desk[piece.x + d_x * count][piece.y + d_y * count].piece:
                if ((self.desk[piece.x + d_x * count][piece.y + d_y * count]
                        .piece.colour != piece.colour and
                        is_possible or
                        self.desk[piece.x + d_x * count][piece.y + d_y * count]
                            .piece.colour == piece.colour and
                        not is_possible) or
                        defend):
                    result.append(Coordinate(piece.x + d_x * count,
                                             piece.y + d_y * count))
                break
            result.append(Coordinate(piece.x + d_x * count,
                                     piece.y + d_y * count))
            count += 1
        return result

    def move_piece(self, game, piece, coordinate, another_piece=None):
        """Переместить фигуру на доске"""
        if not piece or not coordinate:
            return
        self.desk[coordinate.x][coordinate.y].count_visit[piece.colour] += 1
        piece.was_moving = True
        self.desk[piece.x][piece.y].piece = None
        if self.desk[coordinate.x][coordinate.y].piece:
            self.list_of_pieces.remove(
                self.desk[coordinate.x][coordinate.y].piece)
            self.desk[coordinate.x][coordinate.y].piece = None
            if piece.reduction == 'H':
                if piece.colour == Colour.WHITE:
                    piece.colour = Colour.BLACK
                else:
                    piece.colour = Colour.WHITE
        elif (piece.reduction == '' and
                abs(piece.x - coordinate.x) == abs(piece.y - coordinate.y)):
            try:
                self.list_of_pieces.remove(self.desk[coordinate.x][piece.y].
                                           piece)
            except ValueError:
                pass
            self.desk[coordinate.x][piece.y].piece = None
        if piece.reduction == 'K' and abs(piece.x - coordinate.x) == 2:
            if coordinate.x == 6:
                self.move_piece(None, self.desk[7][piece.y].piece,
                                Coordinate(5, piece.y))
            else:
                self.move_piece(None, self.desk[0][piece.y].piece,
                                Coordinate(3, piece.y))
        piece.x = coordinate.x
        piece.y = coordinate.y
        self.desk[coordinate.x][coordinate.y].piece = piece
        if another_piece:
            self.add_piece_conversion(another_piece,
                                      piece.colour, coordinate)
        if game:
            game.history_of_moves.append([self.test_desk(), self.last_move])

    def check_on_check(self, colour):
        """Проверить на шах"""
        for piece in self.list_of_pieces:
            if piece.colour != colour:
                for coordinate in piece.possible_moves(False):
                    if self.desk[coordinate.x][coordinate.y].piece:
                        if (self.desk[coordinate.x][coordinate.y]
                                .piece.reduction == 'K' and
                                self.desk[coordinate.x][coordinate.y].
                                piece.colour == colour):
                            return True
        return False

    def check_on_mate(self, colour):
        """Проверить на мат или пат"""
        count_of_possible_moves = 0
        for piece in self.list_of_pieces:
            if piece.colour == colour:
                count_of_possible_moves += len(piece.possible_moves())
        if count_of_possible_moves == 0:
            if self.check_on_check(colour):
                return StatesOfGame.CHECKMATE
            return StatesOfGame.STALEMATE
        return StatesOfGame.RUN

    def test_desk(self):
        """Копирует фигуры на тестовую доску и возвращает её"""
        test_desk = Desk()
        test_desk.list_of_pieces = []
        for piece in self.list_of_pieces:
            test_desk.list_of_pieces.append(
                self._dict_of_pieces[piece.reduction](piece.x,
                                                      piece.y,
                                                      piece.colour,
                                                      test_desk))
        for piece in test_desk.list_of_pieces:
            test_desk.desk[piece.x][piece.y].piece = piece
        for i in range(8):
            for j in range(8):
                test_desk.desk[i][j].count_visit[Colour.BLACK] = \
                    self.desk[i][j].count_visit[Colour.BLACK]
                test_desk.desk[i][j].count_visit[Colour.WHITE] = \
                    self.desk[i][j].count_visit[Colour.WHITE]
        return test_desk


class Square:
    """Поле на доске"""
    def __init__(self):
        self.piece = None
        self.count_visit = {Colour.BLACK: 0, Colour.WHITE: 0}


class Game:
    """Доска, на которой происходит игра"""
    def __init__(self, is_heretic=False):
        self._desk = Desk()
        self._arrange_pieces = ArrangePieces(is_heretic)
        self._arrange_pieces.arrange_pieces(self._desk)
        self.history_of_moves = []
        self.debut = None

    @property
    def desk(self):
        return self._desk

    def load_desk(self, ind):
        self._desk = self.history_of_moves[ind][0]

    def new_game(self, is_heretic=False):
        """Создать новую игру"""
        self.__init__(is_heretic)
