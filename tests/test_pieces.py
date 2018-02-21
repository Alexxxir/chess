import unittest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from game.constants import *
from game.coordinate import Coordinate
from game.pieces import *
from game.move import Move


class TestPieces(unittest.TestCase):
    def setUp(self):
        self.desk = Desk()

    def test_knight(self):
        self.desk.clear_desk()
        start_coordinate = Coordinate(0, 0)
        test_knight = self.desk.add_piece(start_coordinate, 'N', Colour.WHITE)
        self.assertListEqual(test_knight.possible_moves(),
                             [Coordinate(1, 2), Coordinate(2, 1)])
        self.desk.add_piece(Coordinate(1, 2), '', Colour.WHITE)
        self.desk.add_piece(Coordinate(2, 1), '', Colour.BLACK)
        self.assertListEqual(test_knight.possible_moves(), [Coordinate(2, 1)])
        self.assertListEqual(test_knight.possible_moves(defend=True),
                             [Coordinate(1, 2), Coordinate(2, 1)])
        self.assertEqual(str(test_knight), 'N_w')

    def test_bishop(self):
        self.desk.clear_desk()
        start_coordinate = Coordinate(3, 4)
        test_bishop = self.desk.add_piece(start_coordinate, 'B', Colour.WHITE)
        for coordinate in test_bishop.possible_moves():
            self.assertEqual(abs(coordinate.x - start_coordinate.x),
                             abs(coordinate.y - start_coordinate.y))
        self.assertEqual(len(test_bishop.possible_moves()), 13)
        self.desk.add_piece(Coordinate(4, 5), '', Colour.BLACK)
        self.desk.add_piece(Coordinate(2, 3), '', Colour.WHITE)
        self.assertEqual(len(test_bishop.possible_moves()), 8)

    def test_rook(self):
        self.desk.clear_desk()
        start_coordinate = Coordinate(3, 4)
        test_rook = self.desk.add_piece(start_coordinate, 'R', Colour.WHITE)
        for coordinate in test_rook.possible_moves():
            self.assertTrue(start_coordinate.x == coordinate.x or
                            start_coordinate.y == coordinate.y)

    def test_queen(self):
        self.desk.clear_desk()
        start_coordinate = Coordinate(3, 4)
        test_queen = self.desk.add_piece(start_coordinate, 'Q', Colour.WHITE)
        for coordinate in test_queen.possible_moves():
            self.assertTrue(start_coordinate.x == coordinate.x or
                            start_coordinate.y == coordinate.y or
                            abs(coordinate.x - start_coordinate.x) ==
                            abs(coordinate.y - start_coordinate.y))

    def test_pawn(self):
        self.desk.clear_desk()

        def test_move(piece, coordinate):
            self.desk.move_piece(None, piece, coordinate)
            self.assertEqual(Coordinate(piece.x, piece.y), coordinate)

        def test_start_move():
            self.assertEqual(test_pawn.possible_moves(),
                             [Coordinate(0, 2), Coordinate(0, 3)])
            test_move(test_pawn, Coordinate(0, 3))
            self.assertEqual(Coordinate(test_pawn.x, test_pawn.y),
                             Coordinate(0, 3))

        def test_possible():
            self.assertEqual(test_pawn.possible_moves(),
                             [Coordinate(0, 4), Coordinate(1, 4)])
            test_move(test_pawn, Coordinate(1, 4))
            self.assertEqual(self.desk.desk[1][4].piece, test_pawn)

        def test_defend():
            self.assertEqual(test_pawn.possible_moves(defend=True),
                             [Coordinate(1, 5),
                              Coordinate(2, 5),
                              Coordinate(0, 5)])

        def test_black_start_move_and_last_move():
            self.assertEqual(
                test_enemy_pawn_to_take_on_the_aisle.possible_moves(),
                [Coordinate(0, 5), Coordinate(0, 4)])
            self.desk.set_last_move(Move(
                test_enemy_pawn_to_take_on_the_aisle,
                Coordinate(0, 4)))
            test_move(test_enemy_pawn_to_take_on_the_aisle,
                      Coordinate(0, 4))

        def test_take_on_the_aisle():
            self.assertEqual(test_pawn.possible_moves(),
                             [Coordinate(1, 5), Coordinate(0, 5)])
            test_move(test_pawn, Coordinate(0, 5))
            self.assertIsNone(self.desk.desk[0][4].piece)

        def test_transformation():
            self.desk.move_piece(None, test_pawn, Coordinate(0, 7), 'Q')
            self.assertEqual(self.desk.desk[0][7].piece.reduction, 'Q')
            self.assertEqual(self.desk.desk[0][7].piece.colour, Colour.WHITE)

        test_pawn = self.desk.add_piece(Coordinate(0, 1), '', Colour.WHITE)
        test_enemy_pawn_to_take_on_the_aisle = \
            self.desk.add_piece(Coordinate(0, 6), '', Colour.BLACK)
        self.desk.add_piece(Coordinate(1, 4), '', Colour.BLACK)
        self.desk.add_piece(Coordinate(2, 4), '', Colour.BLACK)
        test_start_move()
        test_possible()
        test_defend()
        test_black_start_move_and_last_move()
        test_take_on_the_aisle()
        test_move(test_pawn, Coordinate(0, 6))
        test_transformation()

    def test_king(self):
        def set_rooks():
            self.desk.add_piece(Coordinate(0, 0), 'R', Colour.WHITE)
            self.desk.add_piece(Coordinate(7, 0), 'R', Colour.WHITE)
            self.desk.add_piece(Coordinate(0, 7), 'R', Colour.BLACK)
            self.desk.add_piece(Coordinate(7, 7), 'R', Colour.BLACK)

        def test_castling():
            self.assertEqual(len(test_white_king.possible_moves()), 5)
            set_rooks()
            self.assertEqual(len(test_white_king.possible_moves()), 7)
            test_white_king.was_moving = True
            self.assertEqual(len(test_white_king.possible_moves()), 5)
            self.assertEqual(len(test_black_king.possible_moves()), 7)
            self.desk.desk[0][7].piece.was_moving = True
            self.assertEqual(len(test_black_king.possible_moves()), 6)
            self.desk.desk[7][7].piece.was_moving = True
            self.assertEqual(len(test_black_king.possible_moves()), 5)

        def test_defence():
            self.assertEqual(
                len(test_white_king.possible_moves(defend=True)), 5)

        def test_possible_moves():
            self.desk.add_piece(Coordinate(0, 1), 'R', Colour.BLACK)
            self.desk.add_piece(Coordinate(3, 0), 'N', Colour.BLACK)
            self.assertEqual(len(test_white_king.possible_moves()), 2)
            self.desk.add_piece(Coordinate(5, 2), 'R', Colour.BLACK)
            test_white_king.was_moving = False
            self.assertEqual(len(test_white_king.possible_moves()), 1)

        self.desk.clear_desk()
        start_coordinate_white = Coordinate(4, 0)
        start_coordinate_black = Coordinate(4, 7)
        test_white_king = self.desk.add_piece(start_coordinate_white,
                                              'K', Colour.WHITE)
        test_black_king = self.desk.add_piece(start_coordinate_black,
                                              'K', Colour.BLACK)
        test_castling()
        test_defence()
        test_possible_moves()


