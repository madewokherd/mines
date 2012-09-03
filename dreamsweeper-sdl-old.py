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

last_revealed = (-1, -1)
show_last_revealed = False

class DreamBoard(object):
    def __init__(self, width, height, count):
        self.width = width
        self.height = height
        self.count = count
        self.solver = None
        self.values = [UNKNOWN] * (width * height)
        self.spaces = frozenset((x, y) for x in range(width) for y in range(height))
        self.possibility = None

    def clear(self):
        self.values = [UNKNOWN] * (width * height)
        self.solver = None
        self.possibility = None

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

    def _is_removing_information(self, x, y, value):
        return self.values[x + y * width] not in (UNKNOWN, UNKNOWN_Q, value) and \
            not (value < 9 and self.values[x + y * width] == CLEAR_Q)

    def _recheck_possibility(self, x, y, value):
        if self.possibility is not None:
            if value == MINE:
                if self.possibility[x, y] != 1:
                    self.possibility = None
            elif value == CLEAR_Q:
                if self.possibility[x, y] != 0:
                    self.possibility = None
            elif value < 9:
                if self.possibility[x, y] != 0:
                    self.possibility = None
                elif sum(self.possibility.get((i, j), 0) for i in range(x-1, x+2) for j in range(y-1, y+2)) != value:
                    self.possibility = None

    def _set_value(self, x, y, value):
        if self.solver:
            if self._is_removing_information(x, y, value):
                # cannot remove information from solver
                self.solver = None
                self.possibility = None
            else:
                self._add_value_to_solver(self.solver, x, y, value)
        self._recheck_possibility(x, y, value)
        self.values[x + y * self.width] = value

    def create_solver(self, exclude = None):
        solver = mines.Solver(self.spaces)
        if self.count != -1:
            solver.add_information(mines.Information(self.spaces, self.count))
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) == exclude:
                    continue
                self._add_value_to_solver(solver, x, y, self.values[x + y * self.width])
        solver.solve()
        return solver

    def get_solver(self):
        if not self.solver:
            self.solver = self.create_solver()
        return self.solver

    def get_solver_where(self, x, y, value):
        if self._is_removing_information(x, y, value):
            solver = self.create_solver((x, y))
        else:
            solver = self.get_solver().copy()
        self._add_value_to_solver(solver, x, y, value)
        solver.solve()
        return solver

    def try_set_value(self, x, y, value):
        try:
            solver = self.get_solver_where(x, y, value)
        except mines.UnsolveableException:
            return False
        self.solver = solver
        self.values[x + y * self.width] = value
        return True

    def get_mine_probabilities(self):
        solver = self.get_solver()
        solver.solve()
        return solver.get_probabilities()

    def reveal_space(self, x, y, discard=False, clear=False):
        if discard and not clear:
            self.set_value(x, y, UNKNOWN)

        if clear and (discard or self.get_value(x, y) >= 9):
            if not self.try_set_value(x, y, CLEAR_Q):
                return False

        if self.possibility is None:
            self.possibility = self.get_solver().get_possibility()

        if self.possibility[x, y] == 1:
            self.set_value(x, y, MINE)
        else:
            self.set_value(x, y, sum(self.possibility.get((i, j), 0) for i in range(x-1, x+2) for j in range(y-1, y+2)))
        return True

    def clear_space(self, x, y):
        # Reveal x,y but make it a non-mine if possible
        if not self.reveal_space(x, y, discard=True, clear=True):
            self.set_value(x, y, MINE)
            return

    def reveal_mine_space(self, x, y):
        # Reveal x,y but make it a mine if possible
        if not self.try_set_value(x, y, MINE):
            self.reveal_space(x, y, discard=True)

    def set_value(self, x, y, value):
        self.try_set_value(x, y, value)

    def mark_known_spaces(self, value = None):
        result = False
        solver = self.get_solver()
        solver.solve()
        
        solved_spaces = solver.solved_spaces.copy()
        
        for x, y in solved_spaces:
            if self.get_value(x, y) == UNKNOWN:
                if value is not None and solved_spaces[x, y] != value:
                    continue
                self._set_value(x, y, MINE if solved_spaces[x, y] else CLEAR_Q)
                return True
        return result

    def reveal_marked_spaces(self):
        result = False
        solver = self.get_solver()
        solver.solve()
        
        solved_spaces = solver.solved_spaces.copy()
        
        for x in range(self.width):
            for y in range(self.height):
                if self.get_value(x, y) == CLEAR_Q:
                    self.reveal_space(x, y, discard=True)
                    result = True
        
        return result

    def reveal_around_zeroes(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.get_value(x, y) == 0:
                    for xi in range(max(x-1, 0), min(x+2, self.width)):
                        for yi in range(max(y-1, 0), min(y+2, self.height)):
                            if self.get_value(xi, yi) >= 9 and self.get_value(xi, yi) != CLEAR_Q:
                                #self.reveal_space(xi, yi)
                                self.set_value(xi, yi, CLEAR_Q)
                                return True
        
        return False

    def reveal_sparse(self):
        global last_revealed
        global show_last_revealed
        solver = self.get_solver()
        spaces_to_reveal = set()
        for space in solver.solved_spaces:
            if self.get_value(*space) in (UNKNOWN, UNKNOWN_Q):
                show_last_revealed = True
                return False
            elif self.get_value(*space) == CLEAR_Q:
                spaces_to_reveal.add(space)
        if spaces_to_reveal:
            space = random.choice(list(spaces_to_reveal))
            self.reveal_space(*space)
            last_revealed = space
            show_last_revealed = False
            return True
        solved_spaces = set(solver.solved_spaces)
        if solved_spaces == set(solver.spaces):
            show_last_revealed = False
            return False
        space = random.choice(list(solver.spaces - solved_spaces))
        self.reveal_space(*space)
        last_revealed = space
        show_last_revealed = False
        return True

    def _hint_score(self, item):
        space, probability = item
        solver = self.get_solver()
        informations = solver.informations_for_space[space]
        return probability, -max(len(i.spaces) for i in informations), -len(informations)

    def hint(self):
        solver = self.get_solver()
        solver.solve()

        for x, y in solver.solved_spaces:
            if solver.solved_spaces[x, y] == 0 and self.get_value(x, y) >= 9:
                self.set_value(x, y, CLEAR_Q)
                return True

        probabilities, _dummy = solver.get_probabilities()
        
        items = list(probabilities.iteritems())
        random.shuffle(items)
        
        x, y = min(items, key=self._hint_score)[0]
        self.set_value(x, y, CLEAR_Q)
        return True
        
        total = sum(probabilities.itervalues())

        if total == 0:
            return False
        
        choice = random.randint(1, total)

        cumsum = 0
        for x, y in probabilities:
            cumsum += probabilities[x, y]
            if cumsum >= choice:
                self.clear_space(x, y)
                return True

    def maybe_hint(self):
        solver = self.get_solver()
        solver.solve()

        for x, y in solver.solved_spaces:
            if solver.solved_spaces[x, y] == 0 and self.get_value(x, y) >= 9:
                break
            elif solver.solved_spaces[x, y] == 1 and self.get_value(x, y) != MINE:
                break
        else:
            return self.hint()
        return False

def draw_board(board, switches):
    screen = pygame.display.get_surface()

    if '/p' in switches:
        probabilities, total = board.get_mine_probabilities()

    for x in range(board.width):
        for y in range(board.height):
            value = board.get_value(x, y)

            screen.blit(mines_image, (x * grid_size, y * grid_size),
                         Rect(0, grid_size * value, grid_size, grid_size))

            if value == UNKNOWN and '/p' in switches:
                if (x, y) in board.solver.solved_spaces:
                    g = board.solver.solved_spaces[x, y] * 255
                    border = 1
                elif (x, y) in probabilities:
                    g = (probabilities[x, y] * 255 / total)
                    border = 2
                else:
                    continue
                pygame.draw.rect(screen, Color(g, 255-g, min(g, 255-g), 255), Rect(x * grid_size + border, y * grid_size + border, grid_size - border*2, grid_size - border*2))

    if show_last_revealed:
        x, y = last_revealed
        pygame.draw.rect(screen, Color(255, 255, 0, 32), Rect(x * grid_size-1, y * grid_size-1, grid_size+1, grid_size+1), 1)

    pygame.display.flip()

key_values = {
    u'0': 0,
    u'1': 1,
    u'2': 2,
    u'3': 3,
    u'4': 4,
    u'5': 5,
    u'6': 6,
    u'7': 7,
    u'8': 8,
    u'm': MINE,
    u' ': UNKNOWN,
    u'c': CLEAR_Q,
    u'?': UNKNOWN_Q,
    }

def run(width, height, count):
    global show_last_revealed
    board = DreamBoard(width, height, count)

    window = pygame.display.set_mode((width * grid_size, height * grid_size))

    x = y = 0

    prev_count = count

    while True:
        if '/d' in switches:
            __import__('time').sleep(0.2)

        draw_board(board, switches)

        if '/r' in switches and board.reveal_marked_spaces():
            continue

        if '/0' in switches and board.reveal_around_zeroes():
            continue

        if '/h' in switches and board.maybe_hint():
            continue

        if '/m' in switches and board.mark_known_spaces():
            continue

        if '/mm' in switches and board.mark_known_spaces(1):
            continue

        if '/mc' in switches and board.mark_known_spaces(0):
            continue

        if '/s' in switches and board.reveal_sparse():
            continue

        cur_count = count - len(list(x for x in board.values if x == MINE))
        if cur_count != prev_count:
            prev_count = cur_count
            print cur_count

        draw_board(board, switches)
        
        events = [pygame.event.wait()]
        while events:
            event = events.pop(0)
            if event.type == QUIT:
                return
            elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                x = event.pos[0] / grid_size
                y = event.pos[1] / grid_size
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    #board.clear_space(x, y)
                    board.set_value(x, y, CLEAR_Q)
                    show_last_revealed = False
                elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                    #board.reveal_mine_space(x, y)
                    board.set_value(x, y, MINE)
                    show_last_revealed = False
            elif event.type == KEYDOWN:
                if event.unicode in key_values:
                    board.set_value(x, y, key_values[event.unicode])
                    show_last_revealed = False
                elif event.unicode == u'h':
                    board.hint()
                    show_last_revealed = False
                elif event.unicode == u'r':
                    board.reveal_space(x, y, discard=True)
                    show_last_revealed = False
                elif event.unicode == u's':
                    board.mark_known_spaces()
                    show_last_revealed = False
                elif event.unicode == u'p':
                    switches.symmetric_difference_update(set(['/p']))
                elif event.key == pygame.K_BACKSPACE:
                    board.clear()
                    show_last_revealed = False
            if not events:
                events = pygame.event.get()
            draw_board(board, switches)

if __name__ == '__main__':
    switches = set()
    argv = []
    for arg in sys.argv[1:]:
        if arg.startswith('/'):
            switches.add(arg)
        else:
            argv.append(arg)
    width = int(argv[0])
    height = int(argv[1])
    count = int(argv[2])

    run(width, height, count)

