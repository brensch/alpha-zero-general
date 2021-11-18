from random import randint, random
import time

from numpy.ma.core import where
import Arena
from MCTS import MCTS
from snake.Board import SNAKELAYERBODY, SNAKELAYERHEAD, SNAKELAYERHEALTH, SNAKELAYERTURNSREMAINING, Board, get_layer
from snake.Game import Game
from snake.SnakePlayers import *
from snake.keras.NNet import NNetWrapper as NNet

import numpy as np
import numpy.ma as ma


import numpy as np
from utils import *

"""
use this script to play any two agents against each other, or play manually with
any agent.
"""

# mini_othello = False  # Play in 6x6 instead of the normal 8x8.
human_vs_cpu = True





g = Game()
nn = NNet(g)

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
