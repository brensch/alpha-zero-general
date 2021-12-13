import random
from typing import Tuple

import numpy as np
from numpy.ma.core import where
import numpy.ma as ma

TOTALLAYERS = 2

# SNACKLAYER = 0
# HAZARDLAYER = 1
# RESULTLAYER = 2
# each snake layer represents the number of turns left until that location is no longer occupied by the snake
# TOTALSNAKELAYERS = 2
# SNAKELAYERHEAD = 0
# SNAKELAYERBODY = 1
# each square indicates how many turns this snake will be in that square for
# SNAKELAYERTURNSREMAINING = 0
# SNAKELAYERHEALTH = 1
BOARDLAYER = 0
SNAKELAYER = 1  # each square is a combination of the number of turns it will remain on that square and the health of the snake
# key:
# 8 bits: turns remaining (max 256 length - should be enough?)
# 7 bits: health (max 128, health only goes up to 100)
# 1 bit: is ded

MAXHEALTH = 100
MAXHEALTHENCODED = MAXHEALTH << 8

SNAKEMASKMOVESREMAINING = 0b11111111
SNAKEMASKHEALTH = 0b111111100000000
SNAKEMASKDEAD = 0b1000000000000000

SNAKEOFFSETMOVES = 0
SNAKEOFFSETHEALTH = 8
SNAKEOFFSETDEAD = 15

BOARDMASKSNACK = 0b1
BOARDOFFSETSNACK = 0

BOARDMASKSAUCE = 0b10
BOARDOFFSETSAUCE = 1


NUMBERSNAKES = 2

PROBABILITYSNACK = 0.5

# player -1 = snakelayer 0, player 1 = snakelayer 1


# def get_layer(player: int, layer: int) -> int:
#     if player is -1:
#         return TOTALDATALAYERS + layer
#     return TOTALDATALAYERS + TOTALSNAKELAYERS + layer


