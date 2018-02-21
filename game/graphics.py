"""Модуль, реализующий графическое представление игры"""

import copy
import time
import tkinter as tk
import sys
import tkinter.filedialog as fd
from PIL import ImageTk, Image
from .coordinate import Coordinate
from .move import Move
from .move import MoveStr
from .constants import TypePlayer, Colour, StatesOfGame
from .play_debut import choose_debut
from .load_info import LoadInfo


TIME_MOVE = 0.5


class ImagesOfPiece:
    """Изображения фигур"""
    def __init__(self, piece, graphics):
        self._image = ImageTk.PhotoImage(
            Image.open('images/{}.png'.format(str(piece))))
        self.image_moves = ImageTk.PhotoImage(
            Image.open('images/__{}.png'.format(str(piece))))
        if graphics.game_signals.rotate_field == Colour.WHITE:
            self.picture = graphics.game_field.canvas.create_image(
                piece.x * 60 + 30, (7 - piece.y) * 60 + 30,
                image=self._image, anchor="nw")
        else:
            self.picture = graphics.game_field.canvas.create_image(
                (7 - piece.x) * 60 + 30, piece.y * 60 + 30,
                image=self._image, anchor="nw")


class ChoosePiece:
    """Окно выбора фигуры для превращения"""
    def __init__(self, root, is_being):
        self.piece = ''
        if not is_being:
            self.piece = 'Q'
            return
        self._ask = tk.Toplevel(root)
        self._ask.geometry('110x110+300+300')
        self._ask.title('Фигура для превращения')
        tk.Button(self._ask, text='Ферзь',
                  command=lambda: self.set_piece('Q')).pack()
        tk.Button(self._ask, text='Ладья',
                  command=lambda: self.set_piece('R')).pack()
        tk.Button(self._ask, text='Слон',
                  command=lambda: self.set_piece('B')).pack()
        tk.Button(self._ask, text='Конь',
                  command=lambda: self.set_piece('N')).pack()
        while self.piece == '':
            pass

    def set_piece(self, piece):
        """Устанавливает выбранную фигуру"""
        self.piece = piece
        self._ask.destroy()


class MovePiece(Move):
    """Информация о ходе, с возможностью перемещения фигуры"""
    def __init__(self, piece, coordinate):
        super().__init__(piece, coordinate)

    @staticmethod
    def move_to_move_piece(move):
        """Преобразует информацию о ходе, для перемещения фигуры"""
        return MovePiece(move.piece, move.coordinate)

    def move(self, graphic, is_being):
        """Перемещение фигуры на доске и игровом поле"""

        def stop_timer(graphics):
            graphics.list_of_moves.timer_white.stop_timer()
            graphics.list_of_moves.timer_black.stop_timer()

        def move_piece(piece, coordinate):
            """Перемещение фигуры на игровом поле"""
            try:
                if graphic.game_signals.rotate_field == Colour.WHITE:
                    for _ in range(30):
                        if not graphic.game_signals.end_game:
                            canvas.move(graphic.images_of_piece[piece].picture,
                                        (coordinate.x - piece.x) * 2,
                                        - (coordinate.y - piece.y) * 2)
                        time.sleep(TIME_MOVE / 30)
                else:
                    for _ in range(30):
                        if not graphic.game_signals.end_game:
                            canvas.move(graphic.images_of_piece[piece].picture,
                                        - (coordinate.x - piece.x) * 2,
                                        + (coordinate.y - piece.y) * 2)
                        time.sleep(0.015)
            except (tk.TclError, RuntimeError, KeyError):
                return False
            return True

        stop_timer(graphic)
        canvas = graphic.game_field.canvas

        try:
            if graphic.game.desk.desk[self.
                                      coordinate.x][self.coordinate.y].piece:
                canvas.delete(
                    graphic.images_of_piece[graphic.game.desk.desk[
                        self.coordinate.x][self.coordinate.y].piece].picture)
            if (self.piece.reduction == '' and
                abs(self.piece.x - self.coordinate.x) ==
                    abs(self.piece.y - self.coordinate.y) and
                    not graphic.game.desk.
                    desk[self.coordinate.x][self.coordinate.y].piece):
                    canvas.delete(graphic.images_of_piece[
                                      graphic.game.desk.desk[
                                          self.coordinate.x][
                                          self.piece.y].piece].picture)
        except KeyError:
            pass
        check_move = move_piece(self.piece, self.coordinate)
        if not check_move:
            graphic.game_field.move = None
            return False
        if (self.piece.reduction == 'K' and
           abs(self.piece.x - self.coordinate.x) == 2):
            if self.coordinate.x == 6:
                move_piece(graphic.game.desk.desk[7][self.piece.y].piece,
                           Coordinate(5, self.piece.y))
            else:
                move_piece(graphic.game.desk.desk[0][self.piece.y].piece,
                           Coordinate(3, self.piece.y))
        replace_colour = False
        if (self.piece.reduction == 'H' and
                graphic.game.desk.desk
                [self.coordinate.x][self.coordinate.y].piece):
            replace_colour = True
        graphic.game.desk.move_piece(graphic.game, self.piece, self.coordinate)
        if replace_colour:
            canvas.delete(graphic.images_of_piece[self.piece].picture)
            graphic.images_of_piece[self.piece] = \
                ImagesOfPiece(self.piece, graphic)
        if (self.piece.reduction == '' and
           (self.piece.y == 7 or self.piece.y == 0)):
            add_piece = ChoosePiece(graphic.root, is_being).piece
            canvas.delete(graphic.images_of_piece[self.piece].picture)
            add_piece = graphic.game.desk.add_piece_conversion(
                add_piece, self.piece.colour, self.coordinate)
            graphic.images_of_piece[add_piece] = \
                ImagesOfPiece(add_piece, graphic)
        graphic.game_signals.move = None
        return True


