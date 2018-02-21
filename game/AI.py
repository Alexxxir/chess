"""Модуль реализующий искусственный интеллект"""

import random
from .coordinate import Coordinate
from .move import Move
from .player import Player
from .constants import TypePlayer, Colour, StatesOfGame
from .play_debut import choose_move


MAX_WEIGHT = 10
MIN_WEIGHT = 0


class SquareInfo:
    """Информация о фигурах, атакующих поле"""
    def __init__(self):
        self.under_possible = {Colour.WHITE: MAX_WEIGHT,
                               Colour.BLACK: MAX_WEIGHT}


class ArtificialIntelligence(Player):
    """Искусственный интеллект"""
    def __init__(self, colour, game, game_signals, graphic):
        super().__init__(colour, game, game_signals, graphic)
        self.is_being = False
        self.view = TypePlayer.COMPUTER
        self._evaluation_of_positions = {}
        self._weight_of_pieces = {'K': -1, 'Q': 9, 'R': 5,
                                  'B': 3, 'N': 3, '': 1, 'H': 3}

    def move_method(self, number_of_stroke=0):
        """Метод, устанавливающий ход в класс 'Сигналы игры'"""
        if self._game.desk.check_on_mate(self.colour) != StatesOfGame.RUN:
            return
        self._evaluation_of_positions.clear()
        for piece in self._game.desk.list_of_pieces:
            if piece.colour == self.colour:
                for coordinate in piece.possible_moves():
                    test_desk = self._game.desk.test_desk()
                    self._evaluation_of_positions[
                        piece, coordinate] = self.evaluation_of_position(
                            test_desk, piece, coordinate)
        max_priority = -(10 ** 11)
        best_move = None
        for key in self._evaluation_of_positions:
            if self._evaluation_of_positions[key] > max_priority:
                max_priority = self._evaluation_of_positions[key]
                best_move = key
        if max_priority >= 2 * 10**6 or number_of_stroke > 8:
            self._game_signals.move = Move(best_move[0], best_move[1])
            return True
        set_move_str = False
        for _ in range(5):
            move_str = choose_move(
                self._game_signals.last_move)
            if move_str:
                set_move_str = self._game_signals.set_move(move_str,
                                                           self.colour)
                if set_move_str:
                    break
        if not set_move_str:
            self._game_signals.move = Move(best_move[0], best_move[1])
            return True
        return True

    def evaluation_of_position(self, desk, piece, coordinate):
        """Метод, оценивающий сделанный ход, возвращает оценку данного хода"""
        def init_dict_of_squares():
            """Устанавливет словарь, сопоставляющий каждому полю информацию о фигурах
                                его атакующих"""
            dict_of_squares_ = {}
            for i in range(8):
                for j in range(8):
                    dict_of_squares_[Coordinate(i, j)] = SquareInfo()
            for piece__ in desk.list_of_pieces:
                for coordinate__ in piece__.possible_moves(False, True):
                    if (self._weight_of_pieces[piece__.reduction] <
                            dict_of_squares_[coordinate__].
                            under_possible[piece__.colour] and
                            self._weight_of_pieces[piece__.reduction]):
                        dict_of_squares_[coordinate__].under_possible[
                            piece__.colour] = self._weight_of_pieces[
                                piece__.reduction]
            for i in range(8):
                for j in range(8):
                    curr_coord = Coordinate(i, j)
                    if (dict_of_squares_[curr_coord].
                            under_possible[Colour.WHITE] == MAX_WEIGHT):
                        dict_of_squares_[
                            curr_coord].under_possible[Colour.WHITE] = MIN_WEIGHT
                    if dict_of_squares_[
                            curr_coord].under_possible[Colour.BLACK] == MAX_WEIGHT:
                        dict_of_squares_[
                            curr_coord].under_possible[Colour.BLACK] = MIN_WEIGHT
            return dict_of_squares_

        if self.colour == Colour.WHITE:
            another_colour = Colour.BLACK
        else:
            another_colour = Colour.WHITE
        priority = 0
        possibleed_piece = desk.desk[coordinate.x][coordinate.y].piece
        if possibleed_piece:
            priority += 10 ** 6 * self._weight_of_pieces[possibleed_piece
                                                         .reduction]
            if piece.reduction == 'H':
                priority -= 10 ** 6 * 6
        desk.move_piece(None, desk.desk[piece.x][piece.y].piece, coordinate)
        if desk.check_on_mate(another_colour) == StatesOfGame.CHECKMATE:
            priority += 10 ** 10
        if desk.check_on_mate(another_colour) == StatesOfGame.STALEMATE:
            priority -= 10 ** 10
        if piece.reduction == 'K':
            if abs(piece.x - coordinate.x) == 2:
                priority += 10 ** 4
            else:
                priority -= 10 ** 4
        if self.colour == Colour.WHITE:
            priority += (coordinate.y - piece.y) * 10 ** 2
        else:
            priority += (piece.y - coordinate.y) * 10 ** 2
        if 1 < coordinate.x < 6 and 1 < coordinate.y < 6:
            priority += 10 ** 1
        dict_of_squares = init_dict_of_squares()
        the_worst_priority = 0
        for piece_ in desk.list_of_pieces:
            if piece_.colour == self.colour:
                if (dict_of_squares[Coordinate(
                        piece_.x, piece_.y)].
                        under_possible[another_colour] and not
                        dict_of_squares[Coordinate(
                            piece_.x, piece_.y)].under_possible[self.colour]):
                    if (the_worst_priority <
                            self._weight_of_pieces[piece_.
                                                   reduction] * 10 ** 6):
                        the_worst_priority = self._weight_of_pieces[
                                                 piece_.reduction] * 10 ** 6
                elif (dict_of_squares[Coordinate(
                        piece_.x, piece_.y)].
                        under_possible[another_colour] and
                        dict_of_squares[Coordinate(
                            piece_.x, piece_.y)].under_possible[self.colour]):
                    if (dict_of_squares[Coordinate(
                            piece_.x, piece_.y)].under_possible[self.colour] <
                            self._weight_of_pieces[piece_.reduction]):
                        if (the_worst_priority <
                                (self._weight_of_pieces[piece_.reduction] -
                                    dict_of_squares[Coordinate(
                                        piece_.x, piece_.y)].under_possible[
                                        self.colour]) * 10 ** 6):
                            the_worst_priority = (self._weight_of_pieces[
                                piece_.reduction] - dict_of_squares[
                                Coordinate(piece_.x, piece_.y)].
                                    under_possible[self.colour]) * 10 ** 6
        if the_worst_priority:
            priority -= the_worst_priority
        priority -= 5 * 10 * self._weight_of_pieces[piece.reduction]
        priority += int(random.random() * 10)
        return priority
