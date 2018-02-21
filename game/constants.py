from enum import Enum


class Colour(Enum):
    COLORLESS = 0
    WHITE = 1
    BLACK = 2


class StatesOfGame(Enum):
    RUN = 0
    CHECKMATE = 1
    CHECK = 2
    STALEMATE = 3


class TypePlayer(Enum):
    COMPUTER = 0
    WAITING = 1
    PLAYER = 2
