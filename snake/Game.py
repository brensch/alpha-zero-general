from __future__ import print_function
import random
import numpy as np
from .Board import SNAKELAYERBODY, SNAKELAYERHEAD, SNAKELAYERHEALTH, SNAKELAYERTURNSREMAINING, Board, get_layer
from Game import Game
import sys
sys.path.append('..')
from typing import Tuple

"""
Game class implementation for the game of Snake.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""



class Game(Game):
    def __init__(self, x: int=11, y: int=11, number_snakes: int = 2) -> None:
        self.x = x
        self.y = y
        self.number_snakes = number_snakes

    def getInitBoard(self) -> np.ndarray:

        number_squares = self.x*self.y
        starting_positions = random.sample(range(number_squares), 2)
        b = Board(self.x, self.y, self.number_snakes) 

        for i in range(self.number_snakes):
            print("calcing snak")
            print(starting_positions[i] % b.x)
            print(int(starting_positions[i] / b.x))
            print(get_layer(i, SNAKELAYERTURNSREMAINING))
            # set the snake layer we're currently on to have value 3 (ie three pieces) in the random location
            start_x = starting_positions[i] % b.x
            start_y = int(starting_positions[i]/b.x)
            b.pieces[start_x,start_y,get_layer(i, SNAKELAYERTURNSREMAINING)] = 3
            # we start with head and body all on one spot
            b.pieces[start_x,start_y,get_layer(i, SNAKELAYERHEAD)] = 1
            b.pieces[start_x,start_y,get_layer(i, SNAKELAYERBODY)] = 1
            b.pieces[:,:,get_layer(i, SNAKELAYERHEALTH)] = 100

            # body = [(starting_positions[i] % x, int(starting_positions[i]/x))]*3

        return b.pieces

    def getBoardSize(self) -> Tuple[int, int]:
        # (a,b) tuple
        return (self.x, self.y)

    def getActionSize(self):
        # return number of actions
        return pow(3, self.number_snakes)

    def getNextState(self, board: np.ndarray, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        board_copy = Board(x=board.x, y=board.y, hazards=board.hazards,
                           snacks=board.snacks, snakes=board.snakes, turn=board.turn)

        board_copy.execute_move(action, player)
        return (board_copy, -player)

    def getValidMoves(self, board, player):
        return board.get_legal_moves(player)

    def getGameEnded(self, board, player):

        return board.is_ended()

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        # TODO:understand wtf is happening here
        # currently just returning one, i think it means i just flip things and send.
        return [(board,pi)]

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
