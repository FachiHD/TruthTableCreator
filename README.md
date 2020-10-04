# How to use
All sources are included in the [src](src) folder so all scripts mentioned can be found there. The [src](src) folder
includes two different scripts the first one [solver.py](src/solver.py) is the main script and houses all logical functions
needed to polish, check and parse a logical statement. The second one [bot.py](src/bot.py) is a small discord bot 
which allows for creating truth tables within discord.

### Solver
The main script includes several layers of abstraction to allow for simple and easy access. If you only want to use the 
script for what it is the [solve](src/solver.py) function will do the trick. It takes one string as argument the 
statement and handles all exceptions.
```python
# a program like this will work for the console
import solver

while True:
    solver.solve(input("Formula: "))
```

For a little more complexity the [create_truth_table](src/solver.py) function creates a filled out truth table
given a statement as a string. You can get a string representing such a truth table by calling the 
[get_representational_string](src/solver.py) method which returns a string representing the truth table.

### Bot
This script contains a discord bot which can be run by passing a token. Currently two commands are supported 
[solve](src/bot.py) and [clear_cache](src/bot.py). The first parses a given string and sends the truth table in the 
channel. Should the message be over 2000 which is the discord message character limit the truth table will be send
in a file. Because the bot also supports the caching of truth tables for performance reasons there exists the
[clear_cache](src/bot.py) command which clears the internal cache and can only be used by the owner of the bot. To
become owner you have to edit the `owner_id` parameter in the client initizaltion line 
  
The cache works by first pre-processing the statement and then calculating its hash and afterwards checking if that
hash has been saved in [cached](src/cached).

# GitHub
Currently all 
