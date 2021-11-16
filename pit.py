from random import randint, random
import time
import Arena
from MCTS import MCTS
from snake.Board import SNAKELAYERBODY, SNAKELAYERHEAD, SNAKELAYERHEALTH, SNAKELAYERTURNSREMAINING, Board, get_layer
from snake.Game import Game
from snake.SnakePlayers import *
from snake.keras.NNet import NNetWrapper as NNet

import numpy as np

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

g = Game()
nn = NNet(g)
nn.save_checkpoint()
nn.load_checkpoint()
b = Board()
board_array = g.getInitBoard()
player = 1

# for i in range(10):

moves = g.getValidMoves(board_array,player)
candidates = np.nonzero(moves)[0]
move = candidates[randint(0,len(candidates)-1)]
next_board_array, player = g.getNextState(board_array,player,move)
print(g.getGameEnded(board_array, player))
# b.pieces = next_board_array
b.find_deaths()
b.pretty()
# print(next_board, player)




# b = Board()
# b.pieces = board_array


# for i in range(15):
#     for snake in range(g.number_snakes):
#         moves = b.legal_moves(snake)
#         move = moves[randint(0,len(moves)-1)]
#         b.pieces = b.execute_move(move, snake)

#     b.find_deaths()
#     result = b.get_result()

#     if result != 0:
#         print(result)
#         b.pretty()
#         break

    # b.pretty()

# create the adjacent cell mask
# TODO: this is probably slow, should see if i can do it as a matrix operation
# mask = np.zeros((g.x, g.y))

        # mask[x+dx][y+dy] = 1

# print(mask)

# masko = np.ma.masked_where(mask == 0, mask)
# print(masko)

# thang = np.where()
# print(thang)

# for i in range(g.number_snakes):




# snake0max = np.where()

# (cord) =list(zip(snake0max[0], snake0max[1]))[0]
# print(cord)

# 



# print(g.pieces)


exit()
starter_snakes = generate_starter_snakes(11,11, 2)

b = Board(x=11, y=11, snakes=starter_snakes, snacks=list(), hazards=list(), turn=0)

# print(b.to_string())
# exit()
no_winners = True
i=0
while no_winners:
    i+=1
    # print("move ", i)
    if i%100 == 0:
        print(i)
        g.display(b)
        for snake in b.snakes:
            print(snake.body)
    # g.display(b)

    if len(b.snakes) == 0:
        no_winners = False
    

    # a tuple of the form: (snake_id, move)
    snake_moves = list()

    for snake in b.snakes:
        legal_moves = b.legal_moves_from_point(snake.body[0])

        # if there are no legal moves just do a move up
        if len(legal_moves) == 0:
            (x,y) = snake.body[0]
            snake_moves.append((snake.id,(x,y+1)))
            continue

        # otherwise add the corresponding move
        snake_moves.append((snake.id,legal_moves[randint(0, len(legal_moves)-1)]))

    # print("snake_moves",snake_moves)
    for move_info in snake_moves:
        (snake_id, move) = move_info
        b.execute_move(move, snake_id)

    b.check_deaths()

    for snake in b.snakes:
        if b.is_lost(snake.id):
            print("snake {} lost".format(snake.id))
            no_winners = False


g.display(b)
for snake in b.snakes:
    print(snake.id, snake.body, snake.died_turn, snake.died_reason)
print("took {} turns".format(i))

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
