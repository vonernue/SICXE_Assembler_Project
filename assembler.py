import argparse
from termcolor import colored
from utils.utils import *
from utils.handler import Handler
from utils.tables import OPCODETAB, REGTAB

PROGNAME = ""
BASE = 0
START = 0
END = 0
SYMTAB = {}
objList = []
reservedSize = {}
tList = []

def firstPass(file):
    """
    First pass of the assembler.
    Generate symbol table during this pass.
    """
    global SYMTAB
    PC = 0
    cnt = -1;
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
                reservedSize[cnt] = int(arg1)
            elif op == "RESW":
                PC += 3 * int(arg1)
                reservedSize[cnt] = 3 * int(arg1)
        cnt += 1

def secondPass(file):
    """
    Second pass of the assembler.
    Generate object code during this pass.
    """
    global BASE
    global PROGNAME
    global START
    global END
    global objList
    PC = 0
    format = 0
    cnt = 1
    
    for line in file:
        reserved = False
        symbol, op, arg1, arg2 = parseLine(line)

        if op == "START":
            PROGNAME = symbol
            PC = int(arg1)
            START = PC
        elif op == "END":
            tList.append(objList)
            END = PC
        elif op == "BASE":
            BASE = SYMTAB[arg1]
        else:
            if op[0] == '+':
                PC += 4
            elif op == "BYTE":
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
                tList.append(objList)
                reserved = True
                objList = []
            elif op == "RESW":
                PC += 3 * int(arg1)
                tList.append(objList)
                reserved = True
                objList = []
            elif op in OPCODETAB.keys():
                PC += OPCODETAB[op][0]
            handler = Handler(line = cnt, symbol=symbol, op=op, arg1=arg1, arg2=arg2, 
                              PC=PC, BASE=BASE, SYMTAB=SYMTAB)
            if not reserved:
                objList.append(handler.objCode())
        cnt += 1
            
def genObjFile():
    """
    Generate object Program
    """
    global PROGNAME
    global START
    global END
    global SYMTAB
    global objList

    objProg = ""
    objProg += "H^" + PROGNAME + "^" + hex(START)[2:].zfill(6).upper() + "^" + hex(END - START)[2:].zfill(6).upper() + "\n"
    tStart = START
    line = 0
    for records in tList:
        if len(records) > 0:
            cnt = 0
            while(1):
                if cnt + 9 < len(records):
                    recordLen = 0
                    for i in range(cnt, cnt + 9):
                        recordLen += len(records[i]) // 2
                    objProg += "T^" + hex(tStart)[2:].zfill(6).upper() + "^" + hex(recordLen)[2:].upper() + "^"
                    for i in range(cnt, cnt + 8):
                        objProg += records[i] + "^"
                    objProg += records[cnt + 8] + "\n"
                    cnt += 9
                    tStart += recordLen
                else:
                    recordLen = 0
                    for i in range(cnt, len(records)):
                        recordLen += len(records[i]) // 2
                    objProg += "T^" + hex(tStart)[2:].zfill(6).upper() + "^" + hex(recordLen)[2:].upper() + "^"
                    for i in range(cnt, len(records) - 1):
                        objProg += records[i] + "^"
                    objProg += records[len(records) - 1] + "\n"
                    tStart += recordLen
                    line += len(records)
                    break
        else:
            line += 1
            tStart += reservedSize[line]
            
                
    return objProg
    




def main(args):
    f = open(args.input, 'r')
    firstPass(f)
    f = open(args.input, 'r')
    secondPass(f)
    print(tList)
    if args.symtab:
        printSymtab(SYMTAB)
    objProg = genObjFile()
    objProg = objProg.replace("^", args.seperator)
    print(colored(" Object Program ", "grey", "on_blue", attrs=["bold"]))
    print(objProg)
    if args.output:
        f = open(args.output, 'w')
        f.write(objProg)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for SIC/XE")
    parser.add_argument("input", help="SIC/XE assembly file")
    parser.add_argument("-o", "--output", help="Object code output location")
    parser.add_argument("-s", "--seperator", default="", help="Seperator for object code")
    parser.add_argument("--symtab", action='store_true', help="Show symbol table")
    args = parser.parse_args()

    if os.name == 'nt':
        os.system('color')

    main(args)


    