class Notice:
    def __init__(self, root, string):
        notice = tk.Toplevel(root)
        notice.geometry("350x50-500+300")
        notice.resizable(0, 0)
        label = tk.Label(notice, text=string)
        label.pack()


class GameField:
    """Игровое поле"""
    def __init__(self, graphic):
        self._graphic = graphic
        self.canvas = tk.Canvas(graphic.root, width=540, height=540)
        self._color_which_turned = Colour.WHITE
        self._desk = ImageTk.PhotoImage(Image.open("images/desk.png"))
        self._desk_image = self.canvas.create_image(1, 1,
                                                    image=self._desk,
                                                    anchor='nw')
        self._possible_moves = []
        self._list_of_heat_map = []
        self.colour_of_heat_map = ''
        self._record = ''
        self.canvas.pack()

    def rotate_desk(self, colour):
        """Повернуть доску"""
        if self._color_which_turned != colour:
            if colour == Colour.WHITE:
                self._graphic.game_signals.rotate_field = Colour.WHITE
                self._desk = ImageTk.PhotoImage(Image.open("images/desk.png"))
                self._desk_image = self.canvas.create_image(1, 1,
                                                            image=self._desk,
                                                            anchor='nw')
                self._color_which_turned = Colour.WHITE
            else:
                self._graphic.game_signals.rotate_field = Colour.BLACK
                self._desk = ImageTk.PhotoImage(
                    Image.open("images/desk.png").rotate(180))
                self._desk_image = self.canvas.create_image(1, 1,
                                                            image=self._desk,
                                                            anchor='nw')
                self._color_which_turned = Colour.BLACK
            self._graphic.delete_pieces()
            self._graphic.arrange_pieces()

    def show_heap_map(self, colour):
        """Показывает тепловую карту"""
        def get_colour(number):
            if 200 - number * 40 >= 0:
                red = 'fa'
                square_colour = hex(200 - number * 40)[2:]
            else:
                red = hex(max(250 - (number - 5) * 25, 100))[2:]
                square_colour = '00'
            if len(square_colour) == 1:
                square_colour = '0' + square_colour
            if number == 0:
                square_colour = 'ff'
            return '#' + red + square_colour * 2

        self.delete_heat_map()
        self.colour_of_heat_map = colour
        for i in range(8):
            for j in range(8):
                str_colour = get_colour(
                    self._graphic.game.desk.desk[i][j].count_visit[colour])
                if self._graphic.game_signals.rotate_field == Colour.WHITE:
                    self._list_of_heat_map.append(
                        self.canvas.create_rectangle(
                            i * 60 + 30,
                            (7 - j) * 60 + 30,
                            i * 60 + 30 + 60,
                            (7 - j) * 60 + 30 + 60,
                            fill=str_colour))
                else:
                    self._list_of_heat_map.append(
                        self.canvas.create_rectangle(
                            (7 - i) * 60 + 30,
                            j * 60 + 30,
                            (7 - i) * 60 + 30 + 60,
                            j * 60 + 30 + 60,
                            fill=str_colour))
        self._graphic.delete_pieces()
        self._graphic.arrange_pieces()

    def delete_heat_map(self):
        """Удаляет тепловую карту"""
        self.colour_of_heat_map = ''
        for square in self._list_of_heat_map:
            self.canvas.delete(square)
        self._list_of_heat_map.clear()

    def make_move(self, colour, is_being, move, graphic_=True):
        """Переместить фигуру на доске"""
        if graphic_:
            self._graphic.game.desk.set_last_move(
                self._graphic.game_signals.move)
            self._record = self._graphic.list_of_moves.record_move(
                self._graphic.game_signals.move,
                colour, self._graphic.game)
            self.delete_possible_moves()
            self.unbind_possible_moves()
            self._graphic.game_signals.move = MovePiece.move_to_move_piece(
                self._graphic.game_signals.move)
            self._graphic.game_signals.move.move(self._graphic, is_being)
        else:
            self._graphic.game.desk.set_last_move(move)
            self._record = self._graphic.list_of_moves.record_move(
                move, colour, self._graphic.game)
            self._graphic.game.desk.move_piece(self._graphic.game,
                                               move.piece,
                                               move.coordinate)
        self._record += MovesList.record_another_symbols(
            colour, self._graphic.game)
        last_move = self._record.split('.')
        if len(last_move) == 2:
            last_move = last_move[1]
        else:
            last_move = last_move[0]
        self._graphic.game_signals.last_move = last_move.strip()
        try:
            self._graphic.list_of_moves.list_of_moves.insert(tk.END,
                                                             self._record)
        except (tk.TclError, RuntimeError):
            pass

    def bind_possible_moves(self, colour):
        """Привязать к фигурам определённого цвета
                        отображение возможных ходов при нажатии"""
        for piece in self._graphic.game.desk.list_of_pieces:
            if piece.colour == colour:
                try:
                    self.canvas.tag_bind(
                        self._graphic.images_of_piece[piece].picture,
                        '<Button-1>',
                        lambda event, piece=piece:
                        self.show_possible_moves(piece))
                except (KeyError, tk.TclError):
                    pass

    def unbind_possible_moves(self):
        """Отвязать от всех фигур
                        отображение возможных ходов при нажатии"""
        self.delete_possible_moves()
        for piece in self._graphic.game.desk.list_of_pieces:
            try:
                self.canvas.tag_unbind(
                    self._graphic.images_of_piece[piece].picture, '<Button-1>')
            except (KeyError, tk.TclError, RuntimeError):
                pass

    def delete_possible_moves(self):
        """Убрать отображение возможных ходов"""
        for possible_move in self._possible_moves:
            self.canvas.delete(possible_move)
        self._possible_moves = []

    def show_possible_moves(self, piece):
        """Показать возможные ходы для определённой фигуры"""
        def set_move(piece, coordinate):
            """Установить ход"""
            self._graphic.game_signals.move = MovePiece(piece, coordinate)

        self.delete_possible_moves()
        for square in piece.possible_moves():
            if self._graphic.game_signals.rotate_field == Colour.WHITE:
                self._possible_moves.append(
                    self.canvas.create_image(
                        square.x * 60 + 30,
                        (7 - square.y) * 60 + 30,
                        image=self._graphic.
                        images_of_piece[piece].image_moves,
                        anchor='nw'))
            else:
                self._possible_moves.append(
                    self.canvas.create_image((7 - square.x) * 60 + 30,
                                             square.y * 60 + 30,
                                             image=self._graphic.
                                             images_of_piece[
                                                 piece].image_moves,
                                             anchor='nw'))
            self.canvas.tag_bind(self._possible_moves[-1],
                                 '<Button-1>', lambda event, square=square:
                                 set_move(piece, square))


