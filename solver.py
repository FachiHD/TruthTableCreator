import math
import sys


class SolverException(Exception):
    def __init__(self, expression, idx, message, name):
        error_message = f"{expression}\n{' ' * idx}^\n{name}: {message}\n"
        self.error_message = error_message


class InvalidBracketException(SolverException):
    def __init__(self, expression, idx, message):
        super().__init__( expression, idx, message, "InvalidBracketException")


class InvalidCharacterException(SolverException):
    def __init__(self, expression, idx, message):
        super().__init__(expression, idx, message, "InvalidCharacterException")


NEGATION_SIGN = "¬"
AND_SIGN = "∧"
OR_SIGN = "∨"
XOR_SIGN = "⊻"
IF_SIGN = "→"
EQUAL_SIGN = "↔"
UNEQUAL_SIGN = "⇹"
OPENING_BRACKET = "("
CLOSING_BRACKET = ")"

SPECIAL_CHARACTERS = [
    NEGATION_SIGN,
    AND_SIGN,
    OR_SIGN,
    XOR_SIGN,
    IF_SIGN,
    EQUAL_SIGN,
    UNEQUAL_SIGN,
    OPENING_BRACKET,
    CLOSING_BRACKET
]

OPERATORS = [
    NEGATION_SIGN,
    AND_SIGN,
    OR_SIGN,
    XOR_SIGN,
    IF_SIGN,
    EQUAL_SIGN,
    UNEQUAL_SIGN
]

REPLACING_DICTIONARY = {
    "not ! -": NEGATION_SIGN,
    "and &&": AND_SIGN,
    "xor": XOR_SIGN,
    "or ||": OR_SIGN,
    "if >": IF_SIGN,
    "unequal !=": UNEQUAL_SIGN,
    "equal == =": EQUAL_SIGN,
}


BRACKETS = [
    OPENING_BRACKET,
    CLOSING_BRACKET
]


VALUES = {}


def NORMAL(var):
    return VALUES[var]


def NOT(var):
    return not var[0](var[1])


