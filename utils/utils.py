from termcolor import colored
from utils.tables import *
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
    if len(tokens) == 3:
        symbol = tokens[0]
        op = tokens[1]
        arg1 = tokens[2]
    elif len(tokens) == 2:
        op = tokens[0]
        args = tokens[1].split(',')
        if len(args) == 2:
            arg1 = args[0]
            arg2 = args[1]
        else:
            arg1 = args[0]
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
        if key not in REGTAB.keys():
            print("{:<10} | {:<10}".format(key, hex(value)))
    print("-----------------------")