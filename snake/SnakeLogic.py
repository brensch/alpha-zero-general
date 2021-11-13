'''
Board class for the game of TicTacToe.
Default board size is 3x3.
Board data:
  1=white(O), -1=black(X), 0=empty
  first dim is column , 2nd is row:
     pieces[0][0] is the top left square,
     pieces[2][0] is the bottom left square,
Squares are stored and manipulated as (x,y) tuples.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the board for the game of Othello by Eric P. Nichols.

'''

import random

# class Snake():
#     def __init__(self):


class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    # __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self, x, y, number_snakes=2):
        "Set up initial board configuration."

        self.x = x
        self.y = y

        number_squares = x*y

        starting_positions = random.sample(range(number_squares), 2)

        # TODO: make this multiplayer. need to get lines on my brain first.
        # list of three identical tuples from the sample above (sample does not overlap)
        self.snake_bodies: list(tuple) = list()
        self.snake_health = list()
        self.snake_is_alive = list()

        for i in range(number_snakes):
            self.snake_bodies.append([(starting_positions[i]%x, int(starting_positions[i]/x))]*3)
            self.snake_health.append(100)
            self.snake_is_alive.append(True)

        print(self.snake_bodies)

    # # add [][] indexer syntax to the Board
    # def __getitem__(self, index):
    #     return self.pieces[index]

    # put a random snake of length 3 on the board

    def legal_moves_from_point(self, point):

        # print("moving from point:", point)

        (x, y) = point
        legal_points = list()

        for direction in ["up", "down", "left", "right"]:
            if direction == "up":
                candidate = (x, y+1)
            if direction == "down":
                candidate = (x, y-1)
            if direction == "left":
                candidate = (x-1, y)
            if direction == "right":
                candidate = (x+1, y)

            if self.point_is_legal(candidate):
                legal_points.append(candidate)

        return legal_points

    def point_is_legal(self, point):

        # check bounds
        (x, y) = point
        if x < 0 or x >= self.x or y < 0 or y >= self.y:
            return False

        # check other snakes
        for snake in self.snake_bodies:
            for snake_point in snake[:-1]:
                # check all points except the last one since that won't be there next time
                # TODO: it might be there if they snack. account for this.
                if point == snake_point:
                    return False
        return True

    def get_legal_moves(self, snake_number):
        "Returns all the legal moves for the given snake_number."
        return self.legal_moves_from_point(self.snake_bodies[snake_number])

    # def has_legal_moves(self):
    #     for y in range(self.n):
    #         for x in range(self.n):
    #             if self[x][y] == 0:
    #                 return True
    #     return False

    def is_lost(self, snake):
        for snake_iter,alive in enumerate(self.snake_is_alive):
            if snake_iter == snake and alive:
                return False
        return True

        # """Check whether the given player has collected a triplet in any direction;
        # @param color (1=white,-1=black)
        # """
        # win = self.n
        # # check y-strips
        # for y in range(self.n):
        #     count = 0
        #     for x in range(self.n):
        #         if self[x][y] == color:
        #             count += 1
        #     if count == win:
        #         return True
        # # check x-strips
        # for x in range(self.n):
        #     count = 0
        #     for y in range(self.n):
        #         if self[x][y] == color:
        #             count += 1
        #     if count == win:
        #         return True
        # # check two diagonal strips
        # count = 0
        # for d in range(self.n):
        #     if self[d][d] == color:
        #         count += 1
        # if count == win:
        #     return True
        # count = 0
        # for d in range(self.n):
        #     if self[d][self.n-d-1] == color:
        #         count += 1
        # if count == win:
        #     return True

    def execute_move(self, move, snake_number):

        # add the new move and remove the last piece
        self.snake_bodies[snake_number].insert(0,move)
        self.snake_bodies[snake_number].pop()
        
    def check_deaths(self):
        for snake_number, snake in enumerate(self.snake_bodies):
            for other_snake_number,other_snake in enumerate(self.snake_bodies):
                for snake_piece_number, snake_piece in enumerate(other_snake):
                    # make sure it's not you and your own head
                    if snake_number == other_snake_number and snake_piece_number == 0:
                        continue

                    (x,y) = snake_piece
                    if x < 0 or y < 0 or x >= self.x or y >= self.y or snake[0] == snake_piece:
                        self.snake_is_alive[snake_number] = False
                        print("snake in waddup",snake)
                        print("waddup", self.snake_is_alive[snake_number], snake[0],snake_piece)
