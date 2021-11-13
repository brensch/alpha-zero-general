from __future__ import print_function
import numpy as np
from .SnakeLogic import Board
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


class SnakeGame(Game):
    def __init__(self, x=11, y=11, number_snakes=2):
        self.x = x
        self.y = y
        self.number_snakes = number_snakes

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.x, self.y, self.number_snakes)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.x, self.y)

    def getActionSize(self):
        # return number of actions
        return pow(3, self.number_snakes)

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action == self.n*self.n:
            return (board, -player)
        b = Board(self.n)
        b.pieces = np.copy(board)
        move = (int(action/self.n), action % self.n)
        b.execute_move(move, player)
        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.n)
        b.pieces = np.copy(board)
        legalMoves = b.get_legal_moves(player)
        if len(legalMoves) == 0:
            valids[-1] = 1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n*x+y] = 1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(self.n)
        b.pieces = np.copy(board)

        if b.is_win(player):
            return 1
        if b.is_win(-player):
            return -1
        if b.has_legal_moves():
            return 0
        # draw has a very little value
        return 1e-4

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
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
                object_type = -1
                for snake_count, snake in enumerate(board.snake_bodies):
                    for snake_piece in snake:
                        (x_snake,y_snake) = snake_piece
                        if x == x_snake and y == y_snake:
                            object_type = snake_count
                if object_type >= 0:
                    print("{:<2}".format(object_type), end="")
                else:
                    print("  ", end="")
            print("|")

        print("  ", end="")
        for _ in range(board.x):
            print("-", end="-")
        print("--")
