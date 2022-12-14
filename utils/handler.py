from utils.tables import *
from utils.utils import *


class Handler:
    def __init__(self, line, symbol, op, arg1, arg2, PC, BASE, SYMTAB):
        """
        Create a new handler with necessary info
        """
        self.line = line
        self.symbol = symbol
        self.arg2 = arg2
        self.PC = PC
        self.BASE = BASE
        self.SYMTAB = SYMTAB

        if arg1 != "" and arg1[0] == '#':
            self.arg1 = arg1[1:]
            self.immediate = True
            self.indirect = False
        elif arg1 != "" and arg1[0] == '@':
            self.arg1 = arg1[1:]
            self.immediate = False
            self.indirect = True
        else:
            self.arg1 = arg1
            self.immediate = False
            self.indirect = False

        if arg2 != "":
            self.indexed = True
        else:
            self.indexed = False

        if op[0] == '+':
            self.op = op[1:]
            self.extended = True
        else:
            self.op = op
            self.extended = False

    def objCode(self):
        """
        Generate object code
        """

        if self.op == "BYTE":
            return self.BYTE()
        elif self.op == "WORD":
            return self.WORD()
        elif self.op == "RESB" or self.op == "RESW":
            return None
        elif self.op in OPCODETAB.keys():
            if OPCODETAB[self.op][0] == 2:
                return self.format2()
            elif OPCODETAB[self.op][0] == 3:
                if self.extended:
                    return self.format4()
                else:
                    return self.format3()

        else:
            raise Exception(f"Line {self.line}: Invalid operation: {self.op}")
        

    def BYTE(self):
        """
        Handle BYTE memnomic
        """
        if self.arg1[0] == 'c' or self.arg1[0] == 'C':
            beg = self.arg1.find("'")
            end = self.arg1.rfind("'")
            data = self.arg1[beg+1:end]
            obj = ""
            for i in data:
                obj += hex(ord(i))[2:]
            return obj.upper()
        elif self.arg1[0] == 'x' or self.arg1[0] == 'X':
            beg = self.arg1.find("'")
            end = self.arg1.rfind("'")
            obj = self.arg1[beg+1:end]
            return obj.upper()
            
    def WORD(self):
        """
        Handle WORD memnomic
        """
        return hex(int(self.arg1))[2:].zfill(6).upper()

    def format2(self):
        """
        Handle format2 instructions
        """
        obj = int(OPCODETAB[self.op][1], 16)
        obj = obj << 4
        if self.arg1 != "":
            obj += int(REGTAB[self.arg1])
        obj = obj << 4
        if self.arg2 != "":
            obj += int(REGTAB[self.arg2])
        return hex(obj)[2:].zfill(4).upper()

    def format3(self):
        """
        Handle format3 instructions
        """
        obj = 0
        if self.immediate:
            if self.arg1 in self.SYMTAB.keys():
                TA = self.SYMTAB[self.arg1] - self.PC
                # PC Relative
                if TA >= -2048 and TA <= 2047:  
                    if TA < 0:
                        TA = twosComp(TA, 2) & int("0000111111111111", 2)
                    obj = int(OPCODETAB[self.op][1], 16) 
                    obj = obj << 4
                    obj += flagConstructor(0, 1, 0, 0, 1, 0)
                    obj = obj << 12
                    obj += TA
                # Base Relative
                else:   
                    TA = self.SYMTAB[self.arg1] - self.BASE
                    if TA >= 0 and TA <= 4095:
                        obj = int(OPCODETAB[self.op][1], 16) 
                        obj = obj << 4
                        obj += flagConstructor(0, 1, 0, 1, 0, 0)
                        obj = obj << 12
                        obj += TA
                    else:
                        raise Exception(f"Line {self.line}: Symbol out of range")
            # Immediate
            else:   
                TA = int(self.arg1)
                obj = int(OPCODETAB[self.op][1], 16)
                obj = obj << 4
                obj += flagConstructor(0, 1, 0, 0, 0, 0)
                obj = obj << 12
                obj += TA
        elif self.indirect:
            TA = self.SYMTAB[self.arg1] - self.PC
            # PC Relative
            if TA >= -2048 and TA <= 2047:  
                if TA < 0:
                    TA = twosComp(TA, 2) & int("0000111111111111", 2)
                obj = int(OPCODETAB[self.op][1], 16) 
                obj = obj << 4
                obj += flagConstructor(1, 0, 0, 0, 1, 0)
                obj = obj << 12
                obj += TA
            # Base Relative
            else:   
                TA = self.SYMTAB[self.arg1] - self.BASE
                if TA >= 0 and TA <= 4095:
                    obj = int(OPCODETAB[self.op][1], 16) 
                    obj = obj << 4
                    obj += flagConstructor(1, 0, 0, 1, 0, 0)
                    obj = obj << 12
                    obj += TA
                else:
                    raise Exception(f"Line {self.line}: Symbol out of range")
        else:
            if self.op == "RSUB":
                return "4F0000"
            TA = self.SYMTAB[self.arg1] - self.PC
            # PC Relative
            if TA >= -2048 and TA <= 2047:  
                if TA < 0:
                    TA = twosComp(TA, 2) & int("0000111111111111", 2)
                obj = int(OPCODETAB[self.op][1], 16) 
                obj = obj << 4
                obj += flagConstructor(1, 1, self.indexed, 0, 1, 0)
                obj = obj << 12
                obj += TA
            # Base Relative
            else:   
                TA = self.SYMTAB[self.arg1] - self.BASE
                if TA >= 0 and TA <= 4095:
                    obj = int(OPCODETAB[self.op][1], 16) 
                    obj = obj << 4
                    obj += flagConstructor(1, 1, self.indexed, 1, 0, 0)
                    obj = obj << 12
                    obj += TA
                else:
                    raise Exception(f"Line {self.line}: Symbol out of range")

        return hex(obj)[2:].zfill(6).upper()
        
    def format4(self):
        """
        Handle format4 instructions
        """
        obj = 0
        if self.immediate:
            if self.arg1 in self.SYMTAB.keys():
                TA = self.SYMTAB[self.arg1]
                # PC Relative
                obj = int(OPCODETAB[self.op][1], 16) 
                obj = obj << 4
                obj += flagConstructor(0, 1, 0, 0, 0, 1)
                obj = obj << 20
                obj += TA
            # Immediate
            else:   
                TA = int(self.arg1)
                obj = int(OPCODETAB[self.op][1], 16)
                obj = obj << 4
                obj += flagConstructor(0, 1, 0, 0, 0, 1)
                obj = obj << 20
                obj += TA
        elif self.indirect:
            TA = self.SYMTAB[self.arg1]
            # PC Relative
            obj = int(OPCODETAB[self.op][1], 16) 
            obj = obj << 4
            obj += flagConstructor(1, 0, 0, 0, 0, 1)
            obj = obj << 20
            obj += TA
        else:
            TA = self.SYMTAB[self.arg1]
            # PC Relative
            obj = int(OPCODETAB[self.op][1], 16) 
            obj = obj << 4
            obj += flagConstructor(1, 1, self.indexed, 0, 0, 1)
            obj = obj << 20
            obj += TA

        return hex(obj)[2:].zfill(8).upper()