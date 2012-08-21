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

import random
import sys
import unittest

import mines

class SolverTests(unittest.TestCase):
    # layouts is a sequence of tuples of the format:
    #  (description, informations, known_mine_spaces, known_clear_spaces, num_possibilities, probabilities)
    # description is a string that identifies the layout
    # informations is a sequence of tuples of the format:
    #  (total, space, space...)
    #  total is the number of mines in the given set of spaces
    # known_mine_spaces is a sequence of spaces that are known to be mines given the information
    # known_clear_spaces is a sequence of spaces that are known to be clear given the information
    # num_possibilities is the number of possible solutions; set this to 0 for unsolveable configurations
    # probabilities is a sequence of tuples of (space, solutions) where solutions is the number of solutions in which that space is a mine
    layouts = (
        ('nothing', (), (), (), 1, ()),
        ('empty', ((0,0,1,2,3),), (), (0,1,2,3), 1, ()),
        ('full', ((4,0,1,2,3),), (0,1,2,3), (), 1, ()),
        ('negative', ((-1,0,1,2,3),), (), (), 0, ()),
        ('overfull', ((5,0,1,2,3),), (), (), 0, ()),
        ('1/4', ((1,0,1,2,3),), (), (), 4, ((0,1), (1,1), (2,1), (3,1))),
        ('2/4', ((2,0,1,2,3),), (), (), 6, ((0,3), (1,3), (2,3), (3,3))),
        ('3/4', ((3,0,1,2,3),), (), (), 4, ((0,3), (1,3), (2,3), (3,3))),
        ('square', ((1,0,1),(1,1,2),(1,2,3),(2,0,3,4)), (4,), (), 2, ((0,1), (1,1), (2,1), (3,1))),
        ('triangle', ((1,0,1),(1,1,2),(1,2,0),), (), (), 0, ()),
        ('triangle2', ((1,0,1),(1,1,2),(2,2,0,3),), (2,0), (1,3), 1, ()),
        ('subset', ((1,0,1,2),(1,0,1),), (), (2,), 2, ((0,1), (1,1))),
        ('5/3', ((1,0,1),(1,1,2),(1,2,3),(1,3,4),(3,0,1,2,3,4)), (0,2,4), (1,3), 1, ()),
        ('5/2', ((1,0,1),(1,1,2),(1,2,3),(1,3,4),(2,0,1,2,3,4)), (1,3), (0,2,4), 1, ()),
        ('difference', ((1,0,1,2),(3,1,2,3,4),), (3,4), (0,), 2, ((1,1), (2,1))),
        ('3/3', ((1,0,1,2),(1,2,3,4),), (), (), 5, ((0,2), (1,2), (2,1), (3,2), (4,2))),
        ('badintersection', ((1,0,1,2,3),(3,1,2,3,4)), (), (), 0, ()),
        ('auto1', ((6,1,2,4,6,7,9,11,13),(3,3,4,13,6),(3,0,1,2,3,5,8,10,11,12),(3,10,5,13,7)), (4,6,7,13), (3,), 24, ()),
    )

    longMessage = True

    def test_solve(self):
        for desc, information_descs, known_mine_spaces, known_clear_spaces, expected_possibilities, expected_probabilities in self.layouts:
            informations = []
            spaces = set()
            for information in information_descs:
                informations.append(mines.Information(frozenset(information[1:]), information[0]))
                spaces.update(information[1:])

            known_spaces = set(known_mine_spaces)
            known_spaces.update(known_clear_spaces)

            solver = mines.Solver(spaces)

            try:
                for information in informations:
                    solver.add_information(information)

                solver.solve()

                self.assertNotEqual(expected_possibilities, 0, desc)

                self.assertEqual(set(solver.solved_spaces), known_spaces, desc)
                for space in known_mine_spaces:
                    self.assertEqual(solver.solved_spaces[space], 1, '%s: %s' % (desc, space))
                for space in known_clear_spaces:
                    self.assertEqual(solver.solved_spaces[space], 0, '%s: %s' % (desc, space))
            except mines.UnsolveableException:
                self.assertEqual(expected_possibilities, 0, desc)
            else:
                probabilities, num_possibilities = solver.get_probabilities()

                self.assertEqual(num_possibilities, expected_possibilities, desc)

                unknown_spaces = set(spaces)
                unknown_spaces.difference_update(known_spaces)

                self.assertEqual(unknown_spaces, set(probabilities))

                for space, possibilities in expected_probabilities:
                    self.assertEqual(probabilities[space], possibilities, '%s: %s' % (desc, space))

    def test_probabilities(self):
        for desc, information_descs, known_mine_spaces, known_clear_spaces, expected_possibilities, expected_probabilities in self.layouts:
            informations = []
            spaces = set()
            for information in information_descs:
                informations.append(mines.Information(frozenset(information[1:]), information[0]))
                spaces.update(information[1:])

            expected_probabilities = dict(expected_probabilities)

            solver = mines.Solver(spaces)

            try:
                for information in informations:
                    solver.add_information(information)
                probabilities, num_possibilities = solver.get_probabilities()
            except mines.UnsolveableException:
                self.assertEqual(expected_possibilities, 0, desc)
            else:
                self.assertEqual(num_possibilities, expected_possibilities, desc)

                if expected_possibilities == 0:
                    continue

                for space in spaces:
                    if space in known_mine_spaces:
                        if space in solver.solved_spaces:
                            self.assertEqual(solver.solved_spaces[space], 1, '%s: %s' % (desc, space))
                            continue
                        expected_probability = num_possibilities
                    elif space in known_clear_spaces:
                        if space in solver.solved_spaces:
                            self.assertEqual(solver.solved_spaces[space], 0, '%s: %s' % (desc, space))
                            continue
                        expected_probability = 0
                    elif space in expected_probabilities:
                        expected_probability = expected_probabilities[space]
                    else:
                        continue
                    self.assertEqual(probabilities[space], expected_probability, '%s: %s' % (desc, space))

    def test_possibility(self):
        desc = None

        try:
            for desc, information_descs, known_mine_spaces, known_clear_spaces, expected_possibilities, expected_probabilities in self.layouts:
                informations = []
                spaces = set()
                for information in information_descs:
                    informations.append(mines.Information(frozenset(information[1:]), information[0]))
                    spaces.update(information[1:])

                expected_probabilities = dict(expected_probabilities)

                solver = mines.Solver(spaces)

                try:
                    for information in informations:
                        solver.add_information(information)

                    solver.solve()
                except mines.UnsolveableException:
                    self.assertEqual(expected_possibilities, 0, desc)
                else:
                    possibility = solver.get_possibility()

                    for information in information_descs:
                        self.assertEqual(
                            sum(possibility[space] for space in information[1:]),
                            information[0])
        except:
            print("Failing test: %s" % desc)
            raise