class Board():

    def __init__(self, x=7, y=7) -> None:
        "Set up initial board configuration."
        self.x = x
        self.y = y
        self.prob_snack = PROBABILITYSNACK
        # self.pieces: np.ndarray = np.zeros(
        #     (self.x, self.y, TOTALLAYERS), dtype=np.int32)
        self.pieces: np.ndarray = np.zeros(
            (self.x, self.y, TOTALLAYERS), dtype=np.int32)

    def __getitem__(self, index: int) -> np.array:
        return self.pieces[index]

    # not returning the layer since to apply it we need to apply to head, body, and turnsremaining
    def legal_moves(self, player: int) -> object():

        # snake_board = self[:, :, get_layer(player, SNAKELAYERTURNSREMAINING)]
        board = self[:, :, SNAKELAYER]
        # print("snake in legal_moves",snake)
        if player == -1:
            board = -board

        head = np.where(board == np.amax(board))

        # print("head", head)

        x = head[0][0]
        y = head[1][0]
        legal_points = list()
        good_points = list()
        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if x+dx < self.x and x+dx >= 0 and y+dy < self.y and y+dy >= 0:
                legal_points.append((x+dx, y+dy))
                if board[x+dx, y+dy] == 0:
                    good_points.append((x+dx, y+dy))

        # good points don't include neckbreak. if we have no other choice we need to neckbreak.
        if len(good_points) > 0:
            return good_points
        return legal_points

    def add_snack(self) -> None:
        roll = random.uniform(0, 1)
        if roll > self.prob_snack:
            return

        # find zeros then flatten it
        blank_spaces = np.argwhere((self.pieces[:, :, SNAKELAYER] | np.bitwise_and(
            self.pieces[:, :, BOARDLAYER], BOARDMASKSNACK)) == 0)
        # print(blank_spaces)

        if len(blank_spaces[:]) == 0:
            return

        # generate a random integer the length of the total blank spaces, and get the location correspond to that number
        (x, y) = blank_spaces[random.randint(0, len(blank_spaces[:])-1), :]
        self.pieces[x, y, BOARDLAYER] = self.pieces[x,
                                                    y, BOARDLAYER] + 1 << BOARDOFFSETSNACK

    def get_result(self, player: int) -> int:

        snake_layer = np.copy(self.pieces[:, :, SNAKELAYER])
        if player == -1:
            snake_layer = -snake_layer

        player_dead = snake_layer[snake_layer > 0][0] >> SNAKEOFFSETDEAD
        opponent_dead = (-1*snake_layer[snake_layer < 0][0]) >> SNAKEOFFSETDEAD

        # player_dead = np.right_shift(
        #     snake_layer, SNAKEOFFSETDEAD, where=snake_layer > 0)
        # opponent_dead = np.right_shift(
        #     -snake_layer, SNAKEOFFSETDEAD, where=snake_layer < 0)

        # if player == 1:
        #     player_dead = dead_layer[dead_layer > 0][0] >> 15
        #     opponent_dead = (-1*dead_layer[dead_layer < 0][0]) >> 15
        #     # print("player 1", player_dead, opponent_dead)
        # else:
        #     player_dead = (-1*dead_layer[dead_layer < 0][0]) >> 15
        #     opponent_dead = dead_layer[dead_layer > 0][0] >> 15
        # print("player -1", player_dead, opponent_dead)

        if player_dead == 0 and opponent_dead == 0:
            return 0

        if player_dead == 0 and opponent_dead == 1:
            return player

        if player_dead == 1 and opponent_dead == 0:
            return -player

        if player_dead == 1 and opponent_dead == 1:
            return 1e-4

    def execute_move(self, move: Tuple[int, int], player: int) -> np.ndarray:

        (x, y) = move
        # multiplying by player so we just operate on everything above 0
        pieces = np.copy(self.pieces)
        board = np.copy(self.pieces[:, :, BOARDLAYER])
        snakes = np.copy(player*self.pieces[:, :, SNAKELAYER])

        # get the current value for what should be the head (turns remaining + health)
        head_value = np.amax(snakes)

        # decrease all positions by 1 turn remaining and 1 health
        snakes = np.subtract(snakes, (1 << SNAKEOFFSETMOVES) + (1 << SNAKEOFFSETHEALTH),
                             where=snakes > 0)
        # zero out any columns the snake is no longer in
        # print("snakes")
        # print(snakes)
        snakes = np.where(np.bitwise_and(snakes,
                                         SNAKEMASKMOVESREMAINING) != 0, snakes, 0)
        # print("snakes after")
        # print(snakes)

        # check collisions
        # TODO: make this engine tell you that you lost if the opponent could have moved into this square in one turn
        # this is a crude approach to dealing with the simultaneousnous of the game.
        # should also make it say you won if the opponent was forced to move into this square on their next turn
        # and are shorter than you.
        if snakes[x, y] != 0:
            # print("player", player, "died on square", x, y)

            snakes = np.add(snakes, SNAKEMASKDEAD,
                            where=snakes > 0)

            pieces[:, :, BOARDLAYER] = board
            pieces[:, :, SNAKELAYER] = player*snakes
            return pieces

        # add new head now that we've checked for collisions. include health loss.
        snakes[x, y] = head_value - (1 << SNAKEOFFSETHEALTH)

        got_snack = (board[x, y] & BOARDMASKSNACK) == 1
        # print("snack check", board[x, y],
        #       BOARDMASKSNACK, (board[x, y] | BOARDMASKSNACK))
        health = snakes[snakes > 0][0] >> SNAKEOFFSETHEALTH
        # if no snacks on our head, check if we died then return either way. rest of the function is dealing with removing snack.
        if not got_snack:
            if health == 0:
                snakes = np.add(snakes, 1 << SNAKEOFFSETDEAD, where=snakes > 0)

            pieces[:, :, BOARDLAYER] = board
            pieces[:, :, SNAKELAYER] = player*snakes
            return pieces

        # remove snack
        # print("got snack", x, y)
        board[x, y] = board[x, y] - (1 << BOARDOFFSETSNACK)

        # get amount to add to get back to 100 (quicker than two bit masks i think)
        health_delta = MAXHEALTH - health
        # add the health delta and 1 to the turnsremaining bits since it will now persist for an extra move
        # print("snakes before add health")
        # print(snakes)
        # snakes = np.add(snakes, (health_delta << SNAKEOFFSETHEALTH) + 1,
        #                 where=snakes > 0)

        me = np.where(np.bitwise_and(snakes,
                                     SNAKEMASKMOVESREMAINING) != 0, snakes, 0)
        me = np.where(me > 0, (health_delta << SNAKEOFFSETHEALTH) + 1, 0)
        snakes = snakes + me

        # print("snakes after add health")
        # print(snakes)

        pieces[:, :, BOARDLAYER] = board
        pieces[:, :, SNAKELAYER] = player*snakes
        return pieces

    # def check_deaths(self):
        # for snake in self.snakes:
        #     for other_snake in self.snakes:
        #         for other_snake_piece in other_snake.body:
        #             # make sure it's not you and your own head
        #             if snake.id == other_snake.id and other_snake_piece == snake.body[0]:
        #                 continue

        #             (x, y) = other_snake_piece
        #             if x < 0 or y < 0 or x >= self.x or y >= self.y:
        #                 snake.died_turn = self.turn
        #                 snake.died_reason = "out of bounds"
        #             if snake.body[0] == other_snake_piece:
        #                 snake.died_turn = self.turn
        #                 snake.died_reason = "collided with snake"

    def to_string(self):
        return "{}:{}:{}:{}:{}".format(self.x, self.y, self.snacks, self.hazards,
                                       ["[{}:{}:{}:{}]".format(snake.body, snake.health, snake.died_turn, snake.died_reason) for snake in self.snakes])

    def pretty(self):
        # pieces = np.copy(self.pieces)
        # all_turns_remaining = np.zeros((self.x, self.y))
        # all_heads = np.zeros((self.x, self.y))
        # for snake in range(self.number_snakes):
        #     turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
        #     all_turns_remaining = all_turns_remaining + \
        #         pieces[:, :, turns_remaining_layer]
        #     heads_layer = get_layer(snake, SNAKELAYERHEAD)
        #     all_heads = all_heads+pieces[:, :, heads_layer]
        #     dead_layer = get_layer(snake, SNAKELAYERDEAD)
        #     print(f"snake {snake} dead: {pieces[0, 0, dead_layer]}")

        # print("turns")
        # print(all_turns_remaining)
        # print("heads")
        # print(all_heads)
        # print("food")
        pieces = np.copy(self.pieces)
        print("raw snake")
        print(pieces[:, :, SNAKELAYER])
        print("raw board")
        print(pieces[:, :, BOARDLAYER])

        print("snacks")
        print(np.bitwise_and(pieces[:, :, BOARDLAYER], BOARDMASKSNACK))
        print("snakes")
        print(np.bitwise_and(
            np.absolute(pieces[:, :, SNAKELAYER]), SNAKEMASKMOVESREMAINING) * np.where(pieces[:, :, SNAKELAYER] > 0, 1, -1))

        print("health")
        print(np.right_shift(np.bitwise_and(
            np.absolute(pieces[:, :, SNAKELAYER]), SNAKEMASKHEALTH), SNAKEOFFSETHEALTH) * np.where(pieces[:, :, SNAKELAYER] > 0, 1, -1))

        print("dead")
        print(np.right_shift(np.bitwise_and(
            np.absolute(pieces[:, :, SNAKELAYER]), SNAKEMASKDEAD), SNAKEOFFSETDEAD) * np.where(pieces[:, :, SNAKELAYER] > 0, 1, -1))


