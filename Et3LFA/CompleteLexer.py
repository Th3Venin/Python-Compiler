import et1 as et1
import et2 as et2


def string_to_list(string):
    list1 = []
    list1[:0] = string
    return list1


def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1


class Parser:
    def __init__(self):
        self.input_regex = []
        self.pairs = []
        self.dfa_list = []
        self.nfa_list = []
        self.operations = ["+", "*", "|"]
        self.output = []

    class Pair(object):
        def __init__(self, token, regex):
            self.token = token
            self.regex = regex

    def read_in_file(self, in_file_name):
        f = open(in_file_name, "r")
        sequence = ""
        for line in f:
            sequence = sequence + line
        self.input_regex = string_to_list(sequence)

    def read_lex_file(self, lex_file_name):
        f = open(lex_file_name, "r")
        for line in f:
            line = line[:-2]
            components = line.split(' ', 1)

            new_pair = self.Pair(components[0], components[1])
            self.pairs.append(new_pair)

    # extraction only contains nfas and operations
    def parse_sequence(self, extraction: list):
        stack = [extraction[0]]
        t = et2.Transform()

        for i in range(1, len(extraction)):
            if extraction[i] not in self.operations:
                if extraction[i - 1] in self.operations:
                    continue
                stack.append(t.concat_nfas(stack[-1], extraction[i]))
                stack.pop(0)
            else:
                if extraction[i] == "|":
                    stack.append(t.union_nfas(stack[-1], extraction[i + 1]))
                    stack.pop(0)
                if extraction[i] == "*":
                    stack.append(t.kleene_nfa(stack[-1]))
                    stack.pop(0)
                if extraction[i] == "+":
                    stack.append(t.plus_nfa(stack[-1]))
                    stack.pop(0)

        return stack[0]

    def parse_regex(self, regex: str):
        main_stack = []
        t = et2.Transform()
        alphabet = set()

        for i in range(0, len(regex)):
            if regex[i] not in self.operations:
                if regex[i] == "(":
                    main_stack.append(regex[i])

                if (regex[i].isalpha() or regex[i].isdigit()) and regex[i - 1] != "\\":
                    alphabet.add(regex[i])
                    transition = et2.Transition(0, regex[i], 1)
                    new_nfa = et2.NFA()
                    new_nfa.transitions.append(transition)
                    new_nfa.initial_state = 0
                    new_nfa.final_state = 1
                    main_stack.append(new_nfa)

                if regex[i] == ")":
                    extraction = [main_stack[-1]]
                    main_stack.pop()
                    while "(" not in extraction:
                        extraction.insert(0, main_stack[-1])
                        main_stack.pop()
                    extraction.pop(0)
                    main_stack.append(self.parse_sequence(extraction))

                if regex[i] == ' ':
                    alphabet.add(' ')
                    transition = et2.Transition(0, ' ', 1)
                    new_nfa = et2.NFA()
                    new_nfa.transitions.append(transition)
                    new_nfa.initial_state = 0
                    new_nfa.final_state = 1
                    main_stack.append(new_nfa)

                if regex[i - 1] == "\\":
                    string = regex[i - 1] + regex[i]
                    alphabet.add('\n')
                    transition = et2.Transition(0, '\n', 1)
                    new_nfa = et2.NFA()
                    new_nfa.transitions.append(transition)
                    new_nfa.initial_state = 0
                    new_nfa.final_state = 1
                    main_stack.append(new_nfa)

            else:
                if regex[i] == "*":
                    main_stack.append(t.kleene_nfa(main_stack[-1]))
                    main_stack.pop(len(main_stack) - 2)
                if regex[i] == "+":
                    main_stack.append(t.plus_nfa(main_stack[-1]))
                    main_stack.pop(len(main_stack) - 2)
                if regex[i] == "|":
                    main_stack.append(regex[i])

        self.nfa_list.append(self.parse_sequence(main_stack))
        self.nfa_list[-1].alphabet = sorted(alphabet)

    def get_nfas(self, lex_file):
        self.read_lex_file(lex_file)

        for _pair in self.pairs:
            self.parse_regex(_pair.regex)

    def get_dfas(self):
        i = 0
        for _nfa in self.nfa_list:
            t = et2.Transform()
            t.nfa = _nfa
            t.alphabet = _nfa.alphabet
            t.build_dfa()

            new_dfa = et2.DFA()
            new_dfa.token = self.pairs[i].token
            new_dfa.transitions = t.transitions
            new_dfa.initial_state = "0"
            new_dfa.final_states = t.final_states

            self.dfa_list.append(new_dfa)
            i += 1

    def runlexer(self):
        regex_copy = self.input_regex.copy()
        t = et1.Lexer()

        while len(regex_copy) > 0:
            prefix_list = []
            max_len_prefix = ""
            dfa_index = 0

            for dfa in self.dfa_list:
                regex_copy = self.input_regex.copy()
                prefix_list.append(t.run_dfa(dfa, regex_copy))

            index = 0
            for prefix in prefix_list:
                if len(prefix) > len(max_len_prefix):
                    max_len_prefix = prefix
                    dfa_index = index
                index += 1

            self.input_regex = self.input_regex[len(max_len_prefix):]
            regex_copy = self.input_regex.copy()
            if listToString(max_len_prefix) == '\n':
                self.output.append(self.dfa_list[dfa_index].token + " " + "\\" + 'n')
            else:
                self.output.append(self.dfa_list[dfa_index].token + " " + listToString(max_len_prefix))

        for prefix in self.output:
            print(prefix)
            
def runparser(in_file, out_file):
	print()

def runcompletelexer(lex_file, in_file, out_file):
	p = Parser()
	p.read_in_file(in_file)
	p.get_nfas(lex_file)
	p.get_dfas()
	p.runlexer()

	f = open(out_file, 'w')
	for i in range(0, len(p.output) - 1):
		f.write(p.output[i])
		f.write("\n")
	f.write(p.output[-1])