def choose_n(rand, n, pool):
    pool = list(pool)
    result = []
    for i in range(n):
        index = rand.randint(0, len(pool)-1)
        result.append(pool[index])
        pool[index] = pool[-1]
        pool.pop(-1)
    return result

class RandomTests(unittest.TestCase):
    def run_random_test(self, rand):
        num_spaces = rand.randint(1,15)

        actual_state = [rand.randint(0,1) for x in range(num_spaces)]

        informations = []

        try:
            solver = mines.Solver(range(num_spaces))

            while len(solver.solved_spaces) != num_spaces:
                solved_spaces = set(solver.solved_spaces)
                unsolved_spaces = set(range(num_spaces)) - solved_spaces

                spaces = choose_n(rand, rand.randint(1, len(unsolved_spaces)), unsolved_spaces) + \
                    choose_n(rand, rand.randint(0, len(solved_spaces)), solved_spaces)

                num_mines = sum(actual_state[i] for i in spaces)

                information = mines.Information(frozenset(spaces), num_mines)

                informations.append(information)

                solver.add_information(information)

                probabilities, num_possibilities = solver.get_probabilities()

                prob_solved_spaces = 0
                for i in range(num_spaces):
                    if i in solver.solved_spaces:
                        prob_solved_spaces += 1
                    elif i in probabilities and probabilities[i] in (0, num_possibilities):
                        prob_solved_spaces += 1

                solver.solve()

                self.assertNotEqual(num_possibilities, 0)

                self.assertEqual(prob_solved_spaces, len(solver.solved_spaces))

                for spaces, total in informations:
                    expected_value = 0
                    for i in spaces:
                        if i in solver.solved_spaces:
                            expected_value += solver.solved_spaces[i] * num_possibilities
                        else:
                            expected_value += probabilities[i]
                    self.assertEqual(expected_value, num_possibilities * total)

            self.assertEqual(actual_state, [solver.solved_spaces[i] for i in range(num_spaces)])
        except:
            print("State: %s" % actual_state)
            print("Informations: %s" % informations)
            raise

    def run_random_unsolvable(self, rand):
        num_spaces = rand.randint(1,15)

        actual_state = [rand.randint(0,1) for x in range(num_spaces)]

        informations = []

        try:
            solver = mines.Solver(range(num_spaces))

            while len(solver.solved_spaces) != num_spaces:
                solved_spaces = set(solver.solved_spaces)

                unsolved_spaces = set(range(num_spaces)) - solved_spaces

                spaces = choose_n(rand, rand.randint(1, len(unsolved_spaces)), unsolved_spaces) + \
                    choose_n(rand, rand.randint(0, len(solved_spaces)), solved_spaces)

                num_mines = sum(actual_state[i] for i in spaces)

                if len(informations) == 0:
                    new_num_mines = rand.randint(0, len(spaces)-1)
                    if new_num_mines == num_mines:
                        new_num_mines = len(spaces)
                    num_mines = new_num_mines

                information = mines.Information(frozenset(spaces), num_mines)

                informations.append(information)

                solver.add_information(information)

                probabilities, num_possibilities = solver.get_probabilities()

                prob_solved_spaces = 0
                for i in range(num_spaces):
                    if i in solver.solved_spaces:
                        prob_solved_spaces += 1
                    elif i in probabilities and probabilities[i] in (0, num_possibilities):
                        prob_solved_spaces += 1

                solver.solve()

                self.assertNotEqual(num_possibilities, 0) # unsolvable, solve() should have raised an exception

                self.assertEqual(prob_solved_spaces, len(solver.solved_spaces))

                for spaces, total in informations:
                    expected_value = 0
                    for i in spaces:
                        if i in solver.solved_spaces:
                            expected_value += solver.solved_spaces[i] * num_possibilities
                        else:
                            expected_value += probabilities[i]

                    self.assertEqual(expected_value, num_possibilities * total)

            self.assertNotEqual(actual_state, [solver.solved_spaces[i] for i in range(num_spaces)])
        except mines.UnsolveableException:
            # expected
            pass
        except:
            print("State: %s" % actual_state)
            print("Informations: %s" % informations)
            raise

    def run_random_tests(self, seed):
        try:
            rand = random.Random(seed)
            for i in range(500):
                self.run_random_test(rand)
            for i in range(500):
                self.run_random_unsolvable(rand)
        except:
            print("Failing seed: %s" % seed)
            raise

    def test_random(self):
        self.run_random_tests(random.SystemRandom().randint(-sys.maxint-1, sys.maxint))

if __name__ == '__main__':
    unittest.main()

