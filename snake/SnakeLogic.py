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


# def generate_starter_snakes(x, y, number_snakes):
#     number_squares = x*y
#     starting_positions = random.sample(range(number_squares), 2)

#     starter_snakes = list()
#     for i in range(number_snakes):
#         # TODO: needs extending to multiple snakes, currently assuming only 2
#         if i == 0:
#             id = -1
#         else:
#             id = i
#         body = [(starting_positions[i] % x, int(starting_positions[i]/x))]*3
#         health = 100
#         died_turn = 0
#         died_reason = ""

#         starter_snakes.append(Snake(id, body, health, died_turn, died_reason))

#     return starter_snakes


# class Snake():

#     def __init__(self, id, body, health, died_turn, died_reason):
#         self.id = id
#         self.body = body
#         self.health = health
#         self.died_turn = died_turn
#         self.died_reason = died_reason


# class Board():

#     # list of all 8 directions on the board
#     # as (x,y) offsets
#     # __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

#     def __init__(self, x, y, snakes, snacks, hazards, turn):
#         "Set up initial board configuration."

#         # self.x = x
#         # self.y = y
#         # self.snakes = snakes
#         # self.snacks = snacks
#         # self.hazards = hazards
#         # self.turn = turn

#         # # TODO: make this multiplayer. need to get lines on my brain first.
#         # # list of three identical tuples from the sample above (sample does not overlap)
#         # self.snake_bodies: list(tuple) = list()
#         # self.snake_health = list()
#         # self.snake_is_alive = list()

#         # for i in range(number_snakes):
#         #     self.snake_bodies.append(
#         #         [(starting_positions[i] % x, int(starting_positions[i]/x))]*3)
#         #     self.snake_health.append(100)
#         #     self.snake_is_alive.append(True)

#         # print(self.snake_bodies)

#     # # add [][] indexer syntax to the Board
#     # def __getitem__(self, index):
#     #     return self.pieces[index]

#     # put a random snake of length 3 on the board

#     def legal_moves_from_point(self, point):

#         # print("moving from point:", point)

#         (x, y) = point
#         legal_points = list()

#         for direction in ["up", "down", "left", "right"]:
#             if direction == "up":
#                 candidate = (x, y+1)
#             if direction == "down":
#                 candidate = (x, y-1)
#             if direction == "left":
#                 candidate = (x-1, y)
#             if direction == "right":
#                 candidate = (x+1, y)

#             if self.point_is_legal(candidate):
#                 legal_points.append(candidate)

#         return legal_points

#     def point_is_legal(self, point):

#         # check bounds
#         (x, y) = point
#         if x < 0 or x >= self.x or y < 0 or y >= self.y:
#             return False

#         # check other snakes
#         for snake in self.snakes:
#             for snake_point in snake.body[:-1]:
#                 # check all points except the last one since that won't be there next time
#                 # TODO: it might be there if they snack. account for this.
#                 if point == snake_point:
#                     return False
#         return True

#     def get_legal_moves(self, snake_id):
#         "Returns all the legal moves for the given snake_number."
#         for snake in self.snakes:
#             if snake.id == snake_id:
#                 return self.legal_moves_from_point(snake.body[0])
#         return list()

#     # def has_legal_moves(self):
#     #     for y in range(self.n):
#     #         for x in range(self.n):
#     #             if self[x][y] == 0:
#     #                 return True
#     #     return False

#     def is_lost(self, snake_id):
#         for snake in self.snakes:
#             if snake.id == snake_id and snake.died_reason=="":
#                 return False
#         return True

#     def is_ended(self):
#         remaining_snakes = list()
#         for snake in self.snakes:
#             if snake.died_reason == "":
#                 remaining_snakes.append(snake)
#         if len(remaining_snakes) == 1:
#             return remaining_snakes[0].id
#         if len(remaining_snakes) == 0:
#             return 1e-4
#         return 0


#     def execute_move(self, move, snake_id):

#         # add the new move and remove the last piece
#         for snake in self.snakes:
#             if snake.id != snake_id:
#                 continue

#             snake.body.insert(0, move)
#             snake.body.pop()

#             for snack in self.snacks:
#                 if snack == move:
#                     snake.body.append(snake.body[-1])
#                     # can stop here to speed up, no snacks will overlap
#                     break


#     def check_deaths(self):
#         for snake in self.snakes:
#             for other_snake in self.snakes:
#                 for other_snake_piece in other_snake.body:
#                     # make sure it's not you and your own head
#                     if snake.id == other_snake.id and other_snake_piece == snake.body[0]:
#                         continue

#                     (x, y) = other_snake_piece
#                     if x < 0 or y < 0 or x >= self.x or y >= self.y:
#                         snake.died_turn = self.turn
#                         snake.died_reason = "out of bounds"
#                     if snake.body[0] == other_snake_piece:
#                         snake.died_turn = self.turn
#                         snake.died_reason = "collided with snake"
    
#     def to_string(self):
#         return "{}:{}:{}:{}:{}".format(self.x,self.y,self.snacks,self.hazards, 
#                 ["[{}:{}:{}:{}]".format(snake.body,snake.health,snake.died_turn, snake.died_reason) for snake in self.snakes])


