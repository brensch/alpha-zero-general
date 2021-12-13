from __future__ import print_function
from typing import Tuple
import random
import numpy as np
from .Board import MAXHEALTHENCODED, TOTALLAYERS, SNAKELAYER, Board
from Game import Game
import sys
sys.path.append('..')

"""
Game class implementation for the game of Snake.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""


# def player_to_snake(player: int) -> int:
#     if player == 1:
#         return 0
#     return 1


class Game(Game):
    def __init__(self, x: int = 7, y: int = 7) -> None:
        self.x = x
        self.y = y

    def getInitBoard(self) -> np.ndarray:

        number_squares = self.x*self.y
        starting_positions = random.sample(range(number_squares), 2)
        b = Board(self.x, self.y)

        for snake in range(2):

            # set the snake layer we're currently on to have value 3 (ie three pieces)
            # in the random location relevant to this snake.
            start_x = starting_positions[snake] % b.x
            start_y = int(starting_positions[snake]/b.x)
            player = -1
            if snake == 1:
                player = 1
            b.pieces[start_x, start_y, SNAKELAYER] = player * \
                (3 + MAXHEALTHENCODED)

            # we start with head and body all on one spot, and health at 100
            # b.pieces[start_x, start_y, get_layer(snake, SNAKELAYERHEAD)] = 1
            # b.pieces[start_x, start_y, get_layer(snake, SNAKELAYERBODY)] = 1
            # b.pieces[:, :, get_layer(player, SNAKELAYERHEALTH)] = 100

        # print(b.pieces)

        return b.pieces

    def getBoardSize(self) -> Tuple[int, int, int]:
        return (self.x, self.y, TOTALLAYERS)

    def getActionSize(self):
        # all possible actions on the board (even if not currently valid)
        return self.x*self.y

    def getNextState(self, board: np.ndarray, player: int, action: int) -> Tuple[np.ndarray, int]:
        # if player takes action on board, return next (board,player)
        # action is the index of the chosen action in the 1d list of all possible moves.
        # this is possibly where i will do >2 players since i can return the next player
        b = Board(self.x, self.y)
        b.pieces = np.copy(board)
        move = (action % self.x, int(action/self.x))

        updated_board = b.execute_move(move, player)
        b.pieces = updated_board

        # only add snack on every second turn
        # print("player in getnextstate", player)
        if player == -1:
            b.add_snack()

        return (b.pieces, -player)

    def getValidMoves(self, board: np.ndarray, player):
        # return boolean array the size of getBoardSize represent whether each move is valid or not
        valids = [0]*self.getActionSize()
        b = Board(self.x, self.y)
        b.pieces = np.copy(board)

        legalMoves = b.legal_moves(player)
        for x, y in legalMoves:
            valids[self.x*y+x] = 1

        return np.array(valids)

    def getGameEnded(self, b: np.ndarray, player):

        board = Board(self.x, self.y)
        board.pieces = np.copy(b)
        # board.find_deaths()

        return board.get_result(player)

    def getCanonicalForm(self, board: np.ndarray, player):
        if player == -1:
            # only need to invert snake layer, others are informational
            # board[:, :, SNAKELAYER] = -board[:, :, SNAKELAYER]
            temp_board = np.copy(board)
            temp_board[:, :, SNAKELAYER] = -temp_board[:, :, SNAKELAYER]
            return temp_board
        return board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert (len(pi) == self.x * self.y)  # 1 for pass
        pi_board = np.reshape(pi, (self.x, self.y))
        return_list = []
        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                return_list += [(newB, list(newPi.ravel()))]
        return return_list

    def stringRepresentation(self, board: np.ndarray):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    @staticmethod
    def display(board: np.ndarray):
        b = Board()
        b.pieces = board
        b.pretty()