class Root:
    """Главное окно игры"""
    def __init__(self, graphic):
        self.graphic = graphic
        self.root = tk.Tk()
        self.root.geometry("540x540+300+0")
        self.root.resizable(0, 0)
        self.root.title('Ход белых')
        self._menu = GameMenu(self.root, graphic)
        self.root.bind('<Destroy>', self.end_game)

    @property
    def menu(self):
        return self._menu

    def end_game(self, event):
        self.graphic.game_signals.end_game = True


class Timer:
    def __init__(self, root, colour):
        self._root = root
        self._label = tk.Label(root)
        self._label.pack()
        self._is_run = False
        self._last_run = 0.0
        self._this_run = 0.0
        self._load_time = -1
        if colour == Colour.WHITE:
            self._colour = "Белые: "
        else:
            self._colour = "Чёрные: "
        self._label.configure(text=self._colour + '0.00')

    def get_time(self):
        return self._label["text"]

    def set_time(self, time_):
        self._load_time = time_

    def _update_clock(self):
        try:
            now = time.time()
            if self._is_run:
                self._root.after(100, self._update_clock)
                self._label.configure(
                    text=self._colour + str(
                        round(now - self._this_run +
                              self._last_run, 2)))
            else:
                self._last_run = round(now - self._this_run +
                                       self._last_run, 2)
        except tk.TclError:
            pass

    def start_new_timer(self):
        try:
            if self._load_time == -1:
                self._last_run = 0.0
                self._this_run = 0.0
                self._label.configure(text=self._colour + '0.00')
            else:
                self._last_run = self._load_time
                self._this_run = time.time()
                self._load_time = -1
                self._label.configure(text=self._colour +
                                      str(round(self._last_run, 2)))
        except tk.TclError:
            pass

    def run_timer(self):
        try:
            self._this_run = time.time()
            self._is_run = True
            self._update_clock()
        except tk.TclError:
            pass

    def stop_timer(self):
        try:
            self._is_run = False
        except tk.TclError:
            pass


