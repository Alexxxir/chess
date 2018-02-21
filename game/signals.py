"""Модуль, хранящий сигналы игры"""

from .move import MoveStr
from .constants import Colour


class GameSignals:
    """Сигналы игры"""
    def __init__(self, game):
        self._game = game
        self.new_game = False
        self.break_move = False
        self.end_game = False
        self.move = None
        self.last_move = ''
        self.rotate_field = Colour.WHITE
        self.is_heretic = False

    def set_move(self, move_str, colour):
        """Устанавливает информацию о ходе, возвращает True в случаи успеха,
                        False в случаи неудачи"""
        if not self.break_move and not self.new_game:
            move = MoveStr(move_str, self._game, colour)
            if move.piece and move.coordinate:
                self.move = move
                return True
            return False
