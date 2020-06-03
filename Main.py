from typing import List


def read_file(file: str) -> str:
    with open(file, 'r') as file:
        return file.read()


class Scope:
    name: str
    variables: List[str]

    def __init__(self, name: str):
        self.name = name
        self.variables = []


def debug(text: str):
    if True:
        print(text)


def detect_declarations(tokens: str):
    types = ["int", "boolean", "byte", "char", "short", "int", "long", "float", "double"]
    separators = [';', ' ', '\n', '\t']
    scopes: List[Scope] = []
    index = 0

    def next_occurrence(character: str, start_index: int) -> int:
        counter = 1
        while start_index+counter < len(tokens):
            if tokens[start_index + counter] == character:
                return start_index + counter
            else:
                counter += 1
        return -1

    def previous_occurrence_from_list(characters: List[str], start_index: int) -> int:
        counter = -1
        while start_index+counter >= 0:
            if tokens[start_index+counter] in characters:
                return start_index+counter
            else:
                counter -= 1
        return -1

    def previous_occurrence(character: str, start_index: int) -> int:
        counter = -1
        while start_index+counter >= 0:
            if tokens[start_index+counter] == character:
                return start_index+counter
            else:
                counter -= 1
        return -1

    def scope_declaration():
        return current == "{"

    def scope_end():
        return current == "}"

    def variable_declaration():
        if index == 56:
            print('g')

        for variable_type in types:  # try [';', ' ', '\n', '\t'] + '('
            if tokens[index:index+len(variable_type)] == variable_type and tokens[index-1] in separators:
                return True

    def get_variable_declaration():
        end = next_occurrence(";", index)
        declaration = tokens[index:end]
        return declaration

    def get_arguments_from_scope_name(scope_name: str) -> List[str]:
        lp = scope_name.index('(')
        rp = scope_name.index(')')
        arguments_with_types = scope_name[lp + 1:rp].split(',')
        arguments = []
        for arg in arguments_with_types:
            arguments.append(arg.split()[1])
        return arguments

    def get_scope_declaration():
        right_parenthesis = previous_occurrence(')', index)
        left_parenthesis = previous_occurrence('(', index)
        space = previous_occurrence_from_list(separators, index-1)
        previous_space = previous_occurrence_from_list(separators, left_parenthesis-1)

        a = tokens[:index]

        if space > right_parenthesis:  # class
            scope_name = tokens[space+1:index]
            return Scope(scope_name)
        elif previous_space < left_parenthesis:
            scope_name = tokens[previous_space+1:index]
            if scope_name.split()[0] not in ["if", "while"]:  # function
                args = get_arguments_from_scope_name(scope_name)
                scope = Scope(scope_name)
                scope.variables.extend(args)
                return scope
            else:  # if or while
                return Scope(scope_name)
        else:
            return Scope("ERROR")

    def function_call():
        if tokens[index] == ')' and tokens[index+1] == ';':
            return True

    def variable_use():
        left_separators = [';', ' ', '(']
        right_separators = [';', ' ', ')']
        if tokens[index - 1] in left_separators and tokens[index + 1] in right_separators and current.isalpha():
            return True

    def get_arguments():
        left_parenthesis = previous_occurrence('(', index)
        space = previous_occurrence_from_list(separators, left_parenthesis)
        args = tokens[left_parenthesis+1:index]
        function_name = tokens[space+1:left_parenthesis]
        debug("Calling " + function_name)
        return args

    def is_in_scope(variable_name: str):
        for s in scopes:
            if variable_name in s.variables:
                return True
        return False

    while index <= len(tokens)-1:
        current = tokens[index]
        if variable_declaration():
            var_declaration = get_variable_declaration()
            name = var_declaration.split()[1]
            scopes[-1].variables.append(name)
            debug("NEW VARIABLE " + var_declaration)
            index = index + len(var_declaration)
        elif scope_declaration():
            scope = get_scope_declaration()
            scopes.append(scope)
            debug("NEW SCOPE " + scopes[-1].name)
            # TODO if function add arguments to new scope
        elif scope_end():
            debug("END SCOPE " + scopes[-1].name)
            scopes.pop(-1)
        elif function_call():
            arguments = get_arguments()
            debug("WITH ARGUMENTS " + arguments)  # check if we can use them
            arguments = [x for x in arguments.split() if x.isalpha()]
            for arg in arguments:
                if not is_in_scope(arg):
                    line = tokens[:index].count('\n') + 1
                    character = tokens[:index][::-1].index('\n')
                    # print("{}, {}: {} undeclared".format(line, character, arg))
        elif variable_use():
            if not is_in_scope(current):
                line = tokens[:index].count('\n') + 1
                character = tokens[:index][::-1].index('\n') + 1
                print("{}, {}: {} undeclared".format(line, character, current))

        index += 1


code = read_file('input.txt')
detect_declarations(code)




