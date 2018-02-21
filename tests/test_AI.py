import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from game.AI import ArtificialIntelligence
from game.pieces import ArrangePieces
from game.pieces import Desk
from game.pieces import Game
from game.signals import GameSignals
from game.constants import *


class TestAI(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game_signals = GameSignals(self.game)
        self.test_AI_w = ArtificialIntelligence(Colour.WHITE, self.game,
                                                self.game_signals, None)
        self.test_AI_b = ArtificialIntelligence(Colour.BLACK, self.game,
                                                self.game_signals, None)
        self.game.history_of_moves.append([Desk()])
        self.game.load_desk(0)
        self.arrange_pieces = ArrangePieces()

    def test_mate_and_taking(self):
        self.assertFalse(self.test_AI_w.move_method())
        pieces = ["-R------",
                  "--B-----",
                  "---p----",
                  "--------",
                  "--------",
                  "-p------",
                  "R-------",
                  "-------K"]
        colours = [[Colour.BLACK] * 8,
                   [Colour.BLACK] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.BLACK] * 8,
                   [Colour.BLACK] * 8,
                   [Colour.WHITE] * 8]
        self.arrange_pieces.arrange_pieces(self.game.desk, pieces, colours)
        self.assertTrue(self.test_AI_b.move_method())
        self.assertTrue(self.test_AI_w.move_method())
        self.assertEqual(self.game_signals.move.piece.reduction, '')
        self.game_signals.move = None
        self.game.desk.list_of_pieces.remove(self.game.desk.desk[1][2].piece)
        self.game.desk.desk[1][2].piece = None
        self.assertTrue(self.test_AI_b.move_method())
        self.assertEqual(self.game_signals.move.piece.reduction, 'R')

    def test_casting_and_taking(self):
        pieces = ["--------",
                  "--------",
                  "--------",
                  "---R-Q--",
                  "--p-----",
                  "--------",
                  "--------",
                  "R---K---"]
        colours = [[Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.WHITE] * 4 + [Colour.BLACK] * 4,
                   [Colour.BLACK] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.WHITE] * 8]

        self.arrange_pieces.arrange_pieces(self.game.desk, pieces, colours)
        self.test_AI_b.move_method()
        self.game_signals.move = None
        self.test_AI_w.move_method()
        self.assertEqual(self.game_signals.move.piece.reduction, 'R')

    def test_heretic_without_queen(self):
        pieces = ["--------",
                  "--------",
                  "--------",
                  "---R-B--",
                  "----H---",
                  "---p----",
                  "------N-",
                  "--------"]
        colours = [[Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.BLACK] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.COLORLESS] * 8]
        self.arrange_pieces.arrange_pieces(self.game.desk, pieces, colours)
        self.test_AI_b.move_method()
        self.assertEqual(self.game_signals.move.piece.reduction, 'H')
        self.assertEqual(self.game_signals.move.coordinate.x, 5)
        self.assertEqual(self.game_signals.move.coordinate.y, 2)

    def test_heretic_with_queen(self):
        pieces = ["--------",
                  "--------",
                  "--------",
                  "---R-B--",
                  "----H---",
                  "---p----",
                  "------Q-",
                  "--------"]
        colours = [[Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.COLORLESS] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.BLACK] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.WHITE] * 8,
                   [Colour.COLORLESS] * 8]
        self.arrange_pieces.arrange_pieces(self.game.desk, pieces, colours)
        self.game_signals.move = None
        self.test_AI_b.move_method()
        self.assertEqual(self.game_signals.move.piece.reduction, 'H')
        self.assertEqual(self.game_signals.move.coordinate.x, 6)
        self.assertEqual(self.game_signals.move.coordinate.y, 1)


if __name__ == '__main__':
    unittest.main()
