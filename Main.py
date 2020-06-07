from typing import List
import time


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
    if False:
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

    def scope_start():
        return current == "{"

    def scope_end():
        return current == "}"

    def variable_declaration():
        """ Checks whether we've stumbled upon variable declaration ex. "int a = 4" """

        def is_variable_declaration():
            """ Checks whether found declaration ex "int a" """
            for variable_type in types:
                if tokens[index:index+len(variable_type)] == variable_type and tokens[index-1] in separators:
                    return True

        def is_declaration_function_argument():
            """ Checks whether found declaration is a function argument ex "int a," or "int a)" """
            assignment = next_occurrence('=', index)
            comma = next_occurrence(',', index)
            rp = next_occurrence(')', index)

            # we have ',' or ')' before '='
            if comma < assignment and rp < assignment:
                return True

        return is_variable_declaration() and not is_declaration_function_argument()

    def get_variable_declaration() -> str:
        def check_initialization(declaration: str):
            """ Check whether variable is initialized another variable ex "int a = b"
            and whether that variable was previously declared """
            value = declaration[-1]
            if value.isalpha() and not is_in_scope(value):
                line = tokens[:index].count('\n') + 1
                character = tokens[:index][::-1].index('\n') + 1
                print("{}, {}: {} undeclared".format(line, character + len(declaration) - 1, value))

        delimiter = next_occurrence(";", index)
        declaration = tokens[index:delimiter]
        check_initialization(declaration)
        return declaration

    def get_arguments_from_scope_name(scope_name: str) -> List[str]:
        lp = scope_name.index('(')
        rp = scope_name.index(')')
        arguments_with_types = scope_name[lp + 1:rp].split(',')
        arguments = []
        for _argument in arguments_with_types:
            arguments.append(_argument.split()[1])
        return arguments

    def get_scope_declaration() -> Scope:
        right_parenthesis = previous_occurrence(')', index)
        left_parenthesis = previous_occurrence('(', index)
        space = previous_occurrence_from_list(separators, index-1)
        previous_space = previous_occurrence_from_list(separators, left_parenthesis-1)

        if space > right_parenthesis:  # class
            scope_name = tokens[space+1:index]
            return Scope(scope_name)
        elif previous_space < left_parenthesis:
            scope_name = tokens[previous_space+1:index]
            if scope_name.split()[0] not in ["if", "while"]:  # function
                args = get_arguments_from_scope_name(scope_name)
                _scope = Scope(scope_name)
                _scope.variables.extend(args)
                return _scope
            else:  # if or while
                return Scope(scope_name)
        else:
            raise Exception("This should not have happened - error or malformed input")

    def function_call():  # TODO this will get fucked up for (a*a);
        if tokens[index] == ')' and tokens[index+1] == ';':
            return True

    def variable_use():
        def is_variable_use_function_argument():
            assignment = next_occurrence('=', index)
            comma = next_occurrence(',', index)
            rp = next_occurrence(')', index)

            # (int a, int b, int c) itd
            if comma < assignment or rp < assignment:
                return True

        def is_variable_use():  # assumes there are spaces around variable use
            left_separators = [';', ' ', '('] # todo add math operators and check for (a=b*c) itd (no spaces)
            right_separators = [';', ' ', ')']
            return tokens[index - 1] in left_separators and tokens[index + 1] in right_separators and current.isalpha()

        # todo return !is_variable_use_a_declaration() and is_variable_use()
        if not current.isalpha():
            return False
        if is_variable_use_function_argument():
            return False
        if is_variable_use():
            return True

    def get_function_call_arguments():
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
        return False  # todo unnecessary? None evaluates to false

    while index <= len(tokens)-1:
        current = tokens[index]
        if variable_declaration():
            var_declaration = get_variable_declaration()
            name = var_declaration.split()[1]
            scopes[-1].variables.append(name)
            index = index + len(var_declaration)
            debug("NEW VARIABLE " + var_declaration)
        elif scope_start():
            scope = get_scope_declaration()
            scopes.append(scope)
            debug("NEW SCOPE " + scopes[-1].name)
        elif scope_end():
            debug("END SCOPE " + scopes[-1].name)
            scopes.pop(-1)
        elif function_call():  #w ogole to usunac bo po co wiedziec ze jest function call? variable use i elo
            arguments = get_function_call_arguments()
            debug("WITH ARGUMENTS " + arguments)  # check if we can use them
            arguments = [x for x in arguments.split() if x.isalpha()]
            for arg in arguments:
                if not is_in_scope(arg):
                    line = tokens[:index].count('\n') + 1
                    character = tokens[:index][::-1].index('\n')
                    print("{}, {}: {} undeclared".format(line, character, arg))
        elif variable_use():  # todo outside function call
            if not is_in_scope(current):
                line = tokens[:index].count('\n') + 1
                character = tokens[:index][::-1].index('\n') + 1
                print("{}, {}: {} undeclared".format(line, character, current))

        index += 1


# start = time.time()
#
# for i in range(0, 10):
code = read_file('input.txt')
detect_declarations(code)
#
# end = time.time()
# print((end - start)/10)
