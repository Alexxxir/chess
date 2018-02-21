from .being import Being
from .constants import TypePlayer


class Player(Being):
    """Игрок, ведущий игру, посредством игрового поля"""
    def __init__(self, colour, game, game_signals, graphic):
        super().__init__(colour, game, game_signals, graphic)
        self.view = TypePlayer.PLAYER
        self._graphic = graphic

    def move_method(self, number_of_stroke=0):
        """Метод, устанавливающий ход в класс 'Сигналы игры'"""
        self._graphic.game_field.bind_possible_moves(self.colour)
