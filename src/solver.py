import math
import sys
import traceback

# TODO: make index optional for exceptions as it confuses the end user


class SolverException(Exception):
    def __init__(self, expression, idx, message, name):
        error_message = f"{expression}\n{' ' * idx}^\n{name}: {message}\n"
        self.error_message = error_message


class InvalidBracketException(SolverException):
    def __init__(self, expression, idx, message):
        super().__init__(expression, idx, message, "InvalidBracketException")


class InvalidCharacterException(SolverException):
    def __init__(self, expression, idx, message):
        super().__init__(expression, idx, message, "InvalidCharacterException")


TRUE_SIGN = "1"
FALSE_SIGN = "0"
NEGATION_SIGN = "¬"
AND_SIGN = "∧"
NAND_SIGN = "⊼"
OR_SIGN = "∨"
NOR_SIGN = "⊽"
XOR_SIGN = "⊻"
IF_SIGN = "→"
EQUAL_SIGN = "↔"
UNEQUAL_SIGN = "⇹"
OPENING_BRACKET = "("
CLOSING_BRACKET = ")"

SPECIAL_CHARACTERS = [
    TRUE_SIGN,
    FALSE_SIGN,
    NEGATION_SIGN,
    AND_SIGN,
    NAND_SIGN,
    OR_SIGN,
    NOR_SIGN,
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
    NAND_SIGN,
    OR_SIGN,
    NOR_SIGN,
    XOR_SIGN,
    IF_SIGN,
    EQUAL_SIGN,
    UNEQUAL_SIGN
]

print(len(OPERATORS))

REPLACING_DICTIONARY = {
    "true": TRUE_SIGN,
    "false": FALSE_SIGN,
    "not ! -": NEGATION_SIGN,
    "nand": NAND_SIGN,
    "and &&": AND_SIGN,
    "nor": NOR_SIGN,
    "xor": XOR_SIGN,
    "or ||": OR_SIGN,
    "if >": IF_SIGN,
    "unequal unequals !=": UNEQUAL_SIGN,
    "equals equal == =": EQUAL_SIGN,
}

BRACKETS = [
    OPENING_BRACKET,
    CLOSING_BRACKET
]

VALUES = {}

# TODO: better documenting for the gates (more consistency)


def TRUE():
    """Always returns true"""
    return True


def FALSE():
    """Always returns false"""
    return False


def NORMAL(var):
    """Returns an actual value read from VALUES this method will always be last when running the method tree"""
    return VALUES[var]


def NOT(var):
    """Negates the result"""
    # we use the * and 1: as it may be a constant value in which case we have no parameters to pass so there is no list
    return not var[0](*var[1:])


def AND(var):
    """Checks if both results are true"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return res1 and res2


def NAND(var):
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return not (res1 and res2)


def OR(var):
    """Checks if any result is true"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return res1 or res2


def NOR(var):
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return not (res1 or res2)


def XOR(var):
    """Checks that only one result is true"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return (res1 and not res2) or (not res1 and res2)


def IF(var):
    """Returns true if result one is false else it returns result two"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return not res1 or res2