# def execute_move(self, move: Tuple[int, int], player: int) -> np.ndarray:

#         (x, y) = move
#         # multiplying by player so everything is positive relative to the current player
#         pieces = np.copy(player*self.pieces)
#         snacks = np.copy(player*self.pieces[:, :, SNACKLAYER])
#         snakes = np.copy(player*self.pieces[:, :, SNAKELAYER])

#         # # calculate layer values once for efficiency
#         # body_layer = get_layer(player, SNAKELAYERBODY)

#         # decrement all turns remaining by one
#         # TODO:check if reassigning this variable slows us down
#         # turns_remaining_layer = get_layer(player, SNAKELAYERTURNSREMAINING)
#         # turns_remaining_layer_opponent = get_layer(
#         #     -1*player, SNAKELAYERTURNSREMAINING)
#         # turns_remaining = snakes[:, :, turns_remaining_layer]

#         # get the current value for what should be the head (turns remaining + health)
#         head_value = np.amax(snakes)

#         # decrease all positions by 1 turn remaining and 1 health
#         # then set anything with 0 steps remaining to zero to clear out other snake data
#         # TODO: figure out the most efficient way to do this.
#         # if player == 1:
#         snakes = np.subtract(snakes, 1 + 1 << SNAKEOFFSETHEALTH,
#                              where=snakes > 0)
#         zeroer = np.where(np.bitwise_or(snakes,
#                                         SNAKEMASKMOVESREMAINING) != 0, 1, 0)
#         # else:
#         #     snakes = np.add(snakes, 1,
#         #                     where=snakes < 0)
#         #     zeroer = np.where(
#         #         np.bitwise_or((-1*snakes), SNAKEMASKMOVESREMAINING) != 0, 1, 0)

#         snakes = zeroer * snakes

#         # #   set new head
#         # snakes[x, y, turns_remaining_layer] = max
#         # # TODO: check if we're on food now and increment the minimum by one if so

