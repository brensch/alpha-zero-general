from __future__ import print_function
from typing import Tuple
import random
import numpy as np
from .Board import SNAKELAYERBODY, SNAKELAYERHEAD, SNAKELAYERHEALTH, SNAKELAYERTURNSREMAINING, TOTALDATALAYERS, TOTALSNAKELAYERS, Board, get_layer
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


class Game(Game):
    def __init__(self, x: int = 11, y: int = 11, number_snakes: int = 2) -> None:
        self.x = x
        self.y = y
        self.number_snakes = number_snakes

    def getInitBoard(self) -> np.ndarray:

        number_squares = self.x*self.y
        starting_positions = random.sample(range(number_squares), 2)
        b = Board(self.x, self.y, self.number_snakes)

        for i in range(self.number_snakes):

            # set the snake layer we're currently on to have value 3 (ie three pieces)
            # in the random location relevant to this snake.
            start_x = starting_positions[i] % b.x
            start_y = int(starting_positions[i]/b.x)
            b.pieces[start_x, start_y, get_layer(
                i, SNAKELAYERTURNSREMAINING)] = 3

            # we start with head and body all on one spot, and health at 100
            b.pieces[start_x, start_y, get_layer(i, SNAKELAYERHEAD)] = 1
            b.pieces[start_x, start_y, get_layer(i, SNAKELAYERBODY)] = 1
            b.pieces[:, :, get_layer(i, SNAKELAYERHEALTH)] = 100

        return b.pieces

    def getBoardSize(self) -> Tuple[int, int, int]:
        return (self.x, self.y, TOTALDATALAYERS + self.number_snakes*TOTALSNAKELAYERS)

    def getActionSize(self):
        # all possible actions on the board (even if not currently valid)
        return self.x*self.y

    def getNextState(self, board: np.ndarray, player: int, action: int):
        # if player takes action on board, return next (board,player)
        # action is the index of the chosen action in the 1d list of all possible moves.
        # this is possibly where i will do >2 players since i can return the next player
        if action == self.x*self.y:
            return (board, -player)
        b = Board(self.x, self.y, self.number_snakes)
        b.pieces = np.copy(board)
        move = (action % self.x, int(action/self.x))
        # TODO:fix
        # if player == -1:
        #     player = 0
        temp_player = player
        if temp_player == -1:
            temp_player = 0
        new_move = b.execute_move(move, temp_player)
        return (new_move, -player)

    def getValidMoves(self, board: np.ndarray, player):
        # return boolean array the size of getBoardSize represent whether each move is valid or not
        valids = [0]*self.getActionSize()
        b = Board(self.x, self.y, self.number_snakes)
        b.pieces = np.copy(board)
        # print("getting valid moves for", player)
        temp_player = player
        if temp_player == -1:
            temp_player = 0
        legalMoves = b.legal_moves(temp_player)
        # # this should never happen since we aren't taking other snakes into account
        # if len(legalMoves) == 0:
        #     valids[-1] = 1
        #     return np.array(valids)
        for x, y in legalMoves:
            valids[self.x*y+x] = 1
        return np.array(valids)

    def getGameEnded(self, b: np.ndarray, player):

        board = Board(self.x, self.y, self.number_snakes)
        board.pieces = b

        return board.get_result()

    def getCanonicalForm(self, board: np.ndarray, player):
        # swap players if -1
        if player == 1:
            return board

        # needs to be less smoothbrain for multiplayer. probably needs shifting logic
        first_snake_layers = [TOTALDATALAYERS,
                             TOTALDATALAYERS+TOTALSNAKELAYERS-1]
        first = board[:, :, first_snake_layers]
        second_snake_layers =  [TOTALDATALAYERS+TOTALSNAKELAYERS,
                              TOTALDATALAYERS+2*TOTALSNAKELAYERS-1]
        second = board[:, :,second_snake_layers]
        board[:,:,first_snake_layers] = second
        board[:,:,second_snake_layers] = first
        return board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        # TODO:understand wtf is happening here
        # currently just returning one, i think it means i just flip things and send.
        return [(board, pi)]

        # assert(len(pi) == self.n**2+1)  # 1 for pass
        # pi_board = np.reshape(pi[:-1], (self.n, self.n))
        # l = []

        # for i in range(1, 5):
        #     for j in [True, False]:
        #         newB = np.rot90(board, i)
        #         newPi = np.rot90(pi_board, i)
        #         if j:
        #             newB = np.fliplr(newB)
        #             newPi = np.fliplr(newPi)
        #         l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        # return l

    def stringRepresentation(self, board: np.ndarray):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    @staticmethod
    def display(board: Board):
        print(board.x, board.y)

        print("    ", end="")
        for x in range(board.x):
            print("{:<1}".format(x), "", end="")
        print("")
        print("  ", end="")
        for _ in range(board.x):
            print("-", end="-")
        print("--")
        for y in range(board.y):
            print("{:<2}".format(y), "|", end="")    # print the row #
            for x in range(board.x):
                object_type = 0
                for snake in board.snakes:
                    for snake_piece in snake.body:
                        (x_snake, y_snake) = snake_piece
                        if x == x_snake and y == y_snake:
                            object_type = snake.id
                if object_type != 0:
                    print("{:>2}".format(object_type), end="")
                else:
                    print("  ", end="")
            print("|")

        print("  ", end="")
        for _ in range(board.x):
            print("-", end="-")
        print("--")
