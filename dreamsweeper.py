# Copyright (C) 2012 by Vincent Povirk
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

from __future__ import division

import mines

class Board(object):
    spaces = () # should be set to frozenset of spaces by subclass's __init__

    def get_polygon(self, space, width, height):
        raise NotImplementedError()

    def space_at_point(self, x, y, width, height):
        raise NotImplementedError()

    def get_adjacent_spaces(self, space):
        raise NotImplementedError()

    _solver = None
    _possibility = None

    def __init__(self, mines=-1):
        if type(self) == Board:
            raise TypeError("Board is an abstract class")

        self.mines = mines
        self.known_spaces = {}
        self.flagged_spaces = {}

    def get_solver(self):
        if self._solver is None:
            solver = mines.Solver(self.spaces)

            if self.mines != -1:
                solver.add_information(mines.Information(self.spaces, self.mines))

            for (space, (value, adjacent)) in self.known_spaces:
                solver.add_known_value(space, value)
                if adjacent != -1:
                    solver.add_information(mines.Information(frozenset(self.get_adjacent_spaces(space)), adjacent))

            self._solver = solver

        return self._solver

    def get_possibility(self):
        if self._possibility is None:
            solver = self.get_solver()

            self._possibility = solver.get_possibility()

        return self._possibility

    def add_known_space(self, space, value, adjacent):
        self.known_spaces[space] = (value, adjacent)

        if space in self.flagged_spaces:
            del self.flagged_spaces[space]

        return True

    def reveal_space(self, space):
        if space in self.known_spaces:
            return

        possibility = self.get_possibility()

        value = possibility[space]

        if value:
            # mine
            adjacent = -1
        else:
            adjacent = sum(possibility[s] for s in self.get_adjacent_spaces(space))

        self.add_known_space(space, value, adjacent)

        return True

class SquareBoard(Board):
    def __init__(self, width=12, height=12, mines=36):
        self.spaces = frozenset((x, y) for x in range(width) for y in range(height))
        self.width = width
        self.height = height

        Board.__init__(self, mines)

    def get_polygon(self, space, width, height):
        (x, y) = space

        left = x * (width-1) / self.width
        right = (x+1) * (width-1) / self.width
        top = y * (height-1) / self.height
        bottom = (y+1) * (height-1) / self.height

        return ((left, top), (right, top), (right, bottom), (left, bottom))

    def space_at_point(self, x, y, width, height):
        result = (int(x * self.width // (width+1)), int(y * self.height // (height+1)))

        if result in self.spaces:
            return result
        else:
            return None

    def get_adjacent_spaces(self, space):
        x, y = space
        min_x = max(0, x-1)
        max_x = min(self.width-1, x+1)
        min_y = max(0, y-1)
        max_y = min(self.height-1, y+1)
        return frozenset((x, y) for x in range(min_x, max_x - min_x + 1) for y in range(min_y, max_y - min_y + 1))

