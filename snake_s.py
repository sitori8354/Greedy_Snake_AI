import pygame
from pygame import *
from settings import *
from copy import deepcopy
from random import randrange


class Square:
    def __init__(self, pos, surface, is_apple=False):
        self.pos = pos
        self.surface = surface
        self.is_apple = is_apple
        self.is_tail = False
        self.dir = [-1, 0]  # [x, y] Direction

        if self.is_apple:
            self.dir = [0, 0]

    def draw(self, clr=SNAKE_CLR):
        x, y = self.pos[0], self.pos[1]
        ss, gs = SQUARE_SIZE, GAP_SIZE

        if self.dir == [-1, 0]:
            if self.is_tail:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))
            else:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss, ss - 2*gs))

        if self.dir == [1, 0]:
            if self.is_tail:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))
            else:
                pygame.draw.rect(self.surface, clr, (x * ss - gs, y * ss + gs, ss, ss - 2*gs))

        if self.dir == [0, 1]:
            if self.is_tail:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))
            else:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss - gs, ss - 2*gs, ss))

        if self.dir == [0, -1]:
            if self.is_tail:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))
            else:
                pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss))

        if self.is_apple:
            pygame.draw.rect(self.surface, clr, (x * ss + gs, y * ss + gs, ss - 2*gs, ss - 2*gs))

    def move(self, direction):
        self.dir = direction
        self.pos[0] += self.dir[0]
        self.pos[1] += self.dir[1]

    def hitting_wall(self):
        if (self.pos[0] <= -1) or (self.pos[0] >= ROWS) or (self.pos[1] <= -1) or (self.pos[1] >= ROWS):
            return True
        else:
            return False


