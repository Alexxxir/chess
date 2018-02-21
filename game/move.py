"""Модуль содержащих классы, задающие информацию о ходе"""

from .coordinate import Coordinate
from .constants import Colour


class Move:
    """Информация о ходе"""
    def __init__(self, piece, coordinate):
        self.piece = piece
        self.coordinate = coordinate


class MoveStr(Move):
    """Преобразует строковое представление хода
                        в фигуру и координату'"""
    def __init__(self, move_string, game, colour):
        try:
            self.piece = None
            self.coordinate = None
            self._another_piece = None
            if colour == Colour.WHITE:
                start_line = 0
            else:
                start_line = 7
            ind_of_separator = ''
            move_string = move_string.replace(' ', '')
            for i in range(len(move_string)):
                if move_string[i] == '.':
                    move_string = move_string[i + 1:]
                    break
            if move_string == '0-0':
                self.piece = game.desk.desk[4][start_line].piece
                self.coordinate = Coordinate(6, start_line)
                return
            if move_string == '0-0-0':
                self.piece = game.desk.desk[4][start_line].piece
                self.coordinate = Coordinate(2, start_line)
                return
            for i in range(len(move_string)):
                if move_string[i] == '-' or move_string[i] == 'x':
                    ind_of_separator = i
                    break
            if (ind_of_separator == '' or
               len(move_string) < 5 or ind_of_separator <= 1):
                return
            piece_reduction = move_string[:ind_of_separator - 2]
            piece_coordinates = move_string[ind_of_separator - 2:
                                            ind_of_separator]
            move_coordinates = move_string[ind_of_separator + 1:
                                           ind_of_separator + 3]
            if len(move_string) > ind_of_separator + 3:
                another_piece = move_string[ind_of_separator + 3]
                for piece in game.desk._dict_of_pieces:
                    if piece == another_piece:
                        self._another_piece = another_piece
            piece_x = ord(piece_coordinates[0]) - 97
            piece_y = int(piece_coordinates[1]) - 1
            move_x = ord(move_coordinates[0]) - 97
            move_y = int(move_coordinates[1]) - 1
            for coordinate in [piece_x, piece_y, move_x, move_y]:
                if coordinate < 0 or coordinate > 7:
                    return
            if game.desk.desk[piece_x][piece_y].piece:
                if (game.desk.desk[piece_x][piece_y].piece.reduction ==
                        piece_reduction):
                    for coordinate in game.desk.desk[piece_x][piece_y].\
                                      piece.possible_moves():
                        if coordinate == Coordinate(move_x, move_y):
                            self.piece = game.desk.desk[piece_x][piece_y].piece
                            self.coordinate = Coordinate(move_x, move_y)

        except Exception:
            pass
