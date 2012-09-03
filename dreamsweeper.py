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

class Board(object):
    spaces = () # should be set to frozenset of spaces by subclass's __init__

    def __init__(self, mines=-1):
        if type(self) == Board:
            raise TypeError("Board is an abstract class")

        self.mines = mines
        self.known_spaces = {}
        self.flagged_spaces = {}

    def get_polygon(self, space, width, height):
        raise NotImplementedError()

    def space_at_point(self, x, y, width, height):
        raise NotImplementedError()

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