#         # # update body
#         # body_layer = get_layer(player, SNAKELAYERBODY)
#         # head_layer = get_layer(player, SNAKELAYERHEAD)
#         # OR with current head location since we haven't moved it yet
#         # snakes[:, :, body_layer] = np.logical_or(
#         #     snakes[:, :, body_layer], snakes[:, :, head_layer])
#         # # AND with turns remaining to remove old tail
#         # snakes[:, :, body_layer] = np.logical_and(
#         #     snakes[:, :, body_layer], snakes[:, :, turns_remaining_layer])

#         # # move head to new location
#         # snakes[:, :, head_layer] = np.zeros((self.x, self.y))
#         # snakes[x, y, head_layer] = 1

#         # check collisions
#         # TODO: make this engine tell you that you lost if the opponent could have moved into this square in one turn
#         # this is a crude approach to dealing with the simultaneousnous of the game.
#         # should also make it say you won if the opponent was forced to move into this square on their next turn
#         # and are shorter than you.
#         if snakes[x, y] != 0:
#             # max = np.amax(turns_remaining)
#             # if we ran into someone, set our deadbit
#             # if player == 1:
#             snakes = np.add(snakes, SNAKEMASKDEAD,
#                             where=snakes > 0)
#             # else:

#             #     snakes = np.subtract(snakes, SNAKEMASKDEAD,
#             #                          where=snakes < 0)

#             # snakes[:, :, RESULTLAYER] = -player
#             # can stop here since we ded
#             pieces[:, :, SNAKELAYER] = player*snakes
#             return pieces

#         # decrement health
#         # health_layer = get_layer(player, SNAKELAYERHEALTH)
#         # if player == 1:
#         # snakes = np.subtract(snakes, 1*SNAKEOFFSETHEALTH,
#         #                      where=snakes > 0)
#         # print(health)
#         # print(head_value)

#         # add new head now that we've checked for collisions
#         snakes[x, y] = head_value
#         # else:
#         #     snakes = np.add(snakes, 1*SNAKEOFFSETHEALTH,
#         #                     where=snakes < 0)

#         # if our head is now on a snack, update health to MAXHEALTH, remove snack, and give our tail an extra piece
#         # eaten_snacks = np.logical_and(
#         #     snakes[:, :, head_layer], snakes[:, :, SNACKLAYER])
#         # snacks = np.copy(self.snakes[:, :, SNACKLAYER])

#         got_snack = snacks[x, y] == 1
#         health = snakes[snakes > 0][0] >> SNAKEOFFSETHEALTH
#         # if no snacks on our head, check if we died then return either way. rest of the function is dealing with removing snack.
#         if not got_snack:
#             # if player == 1:
#             # else:
#             #     health = -snakes[snakes < 0][0]

#             if health == 0:
#                 # check if opponent is on 1 health. since we are taking turns this most likely means it's a draw.
#                 # (ie they will die on the next move)
#                 # another crude adaptation for simultaneous play that doesn't capture the chance they could get health on that turn.
#                 # incredibly rare that in real play two players will starve out at the same time with even a small amount of randomness.
#                 # health_layer_opponent = get_layer(player, SNAKELAYERHEALTH)
#                 # if snakes[0, 0, health_layer_opponent] is 1:
#                 #     snakes[:, :, RESULTLAYER] = 1e-4
#                 #     return snakes

#                 # zeroer is the shape of the current player

#                 snakes = snakes + zeroer*SNAKEMASKDEAD

#             pieces[:, :, SNAKELAYER] = player*snakes
#             return pieces

#         # remove snack
#         snacks[x, y] = 0

#         # get amount to add to get back to 100 (quicker than two bit masks i think)
#         health_delta = MAXHEALTH - health
#         # add the health delta and 1 to the turnsremaining bits since it will now persist for an extra move
#         snakes = np.add(snakes, health_delta >> SNAKEOFFSETHEALTH + 1,
#                         where=snakes > 0)

#         # # make health MAXHEALTH
#         # snakes[:, :, health_layer] = MAXHEALTH
#         # # add 1 to our tail
#         # turns_remaining = snakes[:, :, turns_remaining_layer]
#         # tail_location = np.argmin(ma.masked_where(
#         #     turns_remaining == 0, turns_remaining))
#         # snakes[tail_location % self.x, int(
#         #     tail_location/self.x), turns_remaining_layer] += 1
#         pieces[:, :, SNACKLAYER] = snacks
#         pieces[:, :, SNAKELAYER] = player*snakes
#         return pieces
