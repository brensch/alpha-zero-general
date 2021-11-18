import random
from typing import Tuple

import numpy as np
from numpy.ma.core import where
import numpy.ma as ma

TOTALDATALAYERS = 2

SNACKLAYER = 0
HAZARDLAYER = 1
# each snake layer represents the number of turns left until that location is no longer occupied by the snake
TOTALSNAKELAYERS = 5
SNAKELAYERHEAD = 0
SNAKELAYERBODY = 1
SNAKELAYERTURNSREMAINING = 2
SNAKELAYERHEALTH = 3
SNAKELAYERDEAD = 4

MAXHEALTH = 20

Any = object()


def get_layer(snake: int, layer: int) -> int:
    return TOTALDATALAYERS + TOTALSNAKELAYERS*snake + layer


class Board():

    def __init__(self, x=11, y=11, number_snakes: int = 2, prob_snack=0.1) -> None:
        "Set up initial board configuration."
        self.x = x
        self.y = y
        self.prob_snack = prob_snack
        self.number_snakes = number_snakes
        self.pieces: np.ndarray = np.zeros(
            (self.x, self.y, TOTALSNAKELAYERS*number_snakes+TOTALDATALAYERS))

    def __getitem__(self, index: int) -> np.array:
        return self.pieces[index]

    # not returning the layer since to apply it we need to apply to head, body, and turnsremaining
    def legal_moves(self, snake: int) -> Any:

        snake_board = self[:, :, get_layer(snake, SNAKELAYERTURNSREMAINING)]
        # print("snake in legal_moves",snake)
        max_point = np.where(snake_board == np.amax(snake_board))

        x = max_point[0][0]
        y = max_point[1][0]
        legal_points = list()
        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if x+dx < self.x and x+dx >= 0 and y+dy < self.y and y+dy >= 0:
                legal_points.append((x+dx, y+dy))
        return legal_points

    def add_snack(self) -> None:
        roll = random.uniform(0, 1)
        if roll > self.prob_snack:
            return

        # get empty squares
        # add all turn_remaining squares 
        all_turns_remaining = np.zeros((self.x, self.y))
        for snake in range(self.number_snakes):
            turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
            turns_remaining = self.pieces[:, :, turns_remaining_layer]
            all_turns_remaining+=turns_remaining


        # find zeros then flatten it
        blank_spaces = np.argwhere(all_turns_remaining == 0)


        # generate a random integer the length of the total blank spaces, and get the location correspond to that number
        (x,y) = blank_spaces[random.randint(0, len(blank_spaces[:])-1),:]

        # print(self.pieces[:,:,SNACKLAYER])

        self.pieces[x,y,SNACKLAYER] = 1
        # print(self.pieces[:,:,SNACKLAYER])


    # def is_lost(self, snake_id):
    #     for snake in self.snakes:
    #         if snake.id == snake_id and snake.died_reason == "":
    #             return False
    #     return True

    # get_result returns:
    # -1: still going
    # 1e-4: draw
    # 0+: snake number that won
    def get_result(self, snake: int) -> int:
        alive_snakes = list()
        for snake in range(self.number_snakes):
            dead_layer = get_layer(snake, SNAKELAYERDEAD)
            dead = self.pieces[:, :, dead_layer]
            if not dead[0, 0]:
                alive_snakes.append(snake)

        if len(alive_snakes) == 0:
            return 1e-4
        if len(alive_snakes) == 2:
            return 0
        if len(alive_snakes) == 1:
            if alive_snakes[0] == snake:
                return 1

            return -1

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

    def find_deaths(self) -> None:
        for snake in range(self.number_snakes):
            head_layer = get_layer(snake, SNAKELAYERHEAD)
            head = self.pieces[:, :, head_layer]

            # get your length for comparison with other snakes
            body_layer = get_layer(snake, SNAKELAYERBODY)
            body = self.pieces[:, :, body_layer]
            snake_length = np.count_nonzero(body)

            for other_snake in range(self.number_snakes):
                # check body collisions
                other_body_layer = get_layer(other_snake, SNAKELAYERBODY)
                other_body = self.pieces[:, :, other_body_layer]
                death_from_body = 1 in np.logical_and(head, other_body)
                if death_from_body:
                    # if we've died from our own body we should check just in case this is the first move
                    # only do this here to reduce calculations (ie don't do it first)
                    turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
                    turns_remaining = self.pieces[:, :, turns_remaining_layer]
                    if snake == other_snake and np.sum(turns_remaining) == 3:
                        break
                
                    # if not, set the dead layer to true
                    dead_layer = get_layer(snake, SNAKELAYERDEAD)
                    self.pieces[:, :, dead_layer] = np.ones((self.x, self.y))
                    break

                # don't check collision with your own head
                if snake == other_snake:
                    continue

                # if they are shorter than you then you can't have died.
                # don't worry about head since i don't count it in snake_length.
                other_snake_length = np.count_nonzero(other_body)
                if other_snake_length < snake_length:
                    continue
                # check head collisions
                other_head_layer = get_layer(other_snake, SNAKELAYERHEAD)
                other_head = self.pieces[:, :, other_head_layer]
                death_from_head = 1 in np.logical_and(head, other_head)
                if death_from_head:
                    dead_layer = get_layer(snake, SNAKELAYERDEAD)
                    self.pieces[:, :, dead_layer] = np.ones((self.x, self.y))

        return False

    def execute_move(self, move: Tuple[int, int], snake: int) -> np.ndarray:

        (x, y) = move
        temp_board = np.copy(self.pieces)
        # calculate layer values once for efficiency
        body_layer = get_layer(snake, SNAKELAYERBODY)

        # decrement all turns remaining by one and update head to max
        # TODO:check if reassigning this variable slows us down
        turns_remaining_layer = get_layer(snake, SNAKELAYERTURNSREMAINING)
        turns_remaining = temp_board[:, :, turns_remaining_layer]
        max = np.amax(turns_remaining)
        temp_board[:, :, turns_remaining_layer] = np.subtract(turns_remaining, 1,
                                                              out=turns_remaining,
                                                              where=turns_remaining > 0)
        #   set new head
        temp_board[x, y, turns_remaining_layer] = max
        # TODO: check if we're on food now and increment the minimum by one if so

        # update body
        body_layer = get_layer(snake, SNAKELAYERBODY)
        head_layer = get_layer(snake, SNAKELAYERHEAD)
        # OR with current head location since we haven't moved it yet
        temp_board[:, :, body_layer] = np.logical_or(
            temp_board[:, :, body_layer], temp_board[:, :, head_layer])
        # AND with turns remaining to remove old tail
        temp_board[:, :, body_layer] = np.logical_and(
            temp_board[:, :, body_layer], temp_board[:, :, turns_remaining_layer])

        # move head to new location
        temp_board[:, :, head_layer] = np.zeros((self.x, self.y))
        temp_board[x, y, head_layer] = 1

        # decrement health
        health_layer = get_layer(snake, SNAKELAYERHEALTH)
        temp_board[:, :, health_layer] = temp_board[:, :, health_layer] - 1

        # if our head is now on a snack, update health to MAXHEALTH, remove snack, and give out tail an extra piece
        eaten_snacks = np.logical_and(temp_board[:, :, head_layer], temp_board[:, :, SNACKLAYER])
        # if no snacks on our head, return
        if np.sum(eaten_snacks) == 0:
            return temp_board

        # remove snack
        temp_board[:, :, SNACKLAYER] = temp_board[:, :, SNACKLAYER] - temp_board[:, :, head_layer]
        # make health MAXHEALTH
        temp_board[:, :, health_layer] = MAXHEALTH
        # add 1 to our tail
        turns_remaining = temp_board[:, :, turns_remaining_layer]
        tail_location = np.argmin(ma.masked_where(turns_remaining==0, turns_remaining))
        temp_board[tail_location%self.x, int(tail_location/self.x), turns_remaining_layer] +=1
        return temp_board


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
        print( pieces[:, :, SNACKLAYER])
        print("stop pretty")