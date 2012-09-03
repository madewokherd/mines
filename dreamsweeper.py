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

    def get_text_box(self, space, width, height):
        raise NotImplementedError()

    def space_at_point(self, x, y, width, height):
        raise NotImplementedError()

    def get_adjacent_spaces(self, space):
        raise NotImplementedError()

    # options:
    first_space_clear = False # First revealed space is always clear
    first_space_zero = False # First revealed space is always clear with no adjacent mines
    reveal_around_zeroes = False # Automatically reveal spaces adjacent to zeros

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

            for (space, (value, adjacent)) in self.known_spaces.iteritems():
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

        if self.reveal_around_zeroes and adjacent == 0:
            for s in self.get_adjacent_spaces(space):
                self.reveal_space(s)

        return True

    def reveal_space(self, space):
        if space in self.known_spaces:
            return False

        if self.first_space_zero and not self.known_spaces:
            self.add_known_space(space, 0, 0)
        elif self.first_space_clear and not self.known_spaces:
            self.add_known_space(space, 0, -1)

        possibility = self.get_possibility()

        value = possibility[space]

        if value:
            # mine
            adjacent = -1
        else:
            adjacent = sum(possibility[s] for s in self.get_adjacent_spaces(space))

        self.add_known_space(space, value, adjacent)

        return True

    def flag_space(self, space, value=None):
        if space in self.known_spaces:
            return False

        if value is None:
            new_value = self.flagged_spaces.get(space, 2)-1
        else:
            new_value = value if self.flagged_spaces.get(space, -1) != value else -1

        if new_value == -1:
            del self.flagged_spaces[space]
        else:
            self.flagged_spaces[space] = new_value

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

    def get_text_box(self, space, width, height):
        (x, y) = space

        left = x * (width-1) / self.width
        right = (x+1) * (width-1) / self.width
        top = y * (height-1) / self.height
        bottom = (y+1) * (height-1) / self.height

        return left, top, right-left, bottom-top

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
        return frozenset((x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1))