def EQUALS(var):
    """Checks if both results are the same"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return not ((res1 and not res2) or (not res1 and res2))


def NOT_EQUALS(var):
    """Checks if both results return the opposite same as XOR"""
    res1 = var[0][0](*var[0][1:])
    res2 = var[1][0](*var[1][1:])
    return (res1 and not res2) or (not res1 and res2)


def remove_redundant_negations(string):
    """ Removes any doubled negations in the string

    :param string: The string to process.
    :return: The processed string.
    """
    string_length = len(string)
    idx = 0
    while idx < string_length:
        if string[idx] == NEGATION_SIGN:
            # check for the next position and check if it is also a negation if so remove both
            if idx + 1 <= string_length and string[idx + 1] == NEGATION_SIGN:
                string = string[0:idx] + string[idx + 2:string_length]
                idx -= 2
                string_length -= 2
                if idx < 0:
                    idx = 0
                continue

        idx += 1
    return string


def check_surrounded(string):
    """ Check if the string as a whole is surrounded by brackets

    :param string: The string to check.
    :return: True if it is surrounded.
    """
    length = len(string)
    if length <= 1:
        return False

    counter = 0
    for idx in range(length):
        char = string[idx]
        if char == OPENING_BRACKET:
            counter += 1
        elif char == CLOSING_BRACKET:
            counter -= 1

        # return the string if we exited all brackets but have not looped through the entire string
        # meaning there are no more brackets around the entire string
        if counter == 0 and idx != length - 1:
            return False
    return True


def polish_statement(string):
    """ Removes any brackets and negations containing the entire string

    :param string: The string to process.
    :return: If the statement was negated and the processed string.
    """

    negated = False
    length = len(string)
    if length <= 2:
        return string.startswith(NEGATION_SIGN), string
    while True:
        # brackets or negations containing the entire string will always have to be on 0 index position
        char = string[0]

        to_check = string
        if char == NEGATION_SIGN:
            to_check = to_check[1:]

        surrounded = check_surrounded(to_check)
        if surrounded:
            if char == NEGATION_SIGN:
                negated = not negated
                string = string[1:]
                length -= 1
            string = string[1:length - 1]
            length -= 2
        else:
            return negated, string


def create_method_tree(string):
    """ Creates a method_tree from a checked string using recursion

    Creates a list which contains a method at index 0 and a list at 1 index which stores two lists of the same type.
    A given string should contain both sides in brackets as no operator hierarchy is accounted for. It works by
    extracting both sides of the statement and afterwards checking if they are variables if not it will call
    itself again to get the necessary method tree.

    :param string: The statement for which a method tree should be constructed.
    :return: Any variables found and the method tree.
    """

    negated, string = polish_statement(string)
    length = len(string)
    if length <= 2:
        stripped = string.lstrip(NEGATION_SIGN)
        # check if the string is a constant
        if string == TRUE_SIGN:
            stripped = None
            args = [TRUE]
        elif string == FALSE_SIGN:
            stripped = None
            args = [FALSE]
        else:
            args = [NORMAL, stripped]

        if negated:
            stripped = string.lstrip(NEGATION_SIGN)
            return stripped, [
                NOT, args
            ]
        else:
            return stripped, args

    # TODO: fix danger coming from rogues characters
    done_first_statement = False
    first_statement = ""
    second_statement = ""
    operator = ""
    # incremented every time we pass a OPENING_BRACKET and decremented every time we pass a CLOSING_BRACKET
    # when this is 0 it means we have exited all brackets
    bracket_counter = 0
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

        if char != NEGATION_SIGN and bracket_counter == 0 and not done_first_statement:
            # switch which statement we are collecting and store the operator
            done_first_statement = True
            if idx + 1 >= length:
                raise InvalidCharacterException(string, idx, "expected operator")
            operator = string[idx + 1]
            if operator not in OPERATORS:
                raise InvalidCharacterException(string, idx, "expected operator")
            idx += 1
            bracket_counter = 0
        idx += 1

    # stores any negations because they will be removed in polish_statement
    methods_list = []
    variables = []
    statements = [first_statement, second_statement]

    # loops through the statements and checks if they are only the length of one which means it is a variable
    # if so it appends the NORMAL method which is the only method returning a boolean value
    # if not it pareses the string again by calling itself and then adds this sub_tree to the current tree

    for statement in statements:
        sub_variables, sub_tree = create_method_tree(statement)
        # TODO: use a set instead of a list to avoid checking for duplicates
        if sub_variables is not None:
            for i in sub_variables:
                if i not in variables:
                    variables.append(i)
        methods_list.append(sub_tree)

    # finds the correct operator to use and stores the method without calling it
    # TODO: find a better way to do this
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
    elif operator == NAND_SIGN:
        func = NAND
    elif operator == NOR_SIGN:
        func = NOR
    else:
        raise Exception("reached end of operator checker without conclusion")

    if negated:
        return variables, [
            NOT, [
                func,
                methods_list
            ]
        ]
    else:
        return variables, [
            func,
            methods_list
        ]


def get_matching_brackets(string):
    """ Returns a dictionary of matching brackets also checks for any syntax errors regarding brackets

    Works by adding every OPENING_BRACKET index to a dictionary as a key. When finding a CLOSING_BRACKET it searches
    for the highest key which has not yet been assigned a CLOSING_BRACKET index if it finds one it assigns it. Should
    it encounter any discrepancies a InvalidBracketException is raised.

    :param string: The string to create this dictionary for.
    :return: The dictionary having all `OPENING_BRACKETS` as keys and their `CLOSING_BRACKETS` as values
    """
    dic = {}
    for idx in range(len(string)):
        char = string[idx]
        if char == OPENING_BRACKET:
            dic[idx] = -1
        elif char == CLOSING_BRACKET:
            if not dic:
                raise InvalidBracketException(string, idx, "missing matching opening bracket")
            else:
                for entry in reversed(dic.keys()):
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


def replace_with_conform_operators(string):
    """ Replaces all keywords with their corresponding operator

    Loops through every key in REPLACING_DICTIONARY and splits. It then loops through the splitted list
    to replace all occurrences of every element in this list with the corresponding one character operator.

    :param string: The string to replace in.
    :return: The processed string.
    """

    # TODO: Accept the replacing dictionary as parameter
    for replace_string in REPLACING_DICTIONARY.keys():
        replace_list = replace_string.split()
        for replace in replace_list:
            string = string.replace(replace, REPLACING_DICTIONARY[replace_string])
    return string


def generate_truth_values(variables):
    """ Generates a 2 dimensional array which contains an empty truth table

    Generates a 2 dimensional array of lists in the shape of a typical truth table in which the different columns
    represent the columns in a real truth table. The lists up until not including the last one all have their 0 index
    set to a variables present in variables. The last list is filled with None and should be used to store results.

    :param variables: List of variables to use.
    :return: The empty truth table with an extra list at the end to store the results in.
    """
    truth_table = []
    variable_count = len(variables)
    column_length = int(math.pow(2, variable_count))

    # the inner loop works by having a counter and a limit switch_at which when reached will switch current_value
    # current_value is added every loop to holder
    # switch_at is calculated using 2 to the power of i because i counts down the last list will switch every time
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
    """ Runs a method tree and fills an empty truth table with the given values

    :param tree: The tree to run.
    :param table: The truth table to fill and use.
    :param variables: The variables present in the statement.
    :return: The filled out truth table.
    """
    global VALUES
    variable_count = len(variables)
    for step in range(int(math.pow(2, variable_count))):
        for column in range(variable_count):
            VALUES[table[column][0]] = table[column][step + 1]
        res = tree[0](tree[1])
        table[variable_count][step] = res
    return table


def pre_process_statement(string):
    """ Pre processes a given string to be then further processed

    :param string: The string to process.
    :return: The processed string.
    """
    string = replace_with_conform_operators(string)
    string = string.lower().replace(" ", "").rstrip().lstrip().rstrip("-")
    string = replace_with_conform_operators(string)
    string = remove_redundant_negations(string)
    return string


def create_truth_table(string, pre_process=True):
    """ Collection of functions which polish, check, optimize and parse the given string

    :param pre_process: If the string should be pre processed.
    :param string: The string to process.
    :return: The filled out truth table.
    """
    # -- prepare the statement --
    if pre_process:
        string = pre_process_statement(string)
    # TODO: wrap all statements in brackets as to prevent not using operator hierarchy

    # -- check for syntax errors --
    get_matching_brackets(string)
    # TODO: check for rogue characters

    # -- optimize the statement --
    # TODO: add optimization algorithms

    # -- parse the statement --
    variables, method_tree = create_method_tree(string)
    truth_table = generate_truth_values(variables)
    completed_truth_table = run_truth_table(method_tree, truth_table, variables)

    return completed_truth_table


def boolean_to_string(value):
    return "1" if value else "0"


def get_representational_string(table):
    """ Returns a string which represents a given truth table

    :param table: The table to represent.
    :return: The generated string.
    """
    variables = []
    for i in range(len(table) - 1):
        variables.append(table[i][0])
    variable_count = len(variables)

    to_print = "|"
    for i in range(variable_count):
        to_print += f"  {variables[i]}  {' ' if i >= variable_count - 1 else ''}|"
    to_print += "   #   |"
    total_print = to_print + "\n" + "-" * ((variable_count + 1) * 5) + "-" * (variable_count + 5) + "\n"

    for i in range(int(math.pow(2, variable_count))):
        to_print = ""
        for j in range(variable_count):
            to_print += f"   {boolean_to_string(table[j][i + 1])}  {' ' if j >= variable_count - 1 else ''}"
        to_print += f"|   {boolean_to_string(table[variable_count][i])}   |"
        total_print += to_print + "\n"
    return total_print


def solve(string):
    """ A function which first creates a truth table and then prints it it also handles all custom exceptions raised

    :param string: The string to process.
    :return: Nothing.
    """
    try:
        table = create_truth_table(string)
        print(get_representational_string(table))
    except SolverException as e:
        sys.stderr.write(e.error_message)
    except BaseException as e:
        traceback.print_exc()


# No need to type I have already copied it
# solve("-(--((-p or --q) and -(q and -p)) equal ((q if p) and (-p or --q))) if ((r and -s) unequal (p and -r))")
