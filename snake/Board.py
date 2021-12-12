import random
from typing import Tuple

import numpy as np
from numpy.ma.core import where
import numpy.ma as ma

TOTALLAYERS = 3

SNACKLAYER = 0
HAZARDLAYER = 1
# RESULTLAYER = 2
# each snake layer represents the number of turns left until that location is no longer occupied by the snake
# TOTALSNAKELAYERS = 2
# SNAKELAYERHEAD = 0
# SNAKELAYERBODY = 1
# each square indicates how many turns this snake will be in that square for
# SNAKELAYERTURNSREMAINING = 0
# SNAKELAYERHEALTH = 1
SNAKELAYER = 2  # each square is a combination of the number of turns it will remain on that square and the health of the snake
# key:
# 8 bits: turns remaining (max 256 length - should be enough?)
# 7 bits: health (max 128, health only goes up to 100)
# 1 bit: is ded

MAXHEALTH = 20
MAXHEALTHENCODED = MAXHEALTH << 8

SNAKEMASKMOVESREMAINING = 0b11111111
SNAKEMASKHEALTH = 0b111111100000000
SNAKEOFFSETHEALTH = 8  # TODO: check this is right
SNAKEMASKDEAD = 0b1000000000000000

NUMBERSNAKES = 2


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
        # self.prob_snack = prob_snack
        # self.pieces: np.ndarray = np.zeros(
        #     (self.x, self.y, TOTALLAYERS), dtype=np.int32)
        self.pieces: np.ndarray = np.zeros(
            (self.x, self.y, TOTALLAYERS), dtype=np.int)

    def __getitem__(self, index: int) -> np.array:
        return self.pieces[index]

    # not returning the layer since to apply it we need to apply to head, body, and turnsremaining
    def legal_moves(self, player: int) -> object():

        # snake_board = self[:, :, get_layer(player, SNAKELAYERTURNSREMAINING)]
        board = self[:, :, SNAKELAYER]
        # print("snake in legal_moves",snake)
        if player == 1:
            head = np.where(board == np.amax(board))
        else:
            head = np.where(board == np.amin(board))

        x = head[0][0]
        y = head[1][0]
        legal_points = list()
        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if x+dx < self.x and x+dx >= 0 and y+dy < self.y and y+dy >= 0:
                legal_points.append((x+dx, y+dy))
        return legal_points

    # def add_snack(self) -> None:
    #     roll = random.uniform(0, 1)
    #     if roll > self.prob_snack:
    #         return

    #     # get empty squares
    #     # add all turn_remaining squares
    #     all_turns_remaining = np.zeros((self.x, self.y))
    #     for snake in range(self.number_snakes):
    #         turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
    #         turns_remaining = self.pieces[:, :, turns_remaining_layer]
    #         all_turns_remaining += turns_remaining

    #     # find zeros then flatten it
    #     blank_spaces = np.argwhere(all_turns_remaining == 0)

    #     # generate a random integer the length of the total blank spaces, and get the location correspond to that number
    #     (x, y) = blank_spaces[random.randint(0, len(blank_spaces[:])-1), :]

    #     # print(self.pieces[:,:,SNACKLAYER])

    #     self.pieces[x, y, SNACKLAYER] = 1
    #     # print(self.pieces[:,:,SNACKLAYER])

    # def is_lost(self, snake_id):
    #     for snake in self.snakes:
    #         if snake.id == snake_id and snake.died_reason == "":
    #             return False
    #     return True

    # get_result returns:
    # -1: still going
    # 1e-4: draw
    # 0+: snake number that won

    def get_result(self, player: int) -> int:
        if player == 1:
            player_dead = self.pieces[self.pieces > 0][0] >> 15
            opponent_dead = (-1*self.pieces[self.pieces < 0][0]) >> 15
        else:
            player_dead = (-1*self.pieces[self.pieces < 0][0]) >> 15
            opponent_dead = self.pieces[self.pieces > 0][0] >> 15

        if player_dead == 0 and opponent_dead == 0:
            return player

        if player_dead == 0 and opponent_dead == 1:
            return 0

        if player_dead == 1 and opponent_dead == 0:
            return -player

        if player_dead == 1 and opponent_dead == 1:
            return 1e-4

        # alive_snakes = list()
        # for snake in range(self.number_snakes):
        #     dead_layer = get_layer(snake, SNAKELAYERDEAD)
        #     dead = self.pieces[:, :, dead_layer]
        #     if not dead[0, 0]:
        #         alive_snakes.append(snake)

        # self_dead_layer = get_layer(player, SNAKELAYERDEAD)
        # self_dead = self.pieces[0, 0, self_dead_layer]

        # if self_dead + opponent_dead is 0:
        #     return 0
        # if self_dead + opponent_dead is 2:
        #     return 1e-4
        # if len(alive_snakes) == 1:
        #     if alive_snakes[0] == snake:
        #         return 1

        #     return -1

        # remaining_snakes = list()
        # for snake in self.snakes:
        #     if snake.died_reason == "":
        #         remaining_snakes.append(snake)
        # if len(remaining_snakes) == 1:
        #     return remaining_snakes[0].id
        # if len(remaining_snakes) == 0:
        #     return 1e-4
        # return 0

    # updates the death arrays
    # we are assuming either a two player game where we stop immediately, or that when i build out the
    # multiplayer version i will remove dead snakes once they die.
    # means when converting from api i should just completely ignore any snake that is dead.
    # TODO: if a snake has died at the same time you hit its body that's not accounted for here. need to check how this actually works

    # def find_deaths(self) -> None:
    #     for snake in range(self.number_snakes):
    #         head_layer = get_layer(snake, SNAKELAYERHEAD)
    #         head = self.pieces[:, :, head_layer]

    #         # get your length for comparison with other snakes
    #         body_layer = get_layer(snake, SNAKELAYERBODY)
    #         body = self.pieces[:, :, body_layer]
    #         snake_length = np.count_nonzero(body)

    #         for other_snake in range(self.number_snakes):
    #             # check body collisions
    #             other_body_layer = get_layer(other_snake, SNAKELAYERBODY)
    #             other_body = self.pieces[:, :, other_body_layer]
    #             death_from_body = 1 in np.logical_and(head, other_body)
    #             if death_from_body:
    #                 # if we've died from our own body we should check just in case this is the first move
    #                 # only do this here to reduce calculations (ie don't do it first)
    #                 turns_remaining_layer = get_layer(
    #                     snake, SNAKELAYERTURNSREMAINING)
    #                 turns_remaining = self.pieces[:, :, turns_remaining_layer]
    #                 if snake == other_snake and np.sum(turns_remaining) == 3:
    #                     break

    #                 # if not, set the dead layer to true
    #                 dead_layer = get_layer(snake, SNAKELAYERDEAD)
    #                 self.pieces[:, :, dead_layer] = np.ones((self.x, self.y))
    #                 break

    #             # don't check collision with your own head
    #             if snake == other_snake:
    #                 continue

    #             # if they are shorter than you then you can't have died.
    #             # don't worry about head since i don't count it in snake_length.
    #             other_snake_length = np.count_nonzero(other_body)
    #             if other_snake_length < snake_length:
    #                 continue
    #             # check head collisions
    #             other_head_layer = get_layer(other_snake, SNAKELAYERHEAD)
    #             other_head = self.pieces[:, :, other_head_layer]
    #             death_from_head = 1 in np.logical_and(head, other_head)
    #             if death_from_head:
    #                 dead_layer = get_layer(snake, SNAKELAYERDEAD)
    #                 self.pieces[:, :, dead_layer] = np.ones((self.x, self.y))

    #     return False

    def execute_move(self, move: Tuple[int, int], player: int) -> np.ndarray:

        (x, y) = move
        pieces = np.copy(player*self.pieces)
        snacks = np.copy(player*self.pieces[:, :, SNACKLAYER])
        snakes = np.copy(player*self.pieces[:, :, SNAKELAYER])

        # # calculate layer values once for efficiency
        # body_layer = get_layer(player, SNAKELAYERBODY)

        # decrement all turns remaining by one
        # TODO:check if reassigning this variable slows us down
        # turns_remaining_layer = get_layer(player, SNAKELAYERTURNSREMAINING)
        # turns_remaining_layer_opponent = get_layer(
        #     -1*player, SNAKELAYERTURNSREMAINING)
        # turns_remaining = snakes[:, :, turns_remaining_layer]
        # max = np.amax(turns_remaining)

        # increment or decrement depending on which player is moving
        # then set anything with 0 steps remaining to zero to clear out other snake data
        # TODO: figure out the most efficient way to do this.
        # if player == 1:
        snakes = np.subtract(snakes, 1,
                             where=snakes > 0)
        zeroer = np.where(np.bitwise_or(snakes,
                                        SNAKEMASKMOVESREMAINING) != 0, 1, 0)
        # else:
        #     snakes = np.add(snakes, 1,
        #                     where=snakes < 0)
        #     zeroer = np.where(
        #         np.bitwise_or((-1*snakes), SNAKEMASKMOVESREMAINING) != 0, 1, 0)

        snakes = zeroer * snakes

        # #   set new head
        # snakes[x, y, turns_remaining_layer] = max
        # # TODO: check if we're on food now and increment the minimum by one if so

        # # update body
        # body_layer = get_layer(player, SNAKELAYERBODY)
        # head_layer = get_layer(player, SNAKELAYERHEAD)
        # OR with current head location since we haven't moved it yet
        # snakes[:, :, body_layer] = np.logical_or(
        #     snakes[:, :, body_layer], snakes[:, :, head_layer])
        # # AND with turns remaining to remove old tail
        # snakes[:, :, body_layer] = np.logical_and(
        #     snakes[:, :, body_layer], snakes[:, :, turns_remaining_layer])

        # # move head to new location
        # snakes[:, :, head_layer] = np.zeros((self.x, self.y))
        # snakes[x, y, head_layer] = 1

        # check collisions
        # TODO: make this engine tell you that you lost if the opponent could have moved into this square in one turn
        # this is a crude approach to dealing with the simultaneousnous of the game.
        # should also make it say you won if the opponent was forced to move into this square on their next turn
        # and are shorter than you.
        if snakes[x, y] != 0:
            # max = np.amax(turns_remaining)
            # if we ran into someone, set our deadbit
            # if player == 1:
            snakes = np.add(snakes, SNAKEMASKDEAD,
                            where=snakes > 0)
            # else:

            #     snakes = np.subtract(snakes, SNAKEMASKDEAD,
            #                          where=snakes < 0)

            # snakes[:, :, RESULTLAYER] = -player
            # can stop here since we ded
            pieces[:, :, SNAKELAYER] = player*snakes
            return pieces

        # decrement health
        # health_layer = get_layer(player, SNAKELAYERHEALTH)
        # if player == 1:
        snakes = np.subtract(snakes, 1*SNAKEOFFSETHEALTH,
                             where=snakes > 0)
        # else:
        #     snakes = np.add(snakes, 1*SNAKEOFFSETHEALTH,
        #                     where=snakes < 0)

        # if our head is now on a snack, update health to MAXHEALTH, remove snack, and give our tail an extra piece
        # eaten_snacks = np.logical_and(
        #     snakes[:, :, head_layer], snakes[:, :, SNACKLAYER])
        # snacks = np.copy(self.snakes[:, :, SNACKLAYER])

        got_snack = snacks[x, y] == 1
        # if no snacks on our head, check if we died then return either way. rest of the function is dealing with removing snack.
        if not got_snack:
            # if player == 1:
            health = snakes[snakes > 0][0]
            # else:
            #     health = -snakes[snakes < 0][0]

            if health >> SNAKEOFFSETHEALTH == 0:
                # check if opponent is on 1 health. since we are taking turns this most likely means it's a draw.
                # (ie they will die on the next move)
                # another crude adaptation for simultaneous play that doesn't capture the chance they could get health on that turn.
                # incredibly rare that in real play two players will starve out at the same time with even a small amount of randomness.
                # health_layer_opponent = get_layer(player, SNAKELAYERHEALTH)
                # if snakes[0, 0, health_layer_opponent] is 1:
                #     snakes[:, :, RESULTLAYER] = 1e-4
                #     return snakes

                # zeroer is the shape of the current player

                snakes = snakes + zeroer*SNAKEMASKDEAD

            pieces[:, :, SNAKELAYER] = player*snakes
            return pieces

        # remove snack
        # snakes[x, y, SNACKLAYER] = 0
        # # make health MAXHEALTH
        # snakes[:, :, health_layer] = MAXHEALTH
        # # add 1 to our tail
        # turns_remaining = snakes[:, :, turns_remaining_layer]
        # tail_location = np.argmin(ma.masked_where(
        #     turns_remaining == 0, turns_remaining))
        # snakes[tail_location % self.x, int(
        #     tail_location/self.x), turns_remaining_layer] += 1
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
        pieces = np.copy(self.pieces)
        all_turns_remaining = np.zeros((self.x, self.y))
        all_heads = np.zeros((self.x, self.y))
        for snake in range(self.number_snakes):
            turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
            all_turns_remaining = all_turns_remaining + \
                pieces[:, :, turns_remaining_layer]
            heads_layer = get_layer(snake, SNAKELAYERHEAD)
            all_heads = all_heads+pieces[:, :, heads_layer]
            dead_layer = get_layer(snake, SNAKELAYERDEAD)
            print(f"snake {snake} dead: {pieces[0, 0, dead_layer]}")

        print("turns")
        print(all_turns_remaining)
        print("heads")
        print(all_heads)
        print("food")
        print(pieces[:, :, SNACKLAYER])
        print("stop pretty")
