"""Модуль, реализующий сохранение игры в файл,
        и загрузку из файла"""
from .constants import TypePlayer
import json
import sys
import contextlib


class LoadInfo:
    def __init__(self, is_heretic=False,
                 white_player=TypePlayer.PLAYER,
                 black_player=TypePlayer.COMPUTER,
                 white_time=0.00,
                 black_time=0.00,
                 load_game=[],
                 build_load=''):
        self._is_heretic = int(is_heretic)
        self._white_player = white_player
        self._black_player = black_player
        self._white_time = white_time
        self._black_time = black_time
        self._load_game = load_game
        if build_load:
            self.load_game_from_file(build_load)

    def load_game_from_file(self, build_load):
        if build_load.readline() != 'Chess save\n':
            build_load.seek(0)
            self._load_game = []
            game_string = ''
            for line in build_load:
                game_string += line
            self._load_game = self.convert_string_to_notation(game_string)
        else:
            try:
                load = json.load(build_load)
                self._load_game = self.convert_string_to_notation(load['load_game'])
                if load["white_player"] == "TypePlayer.COMPUTER":
                    self._white_player = TypePlayer.COMPUTER
                else:
                    self._white_player = TypePlayer.PLAYER
                if load["black_player"] == "TypePlayer.PLAYER":
                    self._black_player = TypePlayer.PLAYER
                else:
                    self._black_player = TypePlayer.COMPUTER

                with contextlib.suppress(Exception):
                    self._white_time = float(load["white_time"].split(' ')[1])
                with contextlib.suppress(Exception):
                    self._black_time = float(load["black_time"].split(' ')[1])
                with contextlib.suppress(Exception):
                    self._is_heretic = int(load["is_heretic"])
            except json.decoder.JSONDecodeError as e:
                print("Не удалось загрузить игру".format(e), file=sys.stderr)

    def convert_string_to_notation(self, game_string):
        game_array = []
        game_string = game_string.replace(
            '.', ' ').replace('\n', ' ').split(' ')
        for move in game_string:
            if move != '':
                if len(move) > 3 or move == '0-0':
                    game_array.append(move)
        return game_array

    @property
    def load_game(self):
        return self._load_game

    @property
    def is_heretic(self):
        return self._is_heretic

    @property
    def white_player(self):
        return self._white_player

    @property
    def black_player(self):
        return self._black_player

    @property
    def black_time(self):
        return self._black_time

    @property
    def white_time(self):
        return self._white_time

    def __str__(self):
        return json.dumps({"white_player": str(self._white_player),
                           "black_player": str(self._black_player),
                           "white_time": str(self._white_time),
                           "black_time": str(self._black_time),
                           "is_heretic": str(self._is_heretic),
                           "load_game": self._load_game}, indent=4)
