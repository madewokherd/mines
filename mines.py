
import collections
import sys

class exception(Exception):
    pass

class UnsolveableException(exception):
    pass

Information = collections.namedtuple('Information', ('spaces', 'count'))

class Solver(object):
    def __init__(self, spaces):
        self.spaces = frozenset(spaces)
        self.solved_spaces = dict()
        self.information = set()
        self.informations_for_space = collections.defaultdict(set)

        self.spaces_with_new_information = set()

    def add_information(self, information):
        if information.count < 0 or information.count > len(information.spaces):
            raise UnsolveableException()
        if not information.spaces:
            raise exception("This shouldn't happen")
        self.information.add(information)
        for space in information.spaces:
            self.informations_for_space[space].add(information)
        self.spaces_with_new_information.update(information.spaces)

    def remove_information(self, information):
        self.information.remove(information)
        for space in information.spaces:
            self.informations_for_space[space].remove(information)

    def solve(self):
        while self.spaces_with_new_information:
            space = self.spaces_with_new_information.pop()

            if space in self.solved_spaces:
                value = self.solved_spaces[space]
                for information in list(self.informations_for_space[space]):
                    new_information = Information(
                        information.spaces.difference((space,)),
                        information.count - value)
                    self.remove_information(information)
                    if new_information.spaces:
                        self.add_information(new_information)

                continue

            for information in self.informations_for_space[space]:
                if information.count == 0 or information.count == len(information.spaces):
                    new_value = 0 if information.count == 0 else 1
                    self.spaces_with_new_information.update(information.spaces)
                    for space in information.spaces:
                        if space in self.solved_spaces:
                            if self.solved_spaces[space] != new_value:
                                raise UnsolveableException()
                        else:
                            self.solved_spaces[space] = new_value
                    self.remove_information(information)
                    break

                breaking = True

                for other_information in self.informations_for_space[space]:
                    if other_information is information:
                        continue

                    if information.spaces.issubset(other_information.spaces):
                        new_information = Information(
                            other_information.spaces.difference(information.spaces),
                            other_information.count - information.count)
                        self.remove_information(other_information)
                        self.add_information(new_information)
                        self.spaces_with_new_information.add(space)
                        break

                    if other_information.spaces.issubset(information.spaces):
                        new_information = Information(
                            information.spaces.difference(other_information.spaces),
                            information.count - other_information.count)
                        self.remove_information(information)
                        self.add_information(new_information)
                        self.spaces_with_new_information.add(space)
                        break

                    if other_information.count - len(other_information.spaces.difference(information.spaces)) == information.count:
                        new_spaces = other_information.spaces.difference(information.spaces)
                        new_information = Information(
                            new_spaces,
                            len(new_spaces))
                        self.add_information(new_information)
                        new_information = Information(
                            other_information.spaces.difference(new_spaces),
                            other_information.count - len(new_spaces))
                        self.add_information(new_information)
                        self.remove_information(other_information)
                        self.spaces_with_new_information.add(space)
                        break

                if breaking:
                    break

def picma_main(width, height):
    spaces = set((x,y) for x in range(width) for y in range(height))

    solver = Solver(spaces)

    for y in range(height):
        for x in range(width):
            char = sys.stdin.read(1)
            while char not in '-0123456789':
                char = sys.stdin.read(1)

            if char.isdigit():
                info_count = int(char)
                info_spaces = frozenset((xs,ys) for xs in range(x-1, x+2) for ys in range(y-1, y+2)).intersection(spaces)
                solver.add_information(Information(info_spaces, info_count))

    solver.solve()

    for y in range(height):
        for x in range(width):
            sys.stdout.write(str(solver.solved_spaces.get((x, y), '-')))
        sys.stdout.write('\n')

    for i in solver.information:
        print i

if __name__ == '__main__':
    picma_main(int(sys.argv[1]), int(sys.argv[2]))

