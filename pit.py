from random import randint
import Arena
from MCTS import MCTS
from snake.SnakeLogic import Board
from snake.SnakeGame import SnakeGame
from snake.SnakePlayers import *
from snake.keras.NNet import NNetWrapper as NNet


import numpy as np
from utils import *

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

# mini_othello = False  # Play in 6x6 instead of the normal 8x8.
human_vs_cpu = True

# if mini_othello:
#     g = OthelloGame(6)
# else:
#     g = OthelloGame(8)

g = SnakeGame()

b = Board(11, 11)
no_winners = True
i=0
while no_winners:
    i+=1
    # print("move ", i)
    if i%100 == 0:
        print(i)
        g.display(b)
        for snake in b.snake_bodies:
            print(snake)
    # g.display(b)

    if len(b.snake_bodies) == 0:
        no_winners = False
    

    snake_moves = list()
    for snake_number, snake in enumerate(b.snake_bodies):
        legal_moves = b.legal_moves_from_point(snake[0])

    # if there are no legal moves just do anything
        if len(legal_moves) == 0:
            (x,y) = snake[0]
            snake_moves.append((x,y+1))
            continue

        snake_moves.append(legal_moves[randint(0, len(legal_moves)-1)])

    # print("snake_moves",snake_moves)
    for move_number, move in enumerate(snake_moves):
        b.execute_move(move, move_number)

    b.check_deaths()

    for snake_number in range(len(b.snake_bodies)):
        if b.is_lost(snake_number):
            print("snake {} lost".format(snake_number))
            no_winners = False


g.display(b)
for snake_number,snake in enumerate(b.snake_bodies):
    print(snake_number,snake)

# g.getInitBoard()
# print(g.getValidMoves())
exit()
# all players
rp = RandomPlayer(g).play
# gp = GreedyOthelloPlayer(g).play
hp = HumanTicTacToePlayer(g).play

#

# nnet players
n1 = NNet(g)
n1.load_checkpoint('./pretrained_models/tictactoe/keras',
                   'best-25eps-25sim-10epch.pth.tar')
# if mini_othello:
#     n1.load_checkpoint('./pretrained_models/snake','6x100x25_best.pth.tar')
# else:
#     n1.load_checkpoint('./pretrained_models/snake','8x8_100checkpoints_best.pth.tar')
args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
mcts1 = MCTS(g, n1, args1)
def n1p(x): return np.argmax(mcts1.getActionProb(x, temp=0))


player2 = hp
# if human_vs_cpu:
# player2 = hp
# else:
#     n2 = NNet(g)
#     n2.load_checkpoint('./pretrained_models/snake', '8x8_100checkpoints_best.pth.tar')
#     args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
#     mcts2 = MCTS(g, n2, args2)
#     n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))

#     player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.

arena = Arena.Arena(n1p, player2, g, display=SnakeGame.display)

print(arena.playGames(2, verbose=True))
