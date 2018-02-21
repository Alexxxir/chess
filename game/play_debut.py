"""Модуль, реализующий распознование дебютов и позволяющий
        искусственному интеллекту делать
                стандартные для начала игры ходы"""

import os
import random


def choose_debut(game, debut):
    """Возвращает вид дебюта и его название"""
    name = ''
    if (not debut and len(game.split(' ')) > 1 or
            debut and len(game.split(' ')) == 2):
        try:
            debuts = os.listdir('debuts')
            for debut_ in debuts:
                with open('debuts/' + debut_) as debut_open:
                    move = debut_open.readline()
                    if game == move[:len(game)]:
                        debut = debut_
                        name = move[len(game):].strip()
                        break
        except Exception:
            pass
    elif not debut:
        name = '-'
    elif debut:
        try:
            with open('debuts/' + debut) as debut_open:
                for line in debut_open:
                    if game == line[:len(game)] and line[len(game) + 1] == "'":
                        name = line[len(game):].strip()
                        break
        except Exception:
            pass
    return debut, name


def choose_move(last_move):
    """Выбирает для искусственного интеллекта
                следующий ход, основываясь на предидуйщий"""
    try:
        with open('debuts/Moves_debut') as file_moves:
            moves = []
            if not last_move:
                for move in file_moves:
                    if move == '\n':
                        break
                    moves.append(move.strip())
                return random.choice(moves)
            else:
                for move in file_moves:
                    if len(move.split(' ')) == 2:
                        if move.split(' ')[0] == last_move:
                            moves.append(move.split(' ')[1].strip())
                if len(moves) != 0:
                    return random.choice(moves)
    except Exception:
        pass
