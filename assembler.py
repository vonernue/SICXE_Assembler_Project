import argparse
from utils.utils import *
from utils.tables import OPCODETAB, REGTAB

PROGNAME = ""
START = 0
END = 0
SYMTAB = {}

def firstPass(file):
    """
    First pass of the assembler.
    Generate symbol table during this pass.
    """
    PC = 0
    for line in file:
        symbol, op, arg1, arg2 = parseLine(line)
        if op == "START":
            PC = int(arg1)
            SYMTAB[symbol] = PC
        elif symbol != "":
            SYMTAB[symbol] = PC

        if op[0] == '+':
            PC += 4
        else:
            if op in OPCODETAB.keys():
                PC += OPCODETAB[op][0]
            if op == "BYTE":
                if arg1[0] == 'c' or arg1[0] == 'C':
                    beg = arg1.find("'")
                    end = arg1.rfind("'")
                    PC += (end - beg - 1)
                else:
                    PC += 1
            elif op == "WORD":
                PC += 3
            elif op == "RESB":
                PC += int(arg1)
            elif op == "RESW":
                PC += 3 * int(arg1)

def secondPass(file):
    """
    Second pass of the assembler.
    Generate object code during this pass.
    """
    PC = 0
    format = 0
    for line in file:
        symbol, op, arg1, arg2 = parseLine(line)
        if op == "START":
            PROGNAME = symbol
            PC = int(arg1)
            START = PC
        if op[0] == '+': # Extended format
            format = 4
        elif op in OPCODETAB.keys(): # Get format if it's not directive or vars
            format = OPCODETAB[op][0]
        
        if format == 0:
            pass


def main(input, output):
    f = open(input, 'r')
    firstPass(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for SIC/XE")
    parser.add_argument("input", help="SIC/XE assembly file")
    parser.add_argument("--output", help="Object code output location")
    parser.add_argument("--symtab", action='store_true', help="Show symbol table")
    args = parser.parse_args()

    main(args.input, args.output)

    if args.symtab:
        printSymtab(SYMTAB)
    