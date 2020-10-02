# truth table creator
A collection of methods which together allow for parsing of boolean algebra statements.

# How to use
The project contains one file [solver.py](solver.py) which contains all necessary functions. There is however one function which wraps all these functions and allows for easy parsing of boolean algebra. This function is the [create_truth_table](solver.py) function which takes one string as parameter and parses it. It returns a list of lists which is the filled out truth table.

The list is two dimensional where the inner lists represent the columns of any typical truth table. The lists up until not including the last list however have a string as first index which stores the variable which is used this can be useful for user communication.
```py
[[    [     []
 "a", "b", 
 0,   0,    0,
 0,   1,    0,
 1,   0,    0,
 1    1     1
 ],   ],    ]
```

Incase a string representation of the truth table is required the [get_representational_string](solver.py) can help, it returns a string representation of a truth table like the one above. The output looks like this.

```
|  a  |  b   |   #   |
----------------------
   0     0   |   0   |
   0     1   |   0   |
   1     0   |   0   |
   1     1   |   1   |
```

Combined these two are included in the [solve](solver.py) function which is ment to be used when accessing this script from the console as it catches all custom exceptions and writes them to `sys.stderr`.

# How it works

There are 4 steps involved when parsing a string.
 - Polishing: Removes whitespaces and replaces certain keywords with the correct operators.
 - Syntax: Checks for syntax error like correct bracket placement.
 - Optmization: If possible optimize an example would removing any statements which are either always true or false. (No optimizations have been implemented.)
 - Parsing: Creates a method tree and also generates an empty truth table which are then used when running the method tree to fill the truth table.

*More documentation coming soon*
