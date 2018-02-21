from .constants import TypePlayer


class Being:
    """Шаблон для всех игроков, так же используется,
                чтобы поставить игру на паузу"""
    def __init__(self, colour, game, game_signals, graphic):
        self.colour = colour
        self._game = game
        self._game_signals = game_signals
        self.is_being = True
        self.view = TypePlayer.WAITING

    def make_move(self, number_of_stroke):
        """Возвращает ход, сделанный игроком"""
        self.move_method(number_of_stroke)
        while True:
            if self._game_signals.new_game:
                break
            if self._game_signals.break_move:
                self._game_signals.move = None
                break
            if self._game_signals.end_game:
                break
            if self._game_signals.move:
                break
        return self._game_signals.move

    def move_method(self, number_of_stroke):
        """Метод, устанавливающий ход в класс 'Сигналы игры'"""
        pass
