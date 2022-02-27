import ast as ast
import re


def get_equals(string):
    count = 0
    for c in string:
        if c == "=":
            count += 1
    return count


def get_height(string):
    count = 0
    for c in string:
        if c == " ":
            count += 1
        else:
            return count / 4


def parse_assignment(line, offset):
    container = line.split()
    left_expr = ast.Expr(get_height(line) + 2 + offset, "v", container[0])

    if len(container) > 3:
        if container[2].isdigit() or container[2].lstrip('-').isdigit():
            expr1 = ast.Expr(get_height(line) + 3 + offset, "i", container[2])
        else:
            expr1 = ast.Expr(get_height(line) + 3 + offset, "v", container[2])
        if container[4].isdigit() or container[4].lstrip('-').isdigit():
            expr2 = ast.Expr(get_height(line) + 3 + offset, "i", container[4])
        else:
            expr2 = ast.Expr(get_height(line) + 3 + offset, "v", container[4])
        right_expr = ast.Expr(get_height(line) + 2 + offset, container[3], expr1, expr2)
    else:
        if container[2].isdigit() or container[2].lstrip('-').isdigit():
            right_expr = ast.Expr(get_height(line) + 2 + offset, "i", container[2])
        else:
            right_expr = ast.Expr(get_height(line) + 2 + offset, "v", container[2])
    return ast.Assign(get_height(line) + 1 + offset, left_expr, right_expr)


def parse_condition(line):
    condition = re.search('\\((.*)\\)', line).group(1)
    container = condition.split()

    if len(container) > 3:
        if container[0].isdigit() or container[0].lstrip('-').isdigit():
            expr1 = ast.Expr(get_height(line) + 4, "i", container[0])
        else:
            expr1 = ast.Expr(get_height(line) + 4, "v", container[0])
        if container[2].isdigit() or container[2].lstrip('-').isdigit():
            expr2 = ast.Expr(get_height(line) + 4, "i", container[2])
        else:
            expr2 = ast.Expr(get_height(line) + 4, "v", container[2])
        left_expr = ast.Expr(get_height(line) + 3, container[1], expr1, expr2)
        if container[4].isdigit() or container[4].lstrip('-').isdigit():
            right_expr = ast.Expr(get_height(line) + 3, "i", container[4])
        else:
            right_expr = ast.Expr(get_height(line) + 3, "v", container[4])
        return ast.Expr(get_height(line) + 2, container[3], left_expr, right_expr)

    else:
        if container[0].isdigit():
            left_expr = ast.Expr(get_height(line) + 3, "i", container[0])
        else:
            left_expr = ast.Expr(get_height(line) + 3, "v", container[0])
        if container[2].isdigit():
            right_expr = ast.Expr(get_height(line) + 3, "i", container[2])
        else:
            right_expr = ast.Expr(get_height(line) + 3, "v", container[2])
        return ast.Expr(get_height(line) + 2, container[1], left_expr, right_expr)


class IParser:
    def __init__(self):
        self.program = []
        self.stack = []
        self.storage = {}

    def read_input_file(self, file_name):
        f = open(file_name, "r")
        for line in f:
            self.program.append(line)

    def parse_program(self):
        main_stack = []
        index = 0

        for line in reversed(self.program):
            if "end" in line:
                main_stack.append("end")
            if get_equals(line) == 1:
                if any("do" in _line for _line in self.program[:len(self.program) - index - 2]) \
                        and any("od" in _line for _line in self.program[len(self.program) - index - 2:]):
                    main_stack.append(parse_assignment(line, 1))
                else:
                    main_stack.append(parse_assignment(line, 0))
            if "begin" in line:
                extraction = main_stack.pop()
                temp_list = []
                while extraction != "end":
                    temp_list.append(extraction)
                    extraction = main_stack.pop()
                if index != len(self.program) - 1 and "while" in self.program[len(self.program) - index - 2] \
                        or "else" in self.program[len(self.program) - index - 2]:
                    instr_list = ast.InstructionList(get_height(line) + 1, temp_list)
                else:
                    instr_list = ast.InstructionList(get_height(line), temp_list)
                main_stack.append(instr_list)
            if "if" in line:
                if_block = ast.If(get_height(line) + 1, parse_condition(line), main_stack[-1], main_stack[-2])
                main_stack.pop()
                main_stack.pop()
                main_stack.append(if_block)
            if "while" in line:
                while_block = ast.While(get_height(line) + 1, parse_condition(line), main_stack[-1])
                main_stack.pop()
                main_stack.append(while_block)
            index += 1

        print(main_stack[0].__str__())
        self.stack.append(main_stack[0])

    def get_value(self, element: ast.Expr):
        if element.type == "i":
            return int(element.left)
        if element.type == "v":
            return self.storage[element.left]

    def compute_expression(self, expression: ast.Expr):
        if expression.right is None:
            if expression.type == "i":
                return expression.left
            else:
                return self.storage[expression.left]
        else:
            if expression.type == "+":
                return self.get_value(expression.left) + self.get_value(expression.right)
            if expression.type == "-":
                return self.get_value(expression.left) - self.get_value(expression.right)
            if expression.type == "*":
                return self.get_value(expression.left) * self.get_value(expression.right)

    def compute_condition(self, expression: ast.Expr):
        if expression.type == "==":
            if int(self.compute_expression(expression.left)) == int(self.compute_expression(expression.right)):
                return True
            else:
                return False
        if expression.type == ">":
            if int(self.compute_expression(expression.left)) > int(self.compute_expression(expression.right)):
                return True
            else:
                return False

    def compute_assignment(self, assignment: ast.Assign):
        self.storage[assignment.variable.left] = int(self.compute_expression(assignment.expr))

    def program_interpreter(self, node: ast.Node):
        if type(node) == ast.InstructionList:
            for instr in node.list:
                self.program_interpreter(instr)

        if type(node) == ast.Assign:
            self.compute_assignment(node)

        if type(node) == ast.If:
            if self.compute_condition(node.expr) is True:
                self.program_interpreter(node.then_branch)
            else:
                self.program_interpreter(node.else_branch)

        if type(node) == ast.While:
            if self.compute_condition(node.expr) is True:
                self.program_interpreter(node.prog)
                self.program_interpreter(node)

def runparser(in_file, out_file):
	p = IParser()
	p.read_input_file(in_file)
	p.parse_program()

	f = open(out_file, 'w')
	f.write(p.stack[0].__str__())
	
	for elem in p.stack:
		p.program_interpreter(elem)
	print(p.storage)
        
def runcompletelexer(lex_file, in_file, out_file):
	print()
