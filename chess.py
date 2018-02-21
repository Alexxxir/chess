import argparse
import threading
import time
import sys

try:
    from game import pieces, AI, being, play_debut, player, signals, graphics
    from game.constants import TypePlayer, Colour, StatesOfGame
except Exception as e:
    print('Игровые модули не найдены: "{}"'.format(e), file=sys.stderr)
    sys.exit(1)


class StartGame:
    def __init__(self, move):
        self._player_white = None
        self._player_black = None
        self._curr_player = None
        self.load = move

        def set_players():
            if self._curr_player == self._player_white:
                self._player_white = (self.player_dict
                                      [self.graphics.players[Colour.WHITE]](
                                       Colour.WHITE, self.game,
                                       self.game_signals, self.graphics))
                self._player_black = (self.player_dict
                                      [self.graphics.players[Colour.BLACK]](
                                       Colour.BLACK, self.game,
                                       self.game_signals, self.graphics))
                self._curr_player = self._player_white
            elif self._curr_player == self._player_black:
                self._player_white = (self.player_dict
                                      [self.graphics.players[Colour.WHITE]](
                                       Colour.WHITE, self.game,
                                       self.game_signals, self.graphics))
                self._player_black = (self.player_dict
                                      [self.graphics.players[Colour.BLACK]](
                                       Colour.BLACK, self.game,
                                       self.game_signals, self.graphics))
                self._curr_player = self._player_black
            else:
                self._curr_player = being.Being(Colour.COLORLESS,
                                                self.game,
                                                self.game_signals,
                                                self.graphics)

        self.game = pieces.Game()
        self.game_signals = signals.GameSignals(self.game)
        self.graphics = graphics.Graphics(self.game, self.game_signals)
        self.player_dict = {TypePlayer.PLAYER: player.Player,
                            TypePlayer.COMPUTER: AI.ArtificialIntelligence}
        set_players()
        self._curr_player = self._player_white

        def make_moves():
            def next_player():
                if self._curr_player == self._player_white:
                    return self._player_black
                else:
                    return self._player_white

            def load_game(load=None):
                """Загрузка игры """
                if load:
                    self.load = load
                colour_ = self.graphics.load_game(self.load)
                self.graphics.load_string = None
                if colour_ == Colour.BLACK:
                    self.graphics.set_title('Ход белых')
                    self._curr_player = self._player_white
                elif colour_ == Colour.WHITE:
                    self.graphics.set_title('Ход чёрных')
                    self._curr_player = self._player_black
                else:
                    self.graphics.list_of_moves.timer_white.stop_timer()
                    self.graphics.list_of_moves.timer_black.stop_timer()
                    self.graphics.set_title('Выберите ход с которого '
                                            'хотите продолжить игру')
                    self._curr_player = being.Being(Colour.COLORLESS,
                                                    self.game,
                                                    self.game_signals,
                                                    self.graphics)
                check_state_of_game()
                self.load = None

            def check_state_of_game():
                """Проверить текущее состояние игры
                                    и установить его в з заголовок"""
                result = ''
                for colour_ in [Colour.WHITE, Colour.BLACK]:
                    if self.game.desk.check_on_mate(
                            colour_) != StatesOfGame.RUN:
                        self.graphics.list_of_moves.timer_white.stop_timer()
                        self.graphics.list_of_moves.timer_black.stop_timer()
                        result = self.game.desk.check_on_mate(colour_)
                        if result == StatesOfGame.STALEMATE:
                            self.graphics.set_title('Пат. Ничья')
                        else:
                            if colour_ == Colour.WHITE:
                                self.graphics.set_title('Мат. Чёрные выиграли')
                            else:
                                self.graphics.set_title('Мат. Белые выиграли')
                    elif self.game.desk.check_on_check(colour_):
                        if colour_ == Colour.WHITE:
                            self.graphics.set_title('Белые под шахом')
                        else:
                            self.graphics.set_title('Чёрные под шахом')
                    if len(self.game.desk.list_of_pieces) == 2:
                        self.graphics.set_title('Ничья')
                return result
            while True:
                if self._curr_player.view == TypePlayer.PLAYER:
                    self.graphics.game_field.rotate_desk(
                        self._curr_player.colour)
                    if self.graphics.game_field.colour_of_heat_map:
                        self.graphics.game_field.show_heap_map(
                            self.graphics.game_field.colour_of_heat_map)
                if self.load:
                    self.graphics.menu.load_game(self.load)
                was_move = False
                if (not check_state_of_game() and
                        self.graphics.list_of_moves.list_of_moves.size() != 0):
                    if self._curr_player == self._player_white:
                        self.graphics.list_of_moves.timer_white.run_timer()
                    elif self._curr_player == self._player_black:
                        self.graphics.list_of_moves.timer_black.run_timer()
                if self._curr_player.make_move(
                        len(self.game.history_of_moves)):
                    if self.game_signals.end_game:
                        break
                    was_move = True
                    move_ = self.graphics.game_field
                    move_.make_move(self._curr_player.colour,
                                    self._curr_player.is_being,
                                    self.game_signals.move)
                self.graphics.list_of_moves.timer_white.stop_timer()
                self.graphics.list_of_moves.timer_black.stop_timer()
                time.sleep(0.2)
                if self.game_signals.end_game:
                    break
                self.graphics.game_field.unbind_possible_moves()
                game = self.graphics.list_of_moves.get_game()
                self.graphics.list_of_moves.set_debut_name(
                    *play_debut.choose_debut(game,
                                             self.game.debut))
                if self.graphics.game_field.colour_of_heat_map:
                    self.graphics.game_field.show_heap_map(
                        self.graphics.game_field.colour_of_heat_map)
                if self.game_signals.break_move:
                    if self.graphics.set_players:
                        colour = self.graphics.set_players[0]
                        player_ = self.graphics.set_players[1]
                        self.graphics.players[colour] = player_
                        set_players()
                        self.graphics.set_players = None
                    if (self.graphics.load_string or
                       self.graphics.load_string == 0):
                        if self.graphics.load_string != -1:
                            load_game()
                        else:
                            load_game(self.graphics.load_play)
                            self.graphics.load_play = None
                        if self.graphics.game_field.colour_of_heat_map:
                            self.graphics.game_field.show_heap_map(
                                self.graphics.game_field.colour_of_heat_map)
                        set_players()
                    self.game_signals.break_move = False
                if self.game_signals.new_game:
                    self.graphics.start_new_game()
                    if self.graphics.set_players:
                        colour = self.graphics.set_players[0]
                        player_ = self.graphics.set_players[1]
                        self.graphics.players[colour] = player_
                        set_players()
                        self.graphics.set_players = None
                    self.graphics.set_title('Ход белых')
                    self._curr_player = self._player_white
                    self.graphics.list_of_moves.start_new()
                    if self.graphics.game_field.colour_of_heat_map:
                        self.graphics.game_field.show_heap_map(
                            self.graphics.game_field.colour_of_heat_map)
                    self.game_signals.new_game = False
                    continue
                if was_move:
                    if self._curr_player != self._player_white:
                        self.graphics.set_title('Ход белых')
                    else:
                        self.graphics.set_title('Ход чёрных')
                    set_players()
                    self._curr_player = next_player()

        make_moves_start = threading.Thread(target=make_moves)
        make_moves_start.start()
        self.graphics.root.mainloop()


def main():
    def set_parser():
        parser_ = argparse.ArgumentParser()
        parser_.add_argument('-l', '--load', help='Файл с записью ходов',
                             type=argparse.FileType('r'))
        return parser_.parse_args()

    _parser = set_parser()
    StartGame(_parser.load)


if __name__ == '__main__':
    main()
