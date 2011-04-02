
import collections
import sys

class exception(Exception):
    pass

class UnsolveableException(exception):
    pass

Information = collections.namedtuple('Information', ('spaces', 'count'))

def choose(n, k):
    # by Andrew Dalke.
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in xrange(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

class Solver(object):
    def __init__(self, spaces):
        self.spaces = frozenset(spaces)
        self.solved_spaces = dict()
        self.information = set()
        self.informations_for_space = collections.defaultdict(set)
        self.clusters_checked = set()
        self.cluster_probabilities = dict()

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

    def add_known_value(self, space, value):
        self.solved_spaces[space] = value
        self.spaces_with_new_information.add(space)

    def copy(self):
        result = Solver(self.spaces)
        result.solved_spaces = self.solved_spaces.copy()
        result.information = self.information.copy()
        for key, value in self.informations_for_space.iteritems():
            result.informations_for_space[key] = value.copy()
        result.spaces_with_new_information = self.spaces_with_new_information.copy()
        result.clusters_checked = self.clusters_checked.copy()
        result.cluster_probabilities = self.cluster_probabilities.copy()
        return result

    def get_clusters(self):
        informations_unassigned = set(self.information)
        result = set()

        while informations_unassigned:
            information = informations_unassigned.pop()
            cluster = set((information,))
            unchecked_spaces_in_cluster = set(information.spaces)

            while unchecked_spaces_in_cluster:
                space = unchecked_spaces_in_cluster.pop()
                for information in self.informations_for_space[space]:
                    if information in informations_unassigned:
                        informations_unassigned.remove(information)
                        cluster.add(information)
                        unchecked_spaces_in_cluster.update(information.spaces)

            result.add(frozenset(cluster))

        return result

    @staticmethod
    def get_solutions(base_solver, space, value, result):
        solver = base_solver.copy()

        solver.solved_spaces[space] = value
        solver.spaces_with_new_information.add(space)

        try:
            solver.solve(np=False)
        except UnsolveableException:
            return 0

        if len(solver.solved_spaces) != len(solver.spaces):
            if len(solver.information) == 1:
                for information in solver.information:
                    break
                combinations = choose(len(information.spaces), information.count)
                p = combinations * information.count / len(information.spaces)
                for space in information.spaces:
                    result[space] += p
                for space, value in solver.solved_spaces.iteritems():
                    if value:
                        result[space] += combinations
                return combinations
            else:
                # Find a space in the smallest information, so we can quickly reduce them to one
                min_information = None
                for information in solver.information:
                    if min_information is None or len(information.spaces) < len(min_information.spaces):
                        min_information = information
                for space in min_information.spaces:
                    if space not in solver.solved_spaces:
                        break
                else:
                    raise exception("This shouldn't happen")

                return Solver.get_solutions(solver, space, 0, result) + Solver.get_solutions(solver, space, 1, result)
        else:
            for space, value in solver.solved_spaces.iteritems():
                result[space] += value
            return 1

    def get_probabilities(self):
        self.solve()
        clusters = self.get_clusters()
        new_cluster_probabilities = {}
        result = {}
        denominator = 1

        for cluster in clusters:
            if cluster in self.cluster_probabilities:
                cluster_probabilities = self.cluster_probabilities[cluster]
            elif len(cluster) == 1:
                cluster_possibilities = {}
                for information in cluster:
                    break

                total = choose(len(information.spaces), information.count)
                p = total * information.count / len(information.spaces)

                for space in information.spaces:
                    cluster_possibilities[space] = p

                cluster_probabilities = cluster_possibilities, total
            else:
                spaces = set()
                for information in cluster:
                    spaces.update(information.spaces)

                solver = Solver(spaces)

                for information in cluster:
                    solver.add_information(information)

                possibilities = {}
                total = 0
                for space in spaces:
                    possibilities[space] = 0

                total += Solver.get_solutions(solver, space, 0, possibilities)
                total += Solver.get_solutions(solver, space, 1, possibilities)

                cluster_probabilities = possibilities, total

            new_cluster_probabilities[cluster] = cluster_probabilities

            possibilities, total = cluster_probabilities

            for space in result:
                result[space] *= total

            for space in possibilities:
                result[space] = possibilities[space] * denominator

            denominator *= total

        self.cluster_probabilities = new_cluster_probabilities
        return result, denominator

    @staticmethod
    def check_state(base_solver, space, value, states_to_validate):
        solver = base_solver.copy()

        solver.solved_spaces[space] = value
        solver.spaces_with_new_information.add(space)

        try:
            solver.solve(np=False)
        except UnsolveableException:
            return False

        if len(solver.solved_spaces) != len(solver.spaces):
            for space in solver.spaces:
                if space not in solver.solved_spaces:
                    break
            else:
                raise exception("This shouldn't happen")

            if (space, 1) in states_to_validate:
                first_value_to_check = 1
            else:
                first_value_to_check = 0

            res = Solver.check_state(solver, space, first_value_to_check, states_to_validate)

            if not res:
                res = Solver.check_state(solver, space, first_value_to_check ^ 1, states_to_validate)

            return res
        else:
            return solver.solved_spaces

    def solve_cluster(self, cluster):
        if len(cluster) == 1:
            return False

        spaces = set()
        for information in cluster:
            spaces.update(information.spaces)

        states_to_validate = set()
        states_to_validate.update((x, 0) for x in spaces)
        states_to_validate.update((x, 1) for x in spaces)

        base_solver = Solver(spaces)
        for information in cluster:
            base_solver.add_information(information)

        while states_to_validate:
            space, value = states_to_validate.pop()

            res = Solver.check_state(base_solver, space, value, states_to_validate)

            if res:
                states_validated = set(res.iteritems())
                states_to_validate.difference_update(states_validated)
            else:
                self.solved_spaces[space] = value ^ 1
                self.spaces_with_new_information.add(space)
                return True

        return False

    def solve_np(self):
        clusters = self.get_clusters()

        for cluster in clusters:
            if cluster in self.clusters_checked:
                continue

            self.clusters_checked.add(cluster)

            if self.solve_cluster(cluster):
                return True
        else:
            self.clusters_checked = clusters
            return False

    def solve(self, np=True):
        while True:
            if self.spaces_with_new_information:
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
                        elif new_information.count != 0:
                            raise UnsolveableException()

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
            elif not np or not self.solve_np():
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

def mines_main(width, height, total):
    spaces = set((x,y) for x in range(width) for y in range(height))

    solver = Solver(spaces)

    for y in range(height):
        for x in range(width):
            char = sys.stdin.read(1)
            while char not in '-0123456789m':
                char = sys.stdin.read(1)

            if char.isdigit():
                info_count = int(char)
                info_spaces = frozenset((xs,ys) for xs in range(x-1, x+2) for ys in range(y-1, y+2)).intersection(spaces)
                solver.add_information(Information(info_spaces, info_count))
                solver.add_known_value((x, y), 0)
            elif char == 'm':
                solver.add_known_value((x, y), 1)

    solver.add_information(Information(frozenset(spaces), total))

    solver.solve()

    sys.stdout.write('\n')

    for y in range(height):
        for x in range(width):
            sys.stdout.write(str(solver.solved_spaces.get((x, y), '-')))
        sys.stdout.write('\n')

    for i in solver.information:
        print i

    probabilities, total = solver.get_probabilities()

    probabilities = [(probability, space) for (space, probability) in probabilities.iteritems()]

    probabilities.sort()

    print 'total possible arrangements:', total

    total = float(total)

    for probability, space in probabilities:
        print space, probability / total

if __name__ == '__main__':
    if sys.argv[1] == 'picma':
        picma_main(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == 'mines':
        mines_main(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