class TestGame(unittest.TestCase):
    def setUp(self):
        self.desk = Desk()
        self.game = Game()

    def test_Game(self):
        def test_move_piece():
            self.assertIsNone(self.game.desk.move_piece(self.game, None, None))

        def test_history_of_moves():
            self.game.desk.move_piece(self.game,
                                      self.game.desk.desk[0][1].piece,
                                      Coordinate(0, 2))
            self.assertEqual(len(self.game.history_of_moves), 1)

        test_move_piece()
        test_history_of_moves()

    def test_check_on_mate(self):
        self.desk.add_piece(Coordinate(1, 0), 'K', Colour.WHITE)
        self.desk.add_piece(Coordinate(2, 2), 'Q', Colour.BLACK)
        self.desk.add_piece(Coordinate(0, 2), 'K', Colour.BLACK)
        self.assertEqual(self.desk.check_on_mate(Colour.WHITE), StatesOfGame.STALEMATE)
        self.desk.add_piece(Coordinate(1, 1), 'Q', Colour.BLACK)
        self.assertEqual(self.desk.check_on_mate(Colour.WHITE), StatesOfGame.CHECKMATE)
        self.assertEqual(self.desk.check_on_mate(Colour.BLACK), StatesOfGame.RUN)

    def test_load_desk(self):
        self.game.new_game()
        self.game.history_of_moves.append([Desk()])
        self.game.load_desk(0)
        for i in range(8):
            for j in range(8):
                self.assertFalse(self.game.desk.desk[i][j].piece)


if __name__ == '__main__':
    unittest.main()
