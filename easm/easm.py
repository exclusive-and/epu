
# EASM: The EPU Reference Assembler

from typing import List, Tuple


# An enumeration of possible error codes that the assembler may throw

class AsmError:

    OK              = 0b00000000
    NO_SOURCE       = 0b11000001
    FILE_OPEN_ERROR = 0b11000010
    SYNTAX_ERROR    = 0b10000010

# Detailed info about each error

class AsmErrorInfo:
    
    def __init__ (self, errno, text, lineno=0, colno=0, line=""):
        self.errno  = errno

        self.lineno = lineno
        self.colno  = colno
        self.line   = line

        self.text   = text

# Enum of colours useful for printing compiler messages

class AsmColours:

    RED     = "\033[31m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    END     = "\033[0m"


# Print the contents of an error message with some style because I'm fancy

def printError (errinfo : AsmErrorInfo):
    if errinfo != None:

        errno = errinfo.errno

        # Create the error prefix
        prefix = ""
        if (errno & 0x80) > 0:
            prefix += AsmColours.RED + "Error" + AsmColours.END

        if (errno & 0x40) == 0:
            prefix += ": at {}:{}: ".format (errinfo.lineno, errinfo.colno)
        else:
            prefix += ": "

        # Print the contents of the message
        contents = errinfo.text

        message = prefix + contents

        if (errno & 0x40) == 0:
            # Point out the line and location
            pointer = "{}: ".format (errinfo.lineno)
            pointer += "{}\n".format (errinfo.line)
            pointer += " " * len (str (errinfo.lineno)) + "  "
            pointer += "~" * errinfo.colno + "^" + "~" * (len (errinfo.line) - errinfo.colno)

            message += "\n" + pointer

        print (message)


# Read the contents of a file. Only return an error if we failed to do that.

def readFile (filename : str) -> Tuple[AsmErrorInfo, List[str]]:
    err = None
    fc = []

    try:
        f = open (filename, "rt")
        fc = f.readlines ()
        f.close ()

    except OSError as ex:
        errtext = "{}".format (ex)
        err = AsmErrorInfo (AsmError.FILE_OPEN_ERROR, errtext)

    return err, fc


# A simple line and line number pairing for convenience

class Line:

    def __init__ (self, lineno, text):
        self.lineno = lineno
        self.text = text

# Skip any spaces that may follow in the line
def skipWhitespace (colno : int, line : Line) -> int:
    while True:
        if colno == len (line.text):
            break
        elif line.text[colno] != " " and line.text[colno] != "\t":
            break
        else:
            colno += 1
    return colno

# Skip any whitespaces and return the first thing that has alphanumeric characters
def getWord (colno : int, line : Line) -> Tuple[int, str]:
    colno = skipWhitespace (colno, line)
    start = colno
    while True:
        if colno == len (line.text):
            break
        elif not line.text[colno].lower () in "abcdefghijklmnopqrstuvwxyz0123456789_":
            break
        else:
            colno += 1
    return colno, line.text[start:colno].lower()

# Skip any whitespaces and return the first thing if it looks like an integer
def getImmediate (colno : int, line : Line) -> Tuple[int, int]:
    colno = skipWhitespace (colno, line)
    start = colno
    while True:
        if colno == len (line.text):
            break
        elif not line.text[colno].lower () in "0123456789abcdef":
            break
        else:
            colno += 1

    if start != colno:
        return colno, int (line.text[start:colno], 16)
    else:
        return colno, None


# Abstract representation of a single instruction

class Instr:

    LDI     = 0b00000000
    ATOB    = 0b00000010
    BTOA    = 0b00000100
    ADD     = 0b00000001
    SUB     = 0b00000011
    SEQ     = 0b00000101
    SLT     = 0b00000111
    JNZ     = 0b00001011
    JEZ     = 0b00001101
    JMP     = 0b00001001

    NO_OPERAND  = 0
    IMMEDIATE   = 1
    REGISTER    = 2

    def __init__ (self, mnemonic, operandKind):
        self.mnemonic = mnemonic
        self.operandKind = operandKind

        self.register = 0
        self.immediate = 0

# Abstract representation of a register
# Note: this is given its own class for the convenience of a distinguishable type.

class Register:
    
    def __init__ (self, regnum):
        self.regnum = regnum

class AssembleResult:

    COMMENT        = 0
    INSTRUCTION    = 1
    EMPTY          = 2
    LABEL          = 3
    ANNOTATION     = 4

    def __init__ (self, kind):
        self.kind = kind

        self.comment = ""
        self.label = None
        self.instruction = None
        self.annotation = None


# Assemble a single line.
# Return any errors found, and the resultant object.

def assembleLine (line : Line) -> Tuple[List[AsmErrorInfo], AssembleResult]:

    keywords = \
        { "ldi"  : Instr (Instr.LDI , Instr.IMMEDIATE)
        , "atob" : Instr (Instr.ATOB, Instr.REGISTER)
        , "atob" : Instr (Instr.BTOA, Instr.REGISTER)
        , "add"  : Instr (Instr.ADD , Instr.REGISTER)
        , "sub"  : Instr (Instr.SUB , Instr.REGISTER)
        , "seq"  : Instr (Instr.SEQ , Instr.REGISTER)
        , "slt"  : Instr (Instr.SLT , Instr.REGISTER)
        , "jnz"  : Instr (Instr.JNZ , Instr.REGISTER)
        , "jez"  : Instr (Instr.JEZ , Instr.REGISTER)
        , "jmp"  : Instr (Instr.JMP , Instr.REGISTER)
        , "r0"   : Register (0)
        , "r1"   : Register (1)
        , "r2"   : Register (2)
        , "r3"   : Register (3)
        , "r4"   : Register (4)
        , "r5"   : Register (5)
        , "r6"   : Register (6)
        , "r7"   : Register (7)
        , "r8"   : Register (8)
        , "r9"   : Register (9)
        , "r10"  : Register (10)
        , "r11"  : Register (11)
        , "r12"  : Register (12)
        , "r13"  : Register (13)
        , "r14"  : Register (14)
        , "r15"  : Register (15) }

    colno = 0
    colno = skipWhitespace (colno, line)

    # Utility routine for conveniently giving syntax errors
    def mkSyntaxError (text) -> AsmErrorInfo:
        return AsmErrorInfo \
            ( AsmError.SYNTAX_ERROR
            , "Syntax error: {}".format (text)
            , line.lineno, colno, line.text )

    errors = []
    result = None


    # Check for comments
    if line.text[colno : colno + 1] == "--":
        result = AssembleResult (AssembleResult.COMMENT)
        result.comment = line.text[colno + 2 :]
        return errors, result

    # Check for empty lines
    if colno == len (line.text):
        result = AssembleResult (AssembleResult.EMPTY)
        return errors, result


    # Process something that we already know to be a keyword and that we hope is an instruction.
    # Emit errors if it's not an instruction.
    
    def assembleInstr ():

        res = AssembleResult (AssembleResult.INSTRUCTION)
        keyword = keywords[word]

        # The first keyword we encounter should be an instruction. Get mad if it's not.
        if type (keyword) != Instr:
            return [mkSyntaxError ("expected instruction")], res

        res.instruction = keyword
        return [], res


    # Get a word starting at colno. It should either be a label or a keyword.
    colno, word = getWord (colno, line)

    if word in keywords:
        errs, result = assembleInstr ()
        errors += errs

    else:

        # This must be a label terminated by a colon.
        # If it is, mark it in the result and try to get the instruction again.
        # If it's not, get mad.
        if line.text[colno] != ":":
            errors += [mkSyntaxError ("expected ':'")]
        colno += 1

        # The assignment of the label kind may be temporary if we end up finding an instruction.
        result = AssembleResult (AssembleResult.LABEL)
        result.label = word

        # If the line ends here with just a label, that's okay.
        if colno == len (line.text):
            return errors, result


        colno, word = getWord (colno, line)

        # If we got a label and the line didn't end, we have no choice now but to get an instruction
        if word in keywords:
            errs, res = assembleInstr ()
            result.kind = res.kind
            result.instruction = res.instruction
            # ^ these last two lines are a bit messy.
            # Maybe consider writing a copy method for AssembleResult.
            errors += errs

        else:
            errors += [mkSyntaxError ("expected instruction")]


    # Get the operands for our instruction depending on their kind

    if result.instruction.operandKind == Instr.IMMEDIATE:
        colno, imm = getImmediate (colno, line)

        if imm == None:
            errors += [mkSyntaxError ("expected immediate value")]

        result.instruction.immediate = imm

    elif result.instruction.operandKind == Instr.REGISTER:
        colno, word = getWord (colno, line)

        if not word in keywords:
            errors += [mkSyntaxError ("expected register")]

        elif type (keywords[word]) != Register:
            errors += [mkSyntaxError ("expected register")]

        else:
            keyword = keywords[word]
            result.instruction.register = keyword.regnum

    return errors, result


# Assemble the entire contents of the file to the abstract representation

def assembleLines (lines : List[str]) -> Tuple[List[AsmErrorInfo], List[AssembleResult]]:

    errors = []
    results = []

    for lineno, text in enumerate (lines):
        line = Line (lineno + 1, text)
        errs, res = assembleLine (line)

        errors += errs
        
        # Only take note of instructions for now
        if res.kind == AssembleResult.INSTRUCTION:
            results += [res]

    return errors, results


import sys

def main ():

    errors = []

    if len (sys.argv) < 2:
        errors += [AsmErrorInfo (AsmError.NO_SOURCE, "no input files given")]

    else:
        filename = sys.argv[1]
        errs, lines = readFile (filename)
        errors += [errs]

        errs, results = assembleLines (lines)
        errors += errs

    for error in errors:
        printError (error)


main ()