def AND(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return res1 and res2


def OR(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return res1 or res2


def XOR(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return (res1 and not res2) or (not res1 and res2)


def IF(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return not res1 or res2


def EQUALS(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return not ((res1 and not res2) or (not res1 and res2))


def NOT_EQUALS(var):
    res1 = var[0][0](var[0][1])
    res2 = var[1][0](var[1][1])
    return (res1 and not res2) or (not res1 and res2)


def remove_redundant_negations(string: str) -> str:
    string_length = len(string)
    idx = 0
    while idx < string_length:
        if string[idx] == NEGATION_SIGN:
            # check for the next position and check if it is also a negation if so remove both
            if idx + 1 <= string_length and string[idx + 1] == NEGATION_SIGN:
                first_part = string[0:idx]
                second_part = string[idx + 2:string_length]
                string = first_part + second_part
                idx -= 2
                string_length -= 2
                if idx < 0:
                    idx = 0
                continue

        idx += 1
    return string


def get_variables(string):
    variables = []
    for char in string:
        if char not in SPECIAL_CHARACTERS:
            if char not in variables:
                variables.append(char)
    return tuple(variables)


def polish_statement(string: str):
    # this code is horrible i will fix it one day
    length = len(string)
    if length <= 0:
        return string

    if string[0] == NEGATION_SIGN:
        string = string[1:]
        length = len(string)

    if len(string) <= 1:
        return string
    return string[1:length - 1]


def create_method_tree(string):

    done_first_statement = False
    first_statement = ""
    second_statement = ""
    operator = ""
    bracket_counter = 0
    length = len(string)
    idx = 0

    while idx < length:
        char = string[idx]
        if not done_first_statement:
            first_statement += char
        else:
            second_statement += char

        if char == OPENING_BRACKET:
            bracket_counter += 1
        elif char == CLOSING_BRACKET:
            bracket_counter -= 1

        if char != NEGATION_SIGN and bracket_counter == 0:
            if not done_first_statement:
                done_first_statement = True
                operator = string[idx + 1]
                idx += 1
            bracket_counter = 0
        idx += 1

    negations = [first_statement.startswith(NEGATION_SIGN), second_statement.startswith(NEGATION_SIGN)]
    first_statement = polish_statement(first_statement)
    second_statement = polish_statement(second_statement)

    methods_list = []
    variables = []
    statements = [first_statement, second_statement]

    for idx in range(len(statements)):
        statement = statements[idx]
        length = len(statement)
        if length == 1:
            if statement not in variables:
                variables.append(statement)
            # the statement is a single variable which has no negation
            if negations[idx]:
                methods_list.append([NOT, [NORMAL, statement]])
            else:
                methods_list.append([NORMAL, statement])
        else:
            sub_variables, sub_tree = create_method_tree(statement)
            # use a set instead of a list to avoid checking for duplicates
            for i in sub_variables:
                if i not in variables:
                    variables.append(i)
            if negations[idx]:
                methods_list.append([NOT, sub_tree])
            else:
                methods_list.append(sub_tree)

    # there has to be a better way to do these checks but i am too tired
    if operator not in OPERATORS:
        raise InvalidCharacterException(string, idx + len(first_statement) + 1, "expected operator")
    elif operator == AND_SIGN:
        func = AND
    elif operator == OR_SIGN:
        func = OR
    elif operator == XOR_SIGN:
        func = XOR
    elif operator == IF_SIGN:
        func = IF
    elif operator == EQUAL_SIGN:
        func = EQUALS
    elif operator == UNEQUAL_SIGN:
        func = NOT_EQUALS
    else:
        raise Exception("reached end of operator checker without conclusion")

    return variables, [
        func,
        methods_list
    ]


def get_matching_brackets(string) -> dict:
    dic = {}
    for idx in range(len(string)):
        if string[idx] == OPENING_BRACKET:
            dic[idx] = -1
        elif string[idx] == CLOSING_BRACKET:
            if not dic:
                raise InvalidBracketException(string, idx, "missing matching opening bracket")
            else:
                for entry in reversed(dic):
                    if dic[entry] == -1:
                        if entry == idx - 1:
                            raise InvalidBracketException(string, idx, "empty brackets")
                        dic[entry] = idx
                        break
                else:
                    raise InvalidBracketException(string, idx, "missing matching opening bracket")
    for entry in dic:
        if dic[entry] == -1:
            raise InvalidBracketException(string, entry, "missing matching closing bracket")
    return dic


def replace_with_conform_operators(string: str) -> str:
    for replace_string in REPLACING_DICTIONARY.keys():
        replace_list = replace_string.split()
        for replace in replace_list:
            string = string.replace(replace, REPLACING_DICTIONARY[replace_string])
    return string


def generate_truth_values(variables):
    truth_table = []
    variable_count = len(variables)
    column_length = int(math.pow(2, variable_count))
    for i in range(variable_count - 1, -1, -1):
        holder = [variables[variable_count - i - 1]]
        current_value = False
        switch_at = int(math.pow(2, i))
        counter = 0
        for j in range(column_length):
            if counter >= switch_at:
                counter = 0
                current_value = not current_value
            holder.append(current_value)
            counter += 1
        truth_table.append(holder)
    truth_table.append([None] * column_length)
    return truth_table


def run_truth_table(tree, table, variables):
    global VALUES
    variable_count = len(variables)
    for step in range(int(math.pow(2, variable_count))):
        for column in range(variable_count):
            VALUES[table[column][0]] = table[column][step + 1]
        res = tree[0](tree[1])
        table[variable_count][step] = res
    return table


def create_truth_table(string: str) -> list:
    # -- polish the formula --
    string = string.lower().replace(" ", "").rstrip().lstrip().rstrip("-")
    string = replace_with_conform_operators(string)
    string = remove_redundant_negations(string)

    # -- check for syntax errors --
    brackets = get_matching_brackets(string)

    # -- optimize the formula --

    # -- parse the formula --
    variables, method_tree = create_method_tree(string)
    truth_table = generate_truth_values(variables)
    completed_truth_table = run_truth_table(method_tree, truth_table, variables)

    return completed_truth_table


def boolean_to_int(value):
    return "1" if value else "0"


def print_truth_table(table):
    variables = []
    for i in range(len(table) - 1):
        variables.append(table[i][0])
    variable_count = len(variables)

    to_print = "|"
    for i in range(variable_count):
        to_print += f"  {variables[i]}  {' ' if i >= variable_count - 1 else ''}|"
    to_print += "   #   |"
    print(to_print)
    print("-" * ((variable_count + 1) * 5) + "-" * (variable_count + 5))

    for i in range(int(math.pow(2, variable_count))):
        to_print = ""
        for j in range(variable_count):
            to_print += f"   {boolean_to_int(table[j][i + 1])}  {' ' if j >= variable_count - 1 else ''}"
        to_print += f"|   {boolean_to_int(table[variable_count][i])}   |"
        print(to_print)


try:
    print_truth_table(create_truth_table("-(--((-p or --q) and -(q and -p)) equal ((q if p) and (-p or --q))) if ((r and -s) unequal (p and -r))"))
except SolverException as e:
    print(sys.stderr.write(e.error_message))