class Snake:
    def __init__(self, surface):
        self.surface = surface
        self.is_dead = False
        self.squares_start_pos = [[ROWS // 2 + i, ROWS // 2] for i in range(INITIAL_SNAKE_LENGTH)]
        self.turns = {}
        self.dir = [-1, 0]
        self.score = 0
        self.moves_without_eating = 0
        self.apple = Square([randrange(ROWS), randrange(ROWS)], self.surface, is_apple=True)

        self.squares = []
        for pos in self.squares_start_pos:
            self.squares.append(Square(pos, self.surface))

        self.head = self.squares[0]
        self.tail = self.squares[-1]
        self.tail.is_tail = True

        self.path = []
        self.is_virtual_snake = False
        self.total_moves = 0
        self.won_game = False

        self.wander_times = 0

    def draw(self):
        self.apple.draw(APPLE_CLR)
        self.head.draw(HEAD_CLR)
        for sqr in self.squares[1:]:
            if self.is_virtual_snake:
                sqr.draw(VIRTUAL_SNAKE_CLR)
            else:
                sqr.draw()

    def set_direction(self, direction):
        if direction == 'left':
            #if not self.dir == [1, 0]:
            self.dir = [-1, 0]
            self.turns[self.head.pos[0], self.head.pos[1]] = self.dir
        if direction == "right":
            #if not self.dir == [-1, 0]:
            self.dir = [1, 0]
            self.turns[self.head.pos[0], self.head.pos[1]] = self.dir
        if direction == "up":
            #if not self.dir == [0, 1]:  # right, left or down???
            self.dir = [0, -1]  # down???
            self.turns[self.head.pos[0], self.head.pos[1]] = self.dir
        if direction == "down":
            #if not self.dir == [0, -1]:
            self.dir = [0, 1]
            self.turns[self.head.pos[0], self.head.pos[1]] = self.dir

    def handle_events(self, START, GAMEOVER):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'finish'

            elif event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == ord('d'):
                    self.set_direction('right')
                if event.key == K_UP or event.key == ord('w'):
                    self.set_direction('up')
                if event.key == K_DOWN or event.key == ord('s'):
                    self.set_direction('down')
                if event.key == K_LEFT or event.key == ord('a'):
                    self.set_direction('left')
                if event.key == K_RETURN and START == False:
                    return 'start'
                if event.key == K_RETURN and GAMEOVER == True:
                    return 'restart'

    def go_to(self, position): 
        if self.head.pos[0] - 1 == position[0]:  # path is on left of head
            self.set_direction('left')
        if self.head.pos[0] + 1 == position[0]:
            self.set_direction('right')
        if self.head.pos[1] - 1 == position[1]:
            self.set_direction('up')
        if self.head.pos[1] + 1 == position[1]:
            self.set_direction('down')

    def move(self):
        for j, sqr in enumerate(self.squares):
            p = (sqr.pos[0], sqr.pos[1])
            if p in self.turns:
                turn = self.turns[p]
                sqr.move([turn[0], turn[1]])
                if j == len(self.squares) - 1:
                    self.turns.pop(p)
            else:
                sqr.move(sqr.dir)
        self.moves_without_eating += 1

    def add_square(self):
        self.squares[-1].is_tail = False
        tail = self.squares[-1]  # Tail before adding new square

        direction = tail.dir
        if direction == [1, 0]:
            self.squares.append(Square([tail.pos[0] - 1, tail.pos[1]], self.surface))
        if direction == [-1, 0]:
            self.squares.append(Square([tail.pos[0] + 1, tail.pos[1]], self.surface))
        if direction == [0, 1]:
            self.squares.append(Square([tail.pos[0], tail.pos[1] - 1], self.surface))
        if direction == [0, -1]:
            self.squares.append(Square([tail.pos[0], tail.pos[1] + 1], self.surface))

        self.squares[-1].dir = direction
        self.squares[-1].is_tail = True  # Tail after adding new square

    def reset(self):
        self.__init__(self.surface)

    def hitting_self(self):
        for sqr in self.squares[1:]:
            if sqr.pos == self.head.pos:
                return True

    def generate_apple(self):
        self.apple = Square([randrange(ROWS), randrange(ROWS)], self.surface, is_apple=True)
        if not self.is_position_free(self.apple.pos):
            self.generate_apple()

    def eating_apple(self):
        if self.head.pos == self.apple.pos and not self.is_virtual_snake and not self.won_game:
            self.generate_apple()
            self.moves_without_eating = 0
            self.score += 1
            return True

    def is_position_free(self, position): # check whether there is snake body when generate apple
        if position[0] >= ROWS or position[0] < 0 or position[1] >= ROWS or position[1] < 0:
            return False
        for sqr in self.squares:
            if sqr.pos == position:
                return False
        return True

    def bfs(self, s, e):  # shortest path
        q = [s]
        visited = {tuple(pos): False for pos in GRID}

        visited[s] = True

        prev = {tuple(pos): None for pos in GRID} # find the parent node of each node
        while q:  # While queue is not empty
            node = q.pop(0)

            neighbors = ADJACENCY_DICT[node]

            for next_node in neighbors:
                if self.is_position_free(next_node) and not visited[tuple(next_node)]:
                    q.append(tuple(next_node))
                    visited[tuple(next_node)] = True
                    prev[tuple(next_node)] = node

        path = list()
        p_node = e

        while True:
            if prev[p_node] is None:
                return [] # Path not available
            p_node = prev[p_node]
            if p_node == s:
                path.append(e)
                return path # Path found
            path.insert(0, p_node)

    def wander_s_shape(self, node):
        neighbors = ADJACENCY_DICT[node]
        self.wander_times += 1
        for next_node in neighbors:
            if self.is_position_free(next_node):
                self.go_to(next_node)
                return
        return

    def check(self, START, GAMEOVER, COMMAND_KEY):
        if COMMAND_KEY == 'finish':
            return 'finish'
        elif COMMAND_KEY == 'start':
            return 'start'
        elif COMMAND_KEY == 'restart':
            return 'restart'

        if START and not GAMEOVER:
            self.draw()
            self.move()

        if self.hitting_self() or self.head.hitting_wall():
            #print("Snake is dead, trying again..")
            self.is_dead = True
            return 'dead'

        if self.moves_without_eating == MAX_MOVES_WITHOUT_EATING:
            self.is_dead = True
            #print("Snake got stuck, trying again..")
            return 'dead'

        if self.eating_apple():
            self.add_square()

    def update(self, START, GAMEOVER):

        COMMAND_KEY = self.handle_events(START, GAMEOVER) # direction adjusted by keyboard

        if self.head.pos[0]<ROWS and self.head.pos[0]>-1 and self.head.pos[1]<ROWS and self.head.pos[1]>-1 and self.wander_times == 0:\
               self.path=self.bfs(tuple(self.head.pos),tuple(self.apple.pos)) # direction adjusted by bfs

        if self.path:
            self.go_to(self.path[0])
        else:  # wander
            global final
            if not final and self.head.pos[0]<ROWS and self.head.pos[0]>-1 and self.head.pos[1]<ROWS and self.head.pos[1]>-1:
                self.wander_s_shape(tuple(self.head.pos))
            if self.wander_times >= randrange(4,13,4):
                self.wander_times = 0
            final = self.check(START, GAMEOVER, COMMAND_KEY)
            # print(self.wander_times)
            return final

        final = self.check(START, GAMEOVER, COMMAND_KEY)
        return final