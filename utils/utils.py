from termcolor import colored
import os

if os.name == 'nt':
    os.system('color')

def parseLine(line: str) -> tuple:
    """
    Parse line.
    """
    symbol = ""
    op = ""
    arg1 = ""
    arg2 = ""
    tokens = line.split()
    if len(tokens) == 4:
        symbol = tokens[0]
        op = tokens[1]
        arg1 = tokens[2]
        arg2 = tokens[3]
    elif len(tokens) == 3:
        symbol = tokens[0]
        op = tokens[1]
        arg1 = tokens[2]
    elif len(tokens) == 2:
        op = tokens[0]
        arg1 = tokens[1]
    elif len(tokens) == 1:
        op = tokens[0]
    return symbol, op, arg1, arg2

def printSymtab(symtab: dict):
    """
    Print symbol table.
    """
    print(colored(" Symbol Table ", "grey", "on_blue", attrs=["bold"]))
    print("-----------------------")
    print("{:<10} | {:<10}".format('SYMBOL', 'LOC'))
    print("-----------------------")
    for key, value in symtab.items():
        print("{:<10} | {:<10}".format(key, hex(value)))
    print("-----------------------")