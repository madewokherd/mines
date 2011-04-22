# Copyright (C) 2011 by Vincent Povirk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import random
import sys

random = random.SystemRandom()

import pygame
from pygame.locals import *

import mines

mines_image = pygame.image.load('mines.bmp')

grid_size = mines_image.get_width()

UNKNOWN = 9
MINE = 10
UNKNOWN_Q = 11
CLEAR_Q = 15

revealed_values = (MINE, 0, 1, 2, 3, 4, 5, 6, 7, 8)

class DreamBoard(object):
    def __init__(self, width, height, count):
        self.width = width
        self.height = height
        self.count = count
        self.solver = None
        self.values = [UNKNOWN] * (width * height)
        self.spaces = frozenset((x, y) for x in range(width) for y in range(height))

    def get_value(self, x, y):
        return self.values[x + y * self.width]

    def _add_value_to_solver(self, solver, x, y, value):
        if value < 9:
            if solver.solved_spaces.get((x, y), 0) != 0:
                raise mines.UnsolveableException()
            solver.add_known_value((x, y), 0)
            spaces = frozenset(self.spaces.intersection((x+i, y+j) for i in range(-1, 2) for j in range(-1, 2)))
            solver.add_information(mines.Information(spaces, value))
        elif value == MINE:
            if solver.solved_spaces.get((x, y), 1) != 1:
                raise mines.UnsolveableException()
            solver.add_known_value((x, y), 1)
        elif value == CLEAR_Q:
            if solver.solved_spaces.get((x, y), 0) != 0:
                raise mines.UnsolveableException()
            solver.add_known_value((x, y), 0)

    def _set_value(self, x, y, value):
        if self.solver:
            if self.values[x + y * width] not in (UNKNOWN, UNKNOWN_Q):
                # cannot remove information from solver
                self.solver = None
            else:
                self._add_value_to_solver(self.solver, x, y, value)
        self.values[x + y * self.width] = value

    def _get_solver(self):
        if not self.solver:
            self.solver = mines.Solver(self.spaces)
            self.solver.add_information(mines.Information(self.spaces, self.count))
            for x in range(self.width):
                for y in range(self.height):
                    self._add_value_to_solver(self.solver, x, y, self.values[x + y * self.width])
            self.solver.solve()
        return self.solver

    def get_probabilities(self, x, y):
        solver = self._get_solver()
        
        solvers = [None] * 10
        
        result = [0] * 10
        
        num_solveable = 0

        for i, value in enumerate(revealed_values):
            try:
                new_solver = solver.copy()

                self._add_value_to_solver(new_solver, x, y, value)
                
                new_solver.solve()
                
                solvers[i] = new_solver
                
                num_solveable += 1

            except mines.UnsolveableException:
                # 0 possibilities
                pass

        if num_solveable == 1:
            for i in range(len(revealed_values)):
                if solvers[i] is not None:
                    result[i] = 1
            return result

        for i in range(len(revealed_values)):
            if solvers[i] is not None:
                try:
                    _dummy, result[i] = solvers[i].get_probabilities()
                except mines.UnsolveableException:
                    # FIXME: This shouldn't happen?
                    pass

        return result

    def reveal_space(self, x, y):
        self._set_value(x, y, UNKNOWN)
        
        probabilities = self.get_probabilities(x, y)
        
        total = sum(probabilities) or 1

        choice = random.randint(1, total)
        
        cumsum = 0
        for i, probability in enumerate(probabilities):
            cumsum += probability
            if cumsum >= choice:
                value = revealed_values[i]
                break
        else:
            # this shouldn't happen
            value = UNKNOWN_Q
        
        self._set_value(x, y, value)

    def clear_space(self, x, y):
        try:
            self._set_value(x, y, CLEAR_Q)
            self._get_solver().solve()
        except mines.UnsolveableException:
            self.solver = None
            self.set_value(x, y, MINE)
            return
        
        probabilities = self.get_probabilities(x, y)
        
        total = sum(probabilities) or 1

        choice = random.randint(1, total)
        
        cumsum = 0
        for i, probability in enumerate(probabilities):
            cumsum += probability
            if cumsum >= choice:
                value = revealed_values[i]
                break
        else:
            value = UNKNOWN_Q
        
        self._set_value(x, y, value)

    def set_value(self, x, y, value):
        self._set_value(x, y, UNKNOWN)
        
        solver = self._get_solver()
        
        new_solver = solver.copy()
        
        try:
            self._add_value_to_solver(new_solver, x, y, value)
            
            new_solver.solve()
        except mines.UnsolveableException:
            value = UNKNOWN_Q
        
        self._set_value(x, y, value)

def draw_board(board):
    screen = pygame.display.get_surface()

    for x in range(board.width):
        for y in range(board.height):
            value = board.get_value(x, y)
            screen.blit(mines_image, (x * grid_size, y * grid_size),
                         Rect(0, grid_size * value, grid_size, grid_size))

    pygame.display.flip()

key_values = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    'm': MINE,
    ' ': UNKNOWN,
    'c': CLEAR_Q,
    '?': UNKNOWN_Q,
    }

def run(width, height, count):
    board = DreamBoard(width, height, count)

    window = pygame.display.set_mode((width * grid_size, height * grid_size))

    x = y = 0

    while True:
        draw_board(board)
        
        events = pygame.event.get()
        if not events:
            events = (pygame.event.wait(),)
        for event in events:
            if event.type == QUIT:
                return
            elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                x = event.pos[0] / grid_size
                y = event.pos[1] / grid_size
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    board.reveal_space(x, y)
                elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                    board.clear_space(x, y)
            elif event.type == KEYDOWN:
                if chr(event.key) in key_values:
                    board.set_value(x, y, key_values[chr(event.key)])

if __name__ == '__main__':
    width = int(sys.argv[1])
    height = int(sys.argv[2])
    count = int(sys.argv[3])

    run(width, height, count)

