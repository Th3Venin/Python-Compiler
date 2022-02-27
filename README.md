# Python-Compiler

Project stages :

1. Read the DFA configuration list and the string from the input file, then split the string into multiple components based on the received DFAs (also take into consideration the sink states).
2. Read the regex, split it into expressions (Union, Concat, Star, Plus) and characters, transform each of them into NFAs using Thompson Algorithm, then push the resulted components inside a stack. For the final process, combine the NFAs and build the DFA's configuration.
3. Using the first two stages, transform the input regexes (which are now in prenex form) into DFAs using a push-down automata, then use them to split into tokens the input string.
4. Build a parser and an interpreter for the input chunk of code (imperative programming language), using an Abstract Syntax Tree and a storage data structure (Visitor pattern) to hold the variables' values and compute the input program's final result.