class MovesList:
    """Окно с записью ходов"""
    def __init__(self, root, graphic):
        self.graphic = graphic
        self.num = 0
        self.moves = tk.Toplevel(root)
        self.moves.resizable(0, 0)
        scrollbar = tk.Scrollbar(self.moves)
        self.list_of_moves = tk.Listbox(self.moves,
                                        yscrollcommand=scrollbar.set)
        self.list_of_moves.pack(side=tk.LEFT, fill=tk.BOTH)
        self.moves.title('')
        self.moves.geometry("300x540-0+0")
        self.debut_name = ''
        scrollbar.pack(side=tk.RIGHT, fill=tk.X)
        scrollbar.config(command=self.list_of_moves.yview)
        self.timer_white = Timer(self.moves, Colour.WHITE)
        self.timer_black = Timer(self.moves, Colour.BLACK)

        def set_load_string(event):
            """Установить строку, с которой будет загружиться игра"""
            if len(self.list_of_moves.curselection()) != 0:
                graphic.load_string = self.list_of_moves.curselection()[0]
                graphic.game_signals.break_move = True

        def show_desk(event):
            """Показать доску"""
            graphic.load_string = -1
            graphic.game_signals.break_move = True

        self.list_of_moves.bind('<Button-3>', set_load_string)
        self.list_of_moves.bind('<Double-Button-1>', show_desk)

    def get_game(self):
        """Получить строковое представление ходов с начала игры"""
        game = ''
        try:
            for move in self.list_of_moves.get(0, tk.END):
                game += move
        except tk.TclError:
            pass
        return game[1:]

    def get_last_move(self):
        """Получить строковое представление последнего хода"""
        try:
            if self.list_of_moves.size() != 0:
                return self.list_of_moves.get(
                    tk.END, tk.END)[0].replace('.', ' ').split(' ')[-1]
            return ''
        except (tk.TclError, RuntimeError):
            return ''

    def set_debut_name(self, debut, name):
        """Установить в заголовок название дебюта"""
        if len(self.graphic.game.history_of_moves) != 0:
            self.graphic.game.history_of_moves[-1].append(debut)
            self.graphic.game.history_of_moves[-1].append(name)
        if name != '':
            try:
                self.moves.title(name)
            except tk.TclError:
                pass
            self.debut_name = name
        if debut:
            self.graphic.game.debut = debut

    def start_new(self):
        """Отчистить список ходов"""
        try:
            self.list_of_moves.delete(0, tk.END)
            self.num = 0
        except tk.TclError:
            pass

    def record_move(self, move, colour, game):
        """Преобразовать ход в строку"""
        record = ''
        separator = '-'
        if game:
            if game.desk.desk[move.coordinate.x][move.coordinate.y].piece:
                separator = 'x'
        notation = (move.piece.reduction + chr(move.piece.x + 97) +
                    str(move.piece.y + 1) + separator +
                    chr(move.coordinate.x + 97) + str(move.coordinate.y + 1))
        if move.piece.reduction == 'K':
            if move.coordinate.x - move.piece.x == 2:
                notation = '0-0'
            if move.coordinate.x - move.piece.x == -2:
                notation = '0-0-0'
        if colour:
            if colour == Colour.WHITE:
                self.num += 1
                record += ' ' + str(self.num) + '.' + notation
            else:
                record += ' ' + notation
        else:
            record = notation
        return record

    @staticmethod
    def record_another_symbols(colour, game):
        """В случаи отобых игровых ситуаций, дополнить запись хода"""
        record = ''
        if (game.desk.last_move.piece.reduction == '' and
            (game.desk.last_move.coordinate.y == 0 or
             game.desk.last_move.coordinate.y == 7)):
            record += (game.desk.
                       desk[game.desk.last_move.coordinate.x]
                       [game.desk.last_move.coordinate.y].piece.reduction)
        if colour == Colour.BLACK:
            another_colour = Colour.WHITE
        else:
            another_colour = Colour.BLACK
        if game.desk.check_on_mate(another_colour) == StatesOfGame.CHECKMATE:
            record += '#'
        elif game.desk.check_on_check(another_colour) == StatesOfGame.CHECK:
            record += '+'
        return record


