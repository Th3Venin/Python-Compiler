import sys


def set_to_string(in_set):
    string = ""
    for elem in in_set:
        string += str(elem)
    return string


def convert(string):
    list1 = []
    list1[:0] = string
    return list1


def sublist(list1, list2):
    for l in list2:
        list1.sort()
        l.sort()
        if list1 == l:
            return True

    return False


def listToString(s):
    str1 = ""

    for ele in s:
        str1 += str(ele)

    return str1


def duplicate_state(transitions: list, value):
    for tran in transitions:
        if set_to_string(tran.next_state) == set_to_string(value):
            return True
    return False


def duplicate_transition(transition_list, transition):
    for tran in transition_list:
        if tran.current_state == transition.current_state and tran.next_state == transition.next_state \
                and tran.value == transition.value:
            return True
    return False


def diff(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


class Transition:

    def __init__(self, current_state, value, next_state):
        self.current_state = current_state
        self.value = value
        self.next_state = next_state


class Branch:

    def __init__(self, character: str, state_set: list):
        self.character = character
        self.set = state_set


class NFA:

    def __init__(self):
        self.alphabet = []
        self.transitions = []
        self.initial_state = int
        self.final_state = int

    def print_nfa(self):
        print(self.initial_state)
        print(self.final_state)
        for n in self.transitions:
            print(n.current_state, n.value, n.next_state)


class DFA:

    def __init__(self):
        self.transitions = []
        self.initial_state = int
        self.final_states = []
        self.token = ""

    def print_dfa(self):
        print(self.token)
        print(self.initial_state)
        print(self.final_states)
        for n in self.transitions:
            print(n.current_state, n.value, n.next_state)


class Transform:

    def __init__(self):
        self.input_prenex = []
        self.operations = ["UNION", "CONCAT", "STAR", "PLUS"]
        self.regex = ""
        self.nfa = NFA()
        self.alphabet = []
        self.final_states = []
        self.transitions = []
        self.transition_number = int

    def read_in_file(self, in_file_name):
        f = open(in_file_name, "r")
        sequence = f.read()
        self.input_prenex = sequence.split()
        self.input_prenex.reverse()

    def write_to_file(self, out_file_name):
        f = open(out_file_name, 'w')

        alphabet = ""
        initial_state = "0"
        final_states = ""

        for char in self.alphabet:
            alphabet += char
        f.write(alphabet)
        f.write("\n")

        f.write(str(self.transition_number))
        f.write("\n")
        f.write(initial_state)
        f.write("\n")

        for state in self.final_states:
            final_states += str(state) + " "
        final_states = final_states[:-1]
        f.write(final_states)

        for trans in self.transitions:
            transition = ""
            transition += str(trans.current_state) + ",'" + trans.value + "'," + str(trans.next_state)
            f.write("\n")
            f.write(transition)

    def parse_prenex(self):
        stack = []

        for elem in self.input_prenex:
            if elem not in self.operations:
                stack.insert(0, elem)
            else:
                if elem == 'UNION':
                    collector = "UNION("

                    for i in range(0, 2):
                        collector += stack[0] + ","
                        stack.pop(0)

                    collector = collector[:-1] + ")"
                    stack.insert(0, collector)

                if elem == "CONCAT":
                    collector = "CONCAT("

                    for i in range(0, 2):
                        collector += stack[0] + ","
                        stack.pop(0)

                    collector = collector[:-1] + ")"
                    stack.insert(0, collector)

                if elem == "STAR":
                    collector = "STAR("

                    collector += stack[0] + ")"
                    stack.pop(0)

                    stack.insert(0, collector)

                if elem == "PLUS":
                    collector = "PLUS("

                    collector += stack[0] + ")"
                    stack.pop(0)

                    stack.insert(0, collector)

    @staticmethod
    def concat_nfas(n1: NFA, n2: NFA):
        n = NFA()
        n.transitions.extend(n1.transitions)
        inter = Transition(n1.transitions[-1].next_state, "eps", n1.transitions[-1].next_state + 1)
        n.transitions.append(inter)

        for transition in n2.transitions:
            transition.current_state += n.transitions[-1].next_state
            transition.next_state += n.transitions[-1].next_state

        n.transitions.extend(n2.transitions)
        n.initial_state = n.transitions[0].current_state
        n.final_state = n.transitions[-1].next_state
        return n

    @staticmethod
    def kleene_nfa(n1: NFA):
        n = NFA()

        for trans in n1.transitions:
            trans.current_state += 1
            trans.next_state += 1

        inter = Transition(n1.transitions[-1].next_state, "eps", n1.transitions[0].current_state)
        n.transitions.insert(0, inter)

        pre = Transition(0, "eps", n1.transitions[0].current_state)
        after = Transition(n1.transitions[-1].next_state, "eps", n1.transitions[-1].next_state + 1)

        n.transitions.insert(0, pre)
        n.transitions.extend(n1.transitions)
        n.transitions.append(after)

        exter = Transition(n.transitions[0].current_state, "eps", n.transitions[-1].next_state)
        n.initial_state = pre.current_state
        n.final_state = after.next_state
        n.transitions.append(exter)

        return n

    @staticmethod
    def plus_nfa(n1: NFA):
        n = NFA()

        for trans in n1.transitions:
            trans.current_state += 1
            trans.next_state += 1

        inter = Transition(n1.transitions[-1].next_state, "eps", n1.transitions[0].current_state)
        n.transitions.insert(0, inter)

        pre = Transition(0, "eps", n1.transitions[0].current_state)
        after = Transition(n1.transitions[-1].next_state, "eps", n1.transitions[-1].next_state + 1)

        n.transitions.insert(0, pre)
        n.transitions.extend(n1.transitions)
        n.transitions.append(after)
        n.initial_state = 0
        n.final_state = after.next_state

        return n

    @staticmethod
    def union_nfas(n1: NFA, n2: NFA):
        n = NFA()

        for transition in n1.transitions:
            transition.current_state += 1
            transition.next_state += 1

        for transition in n2.transitions:
            transition.current_state += len(n1.transitions) + 2
            transition.next_state += len(n1.transitions) + 2

        n.transitions.extend(n1.transitions)
        n.transitions.extend(n2.transitions)

        pre1 = Transition(0, "eps", n1.transitions[0].current_state)
        pre2 = Transition(0, "eps", n2.transitions[0].current_state)
        after1 = Transition(n1.transitions[-1].next_state, "eps", n2.transitions[-1].next_state + 1)
        after2 = Transition(n2.transitions[-1].next_state, "eps", n2.transitions[-1].next_state + 1)

        n.transitions.insert(0, pre1)
        n.transitions.insert(0, pre2)
        n.transitions.append(after1)
        n.transitions.append(after2)
        n.initial_state = 0
        n.final_state = after2.next_state

        return n

    def build_nfa(self):
        stack = []
        alphabet = set()

        for elem in self.input_prenex:
            if elem not in self.operations:
                alphabet.add(elem)
                transition = Transition(0, elem, 1)
                nfa = NFA()
                nfa.transitions.append(transition)
                nfa.initial_state = 0
                nfa.final_state = 1
                stack.insert(0, nfa)

            else:
                if elem == 'CONCAT':
                    result = self.concat_nfas(stack[0], stack[1])
                    for i in range(0, 2):
                        stack.pop(0)
                    stack.insert(0, result)

                if elem == "STAR":
                    result = self.kleene_nfa(stack[0])
                    stack.pop(0)
                    stack.insert(0, result)

                if elem == "PLUS":
                    result = self.plus_nfa(stack[0])
                    stack.pop(0)
                    stack.insert(0, result)

                if elem == "UNION":
                    result = self.union_nfas(stack[0], stack[1])
                    for i in range(0, 2):
                        stack.pop(0)
                    stack.insert(0, result)

        stack[0].transitions.sort(key=lambda x: (x.current_state, x.next_state))
        self.nfa = stack[0]
        self.alphabet = sorted(alphabet)
        self.nfa.alphabet = self.alphabet

    def find_first_set(self):
        first_set = {self.nfa.initial_state, self.nfa.final_state}

        for trans in self.nfa.transitions:
            if trans.current_state in first_set and trans.value == "eps":
                first_set.add(trans.next_state)

        return sorted(first_set)

    def compute_character_branch(self, character: str, state: int):
        found_states = []
        epsilon_states = []

        for trans in self.nfa.transitions:
            if trans.current_state == state and trans.value == character:
                found_states.append(trans.next_state)

        searched_states = found_states.copy()
        while len(searched_states) > 0:
            found_eps = []
            for state in searched_states:
                for trans in self.nfa.transitions:
                    if state == trans.current_state and trans.value == "eps":
                        found_eps.append(trans.next_state)
            searched_states = found_eps.copy()
            epsilon_states.extend(found_eps)

        found_states.extend(epsilon_states)
        found_states.sort()

        return found_states

    def build_dfa(self):
        start_set = self.find_first_set()
        in_process = [start_set]
        processed = []
        dfa_transitions = []
        actual_transitions = []
        indexes = []

        while len(in_process) > 0:
            in_process_next = []
            for in_process_set in in_process:
                found_branches = []
                for character in self.alphabet:
                    cumulative_set = set()
                    for state in in_process_set:
                        if len(self.compute_character_branch(character, state)) > 0:
                            cumulative_set.update(self.compute_character_branch(character, state))
                    b = Branch(character, sorted(cumulative_set))
                    # print(in_process_set, b.character, b.set)
                    if len(b.set) > 0:
                        found_branches.append(b)

                for branch in found_branches:
                    # if duplicate_state(dfa_transitions, branch.set) is False:
                    new_t = Transition(listToString(in_process_set), branch.character, listToString(branch.set))
                    if duplicate_transition(dfa_transitions, new_t) is False:
                        dfa_transitions.append(new_t)

                for subl in in_process:
                    if sublist(subl, processed) is False:
                        processed.append(subl)
                for branch in found_branches:
                    if sublist(branch.set, in_process) is False and sublist(branch.set, processed) is False:
                        in_process_next.append(branch.set)
            in_process = in_process_next

        # print(processed)
        # for trans in dfa_transitions:
            # print(trans.current_state, trans.value, trans.next_state)

        for sett in processed:
            indexes.append(set_to_string(sett))

        for trans in dfa_transitions:
            tr = Transition(indexes.index(trans.current_state), trans.value, indexes.index(trans.next_state))
            actual_transitions.append(tr)

        for i in range(0, len(processed)):
            nr_of_this_index = 0
            characters = []
            for trans in actual_transitions:
                if trans.current_state == i:
                    characters.append(trans.value)
                    nr_of_this_index += 1
            if nr_of_this_index == 0:
                for j in range(0, len(self.alphabet)):
                    tr = Transition(i, self.alphabet[j], len(processed))
                    actual_transitions.append(tr)
            elif 0 < nr_of_this_index < len(processed) - 1:
                missing = diff(self.alphabet, characters)
                for j in range(0, len(missing)):
                    tr = Transition(i, missing[j], len(processed))
                    actual_transitions.append(tr)

        for i in range(0, len(self.alphabet)):
            tr = Transition(len(processed), self.alphabet[i], len(processed))
            actual_transitions.append(tr)

        for i in range(1, len(processed)):
            for state in processed[i]:
                if state == self.nfa.final_state:
                    self.final_states.append(i)
                    # print(i)

        actual_transitions.sort(key=lambda x: (x.current_state, x.value))
        self.transitions = actual_transitions
        self.transition_number = len(processed) + 1

        # for trans in actual_transitions:
            # print(trans.current_state, trans.value, trans.next_state)


if __name__ == '__main__':
    t = Transform()
    t.read_in_file(sys.argv[1])
    t.build_nfa()
    print(t.alphabet)
    t.nfa.print_nfa()
    t.build_dfa()
    t.write_to_file(sys.argv[2])
