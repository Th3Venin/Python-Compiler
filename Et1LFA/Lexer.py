def split(string):
    return [char for char in string]


def convert(string):
    list1 = []
    list1[:0] = string
    return list1


def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1


def run_dfa(dfa, regex):
        current_state = 0
        longest_prefix = []
        processed_prefix = []

        while len(regex) > 0:
            not_found = True
            current_char = regex[0]

            for i in range(len(dfa.transitions)):
                if int(dfa.transitions[i].current_state) == int(current_state) and \
                        dfa.transitions[i].value == current_char:
                    not_found = False
                    regex.pop(0)
                    current_state = dfa.transitions[i].next_state
                    if int(current_state) in dfa.final_states:
                        processed_prefix.append(current_char)
                        longest_prefix = processed_prefix.copy()
                    else:
                        processed_prefix.append(current_char)
                    break

            if not_found:
                # print("DFA with token " + dfa.token + " no longer accepts. "
                # "Longest prefix found is: " + listToString(longest_prefix))
                return longest_prefix

        # print("DFA with token " + dfa.token + " accepted! Longest prefix found is: " + listToString(longest_prefix))
        return longest_prefix


class Lexer:
    def __init__(self):
        self.dfa_number = 0
        self.dfa_list = []
        self.input = []
        self.output = []

    class DFA(object):
        def __init__(self, alphabet, token, initial_state, transitions, final_states):
            self.alphabet = alphabet
            self.token = token
            self.init_state = initial_state
            self.transitions = transitions
            self.final_states = final_states

    class Transition(object):
        def __init__(self, current_state, value, next_state):
            self.current_state = current_state
            self.value = value
            self.next_state = next_state

    def read_in_file(self, in_file_name):
        f = open(in_file_name, "r")
        sequence = ""
        for line in f:
            sequence = sequence + line
        self.input = convert(sequence)

    def write_to_file(self, out_file_name):
        f = open(out_file_name, "w")
        for i in range(0, len(self.output) - 1):
            f.write(self.output[i])
            f.write('\n')
        f.write(self.output[-1])

    def read_lex_file(self, lex_file_name):
        f = open(lex_file_name, "r")
        file_lines = f.readlines()

        dfa_list = []
        dfa_lines = []
        for i in range(len(file_lines)):
            if file_lines[i] == '\n':
                dfa_list.append(dfa_lines)
                dfa_lines = []
            elif i == len(file_lines) - 1:
                dfa_lines.append(file_lines[i])
                dfa_list.append(dfa_lines)
                dfa_lines = []
            else:
                dfa_lines.append(file_lines[i])

        for dfa_params in dfa_list:
            if dfa_params[0][:-1] == "\\n":
                alphabet = dfa_params[0][:-1]
            else:
                alphabet = split(dfa_params[0][:-1])
            token = dfa_params[1][:-1]
            initial_state = dfa_params[2][:-1]
            final_states = convert(dfa_params[-1].split(' '))
            if '\n' in final_states:
                final_states.remove('\n')
            final_states = list(map(int, final_states))

            transitions = dfa_params[3:-1]
            transitions_list = []
            for i in range(len(transitions)):
                transitions[i] = transitions[i][:-1]
                current_state = transitions[i].split(',')[0]
                value = transitions[i].split(',')[1].replace("\'", "")
                if value == "\\n":
                    value = '\n'
                next_state = transitions[i].split(',')[2]
                transitions_list.append(Lexer.Transition(current_state, value, next_state))

            self.dfa_list.append(Lexer.DFA(alphabet, token, initial_state, transitions_list, final_states))


def runlexer(lex_file, in_file, out_file):
    lexer = Lexer()

    lexer.read_lex_file(lex_file)
    lexer.read_in_file(in_file)
    regex_copy = lexer.input.copy()

    while len(regex_copy) > 0:
        prefix_list = []
        max_len_prefix = ""
        dfa_index = 0

        for dfa in lexer.dfa_list:
            regex_copy = lexer.input.copy()
            prefix_list.append(run_dfa(dfa, regex_copy))

        index = 0
        for prefix in prefix_list:
            if len(prefix) > len(max_len_prefix):
                max_len_prefix = prefix
                dfa_index = index
            index += 1

        lexer.input = lexer.input[len(max_len_prefix):]
        regex_copy = lexer.input.copy()
        if listToString(max_len_prefix) == '\n':
            lexer.output.append(lexer.dfa_list[dfa_index].token + " " + "\\" + 'n')
        else:
            lexer.output.append(lexer.dfa_list[dfa_index].token + " " + listToString(max_len_prefix))

    lexer.write_to_file(out_file)