class GameMenu:
    """Игровое меню"""
    def __init__(self, root, graphic):
        self._root = root
        self._graphic = graphic
        self.menu = tk.Menu(self._root)
        self.last_appeal = 0

        def remove_unnecessary_appeal():
            """Игнорирует слишком частое обращение"""
            now_time = time.time()
            if 0 < now_time - self.last_appeal < 1:
                print('Пожалуйста, не нажимайте так часто')
                return True
            else:
                self.last_appeal = now_time
                return False

        def set_colour_of_heat_map(colour):
            """Устанавливает выбранный цвет тепловой карты"""
            if remove_unnecessary_appeal():
                return
            self._graphic.game_signals.break_move = True
            self._graphic.game_field.colour_of_heat_map = colour

        def set_using_heretic():
            if self._graphic.list_of_moves.list_of_moves.size() == 0:
                self._graphic.game_signals.is_heretic =\
                    not self._graphic.game_signals.is_heretic
                self._graphic.game_signals.new_game = True
            else:
                self._choose_heretic.set(self._graphic.game_signals.is_heretic)

        self.menu.add_command(label="Новая игра", command=self.is_new_game)
        self.menu.add_command(label="Сохранение", command=self.save_game)
        self.menu.add_command(label="Загрузка", command=self.load_game)

        self._play_player = {Colour.WHITE: tk.BooleanVar(),
                             Colour.BLACK: tk.BooleanVar()}
        self._play_comp = {Colour.WHITE: tk.BooleanVar(),
                           Colour.BLACK: tk.BooleanVar()}

        self._play_player[Colour.WHITE].set(True)
        self._play_comp[Colour.WHITE].set(False)
        w_menu = tk.Menu(self.menu)
        w_menu.add_checkbutton(label='Игрок',
                               variable=self._play_player[Colour.WHITE],
                               command=lambda: self.set_players(
                                   Colour.WHITE, TypePlayer.PLAYER))
        w_menu.add_checkbutton(label='Компьютер',
                               variable=self._play_comp[Colour.WHITE],
                               command=lambda:
                               self.set_players(Colour.WHITE,
                                                TypePlayer.COMPUTER))
        self.menu.add_cascade(label="Белые", menu=w_menu)

        self._play_player[Colour.BLACK].set(False)
        self._play_comp[Colour.BLACK].set(True)
        b_menu = tk.Menu(self.menu)
        b_menu.add_checkbutton(label='Игрок',
                               variable=self._play_player[Colour.BLACK],
                               command=lambda:
                               self.set_players(Colour.BLACK,
                                                TypePlayer.PLAYER))
        b_menu.add_checkbutton(label='Компьютер',
                               variable=self._play_comp[Colour.BLACK],
                               command=lambda:
                               self.set_players(Colour.BLACK,
                                                TypePlayer.COMPUTER))
        self.menu.add_cascade(label="Чёрные", menu=b_menu)

        heat_map_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Показать тепловую карту",
                              menu=heat_map_menu)
        heat_map_menu.add_command(label='Белых',
                                  command=lambda:
                                  set_colour_of_heat_map(Colour.WHITE))
        heat_map_menu.add_command(label='Чёрных',
                                  command=lambda:
                                  set_colour_of_heat_map(Colour.BLACK))
        heat_map_menu.add_command(label='Убрать',
                                  command=lambda:
                                  self._graphic.game_field.delete_heat_map())

        f_menu = tk.Menu(self.menu)
        self._choose_heretic = tk.BooleanVar()
        self._choose_heretic.set(self._graphic.game_signals.is_heretic)
        self.menu.add_cascade(label="Верблюд", menu=f_menu)
        f_menu.add_checkbutton(label='Использовать',
                               variable=self._choose_heretic,
                               command=lambda: set_using_heretic())
        self._root.config(menu=self.menu)

    def set_choose_heretic(self, boolean):
        self._choose_heretic.set(boolean)

    def set_players(self, colour, player, load_game=False):
        """Устанавливает игроков"""
        if self._graphic.list_of_moves.list_of_moves.size() != 0 and not load_game:
            if player == TypePlayer.PLAYER:
                self._play_player[colour].set(not self._play_player[colour].get())
            else:
                self._play_comp[colour].set(not self._play_comp[colour].get())
            return
        if player == TypePlayer.PLAYER:
            self._play_player[colour].set(True)
            self._play_comp[colour].set(False)
        else:
            self._play_player[colour].set(False)
            self._play_comp[colour].set(True)
        self._graphic.game_signals.break_move = True
        self._graphic.set_players = colour, player

    def save_game(self):
        self._root.unbind('<Destroy>')
        save_file = fd.asksaveasfilename()
        if save_file:
            try:
                with open(save_file, "w") as file:
                    file.write(
                        "Chess save\n" +
                        str(LoadInfo(
                            is_heretic=self._graphic.game_signals.is_heretic,
                            white_player=self._graphic.players[Colour.WHITE],
                            black_player=self._graphic.players[Colour.BLACK],
                            white_time=self._graphic.
                            list_of_moves.timer_white.get_time(),
                            black_time=self._graphic.
                            list_of_moves.timer_black.get_time(),
                            load_game=self._graphic.list_of_moves.get_game()))
                    )
            except Exception as e:
                print('Не удалось открыть файл, {}'.format(e), file=sys.stderr)
                Notice(self._graphic.root, 'Не удалось '
                                           'открыть файл.\n'
                                           'Игра не была сохранена')
            else:
                Notice(self._graphic.root, 'Сохранено')
        self._root.bind('<Destroy>', self._graphic.end_game)

    def load_game(self, file=None):
        self._root.unbind('<Destroy>')
        if not file:
            file = fd.askopenfilename()
            if not file:
                self._root.bind('<Destroy>', self._graphic.end_game)
                return
            try:
                file = open(file)
            except Exception as e:
                print('Не удалось открыть файл, {}'.format(e), file=sys.stderr)
                Notice(self._graphic.root, 'Не удалось '
                                           'открыть файл.\n'
                                           'Запущена новая игра')
                self._root.bind('<Destroy>', self._graphic.end_game)
                return
        if file:
            load_info = LoadInfo(build_load=file)
            self._graphic.load_string = -1
            self._graphic.load_play = load_info.load_game
            self._graphic.game_signals.is_heretic = load_info.is_heretic
            self._graphic.menu.set_choose_heretic(
                self._graphic.game_signals.is_heretic)
            self._graphic.players[Colour.WHITE] = load_info.white_player
            self._graphic.players[Colour.BLACK] = load_info.black_player
            self._graphic.menu.set_players(
                Colour.WHITE, load_info.white_player, True)
            self._graphic.menu.set_players(
                Colour.BLACK, load_info.black_player, True)
            self._graphic.list_of_moves.timer_white.set_time(
                load_info.white_time)
            self._graphic.list_of_moves.timer_black.set_time(
                load_info.black_time)
            self._graphic.game_signals.break_move = True
            file.close()
        self._root.bind('<Destroy>', self._graphic.end_game)

    def set_new_game(self):
        """Уствнавливает начало новой игры"""
        self._graphic.game_signals.new_game = True

    def is_new_game(self):
        """Окно, спрашивающее подтверждение начала новой игры"""
        ask = tk.Toplevel(self._root)
        ask.geometry("290x28-900+100")
        ask.resizable(0, 0)
        tk.Button(ask, text="Да", command=lambda:
                  self.run_functions(self.set_new_game, ask.destroy),
                  width=15).place(x=0, y=0)
        ask.title('Начать новую игру?')
        tk.Button(ask, text="Нет", command=lambda: ask.destroy(),
                  width=15).place(x=150, y=0)

    def run_functions(self, *args):
        """Запустить по порядку функции"""
        for func in args:
            func()


class Graphics:
    """Графическое представление игры"""
    def __init__(self, game, game_signals):
        self.game_signals = game_signals
        self.root = Root(self)
        self.menu = self.root.menu
        self.end_game = self.root.end_game
        self.root = self.root.root
        self.game = game
        self.images_of_piece = {}
        self.game_field = GameField(self)
        self.list_of_moves = MovesList(self.root, self)
        self.arrange_pieces()
        self.load_string = None
        self.set_players = None
        self.load_play = None
        self.players = {Colour.WHITE: TypePlayer.PLAYER,
                        Colour.BLACK: TypePlayer.COMPUTER}

    def set_title(self, title):
        """Установить заголовок окна"""
        self.root.title(title)

    def load_game(self, load=None):
        """Загружает игру из записи ходов"""
        self.root.title("Загрузка...")
        if load:
            load_game = load
            num = 0
            self.start_new_game(False)
            self.list_of_moves.start_new()
            for move in load_game:
                if num % 2 == 1:
                    colour = Colour.BLACK
                else:
                    colour = Colour.WHITE
                num += 1
                move = MoveStr(move, self.game, colour)
                if not move.piece:
                    self.arrange_pieces()
                    print('Не удалось загрузить игру из файла')
                    Notice(self.root, 'Не удалось загрузить '
                                      'игру из файла.\n'
                                      'Запущена новая игра')
                    self.game_signals.new_game = True
                    return colour
                else:
                    self.game_field.make_move(colour,
                                              False, move, False)
                    self.list_of_moves.set_debut_name(
                        *choose_debut(self.list_of_moves.get_game(),
                                      self.game.debut))
            self.arrange_pieces()
            self.game_signals.break_move = True
            return colour
        else:
            if self.load_string != -1:
                self.delete_pieces()
                self.game.load_desk(self.load_string)
                self.game_signals.last_move = \
                    self.game.history_of_moves[self.load_string][1]
                self.game.desk.last_move = \
                    self.game.history_of_moves[self.load_string][1]
                self.game.history_of_moves = copy.deepcopy(
                    self.game.history_of_moves[:self.load_string + 1])
                self.list_of_moves.set_debut_name(
                    self.game.history_of_moves[self.load_string][2],
                    self.game.history_of_moves[self.load_string][3])
                self.list_of_moves.num = \
                    (len(self.game.history_of_moves) + 1) // 2
                self.list_of_moves.list_of_moves.delete(
                    self.load_string + 1, tk.END)
                self.arrange_pieces()
                if self.load_string % 2 == 1:
                    colour = Colour.BLACK
                else:
                    colour = Colour.WHITE
                return colour
            else:
                if len(self.list_of_moves.list_of_moves.curselection()):
                    self.load_string = \
                        self.list_of_moves.list_of_moves.curselection()[0]
                    self.delete_pieces()
                    self.game.load_desk(self.load_string)
                    self.arrange_pieces()
                return ''

    def override_game(self, game):
        """Устанавливет другую доску, при начале новой игры"""
        self.game = game

    def arrange_pieces(self):
        """Расставить фигуры на игровом поле"""
        for piece in self.game.desk.list_of_pieces:
            self.images_of_piece[piece] = ImagesOfPiece(piece, self)

    def delete_pieces(self):
        """Удаляет все фигуры на игровом поле"""
        for piece in self.images_of_piece:
            self.game_field.canvas.delete(self.images_of_piece[piece].picture)
        self.images_of_piece.clear()

    def start_new_game(self, set_new_game=True):
        """Начинает новую игру"""
        self.delete_pieces()
        self.game.new_game(self.game_signals.is_heretic)
        self.set_players = Colour.WHITE, TypePlayer.PLAYER
        self.menu.set_players(
            Colour.WHITE, TypePlayer.PLAYER, True)
        self.game_signals.last_move = ''
        self.override_game(self.game)
        try:
            self.list_of_moves.timer_black.start_new_timer()
            self.list_of_moves.timer_white.start_new_timer()
        except Exception:
            pass
        try:
            self.list_of_moves.moves.title('-')
            self.list_of_moves.debut_name = ''
        except tk.TclError:
            pass
        if set_new_game:
            self.arrange_pieces()
