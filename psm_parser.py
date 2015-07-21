from instructions import *
import re
import operator
import sys

class PsmSyntaxError(Exception):
    def __init__(self,String):
        self.string = String
    def __str__(self):
        return self.string
#
#tokenizer helpers
#
def remove_comment(line):
    if '#' in line:
        return line[:line.index('#')]
    else:
        return line
        
def split_all(L,char):
    newL = []
    for w in L:
        newL += w.split(char)
    return newL
    
all_ops = ["\n"," ","\t",":","++","--","+=","-=","&=","|=","^=",">>=","<<=","*=","/=","%=","[","]","<=",">=","==","!=","<",">","=","-","~","+","-"]
def split_operators(S):
    for op in all_ops:
        if op in S:
            op_loc = S.index(op)
            begining = split_operators(S[:op_loc])
            end = split_operators(S[op_loc + len(op):])
            if op.isspace():
                return begining + end
            else:
                return begining + [op] + end
    if S:
        return [S]
    else:
        return []

def is_label(tokens):
    return len(tokens) == 2 and tokens[1] == ":"
    
def tokenize(line):
    new_line = remove_comment(line)
    tokens = split_operators(new_line)
    if len(tokens) == 0:
        return []
    if not new_line[0].isspace() and is_label(tokens) or \
        not is_label(tokens) and ((line[0] == "\t" and not line[1].isspace()) \
        or (len(line) > 4 and line[:4] == "    " and not line[5].isspace())):
        return tokens
    else:
        raise PsmSyntaxError('''line intiated incorrectly.
Expected either no spaces followed by a label followed by a single colon,
or 4 spaces or a tab followed by an instruction''')


#general purpose PsmSyntaxError used in many places
NO_MATCH = PsmSyntaxError("line does not match any patterns")

def is_word(word):
    #checks if it is composed of only letters, numbers, and underscores
    return bool(re.match(r"[a-zA-Z0-9_]+$",word))
    
def parse_line(tokens,line_num,registers,label_locs,State,Console,Stack):
    try:
        result = parse_instruc(tokens,line_num,registers,label_locs,State,Console,Stack)
        #if there are tokens left over that means that there is extra stuff at the end which is an error
        if tokens:
            raise PsmSyntaxError("Junk at end of expression")
        return result
    except IndexError:
        #this means that the instruction is missing tokens
        raise NO_MATCH
        
def parse_label(tokens,line_num,label_locs):
    label = tokens[0]
    if not is_word(label):
        raise PsmSyntaxError("Label has bad charachters")
    elif label[0].isdigit():
        raise PsmSyntaxError("Label needs to start with a letter")
    elif label in label_locs:
        raise PsmSyntaxError("Ambiguity: this label matches the label on another line.\nLabels must be unique")
    elif label in {"input","print","_input","_print"}:
        raise PsmSyntaxError("Reserved label")
    else:
        label_locs[label] = line_num
        
#
#helpers for parse_instruction
#

def is_in_size(max_size,num):
    return num > (1 << (max_size-1)) - 1 or  num < -(1 << (max_size-1))
    
def is_int(num_str):
    try:
        if num_str[:2] == "0x":
            int(num_str,16)
        else:
            int(num_str)
    except ValueError:
        return False
    else:
        return True
        
def parse_int(max_size,num_str,operator="+"):
    try:
        if num_str[:2] == "0x":
            num = int(num_str,16)
        else:
            num = int(num_str)
    except ValueError as ve:
        raise PsmSyntaxError("Bad constant")
        
    if operator == "-":
        num = -num
    elif operator == "+":
        num = num
    else:
        raise PsmSyntaxError("Bad constant operator")
        
    if is_in_size(max_size,num):
        raise PsmSyntaxError("Constant greater than size of: " + str(max_size) + " bits.")
    else:
        return Const(num)
        
def parse_shift_int(tokens):
    num_str = tokens.pop(0)
    if num_str == "-":
        raise PsmSyntaxError("shift bit instructions only take positive numbers")
    return parse_int(7,num_str)

def parse_reg(Reg,registers):
    if Reg == "rIP":
        raise PsmSyntaxError("rIP cannot be used in ordinary instructions!")
    elif Reg not in registers:
        raise PsmSyntaxError("invalid register name: " + Reg)
    else:
        return registers[Reg]
        
def parse_reg_const(tokens,max_size,registers,*args):
    for tok in args:
        tokens.insert(0,tok)
        
    first = tokens.pop(0)
    if first == "-" or first == "+":
        Op = first
        const = tokens.pop(0)
        return parse_int(max_size,const,Op)
    else:
        Str = first
        if is_int(Str):
            return parse_int(max_size,Str)
        else:
            return parse_reg(Str,registers)
         
def parse_mem_block(tokens,registers):
    mem_loc = tokens[1]
    
    if tokens[0] == "[":
        if tokens[2] == "+" or tokens[2] == "-":
            offset = tokens[3]
            if tokens[4] == "]":
                operator = tokens[2]
                const = parse_int(32,offset,operator)
                for i in range(5):
                    tokens.pop(0)
                return (parse_reg(mem_loc,registers),const)
        elif tokens[2] == "]":
            for i in range(3):
                tokens.pop(0)
            return (parse_reg(mem_loc,registers),Const(0))
            
    raise NO_MATCH

def parse_operator(tokens):
    opstr = tokens.pop(0)
    if opstr == "<":
        return operator.lt
    elif opstr == ">":
        return operator.gt
    elif opstr == "<=":
        return operator.le
    elif opstr == ">=":
        return operator.ge
    elif opstr == "==":
        return operator.eq
    elif opstr == "!=":
        return operator.ne
            
    raise PsmSyntaxError("bad operator: " + opstr)

def parse_label_ref(tokens,label_locs):
    label = tokens.pop(0)
    if label in label_locs:
        return label
    else:
        raise PsmSyntaxError("Bad label")
       
def parse_instruc(tokens,line_num,registers,label_locs,State,Console,Stack):
    """
    Builds and returns the instruction that the line signals, or 
    raises an exception. It pops symbols off of the front of the 
    token list and if there is nothing left to pop off it throws an 
    error which is translated into a PsmSyntaxError by parse_line.
    Note that parse_something functions pop items off of the token list
    in a stateful change if they accept "tokens" as an argument.
    If there are any tokens left after this function returns, that 
    is also a PsmSyntaxError.
    """
    def parse_src(tokens):
        return parse_reg_const(tokens,32,registers)
    def parse_dest_reg(Reg):
        return parse_reg(Reg,registers)
        
    rSP = registers["rSP"]
    
    first = tokens.pop(0)
    if first in registers:
        first_op = tokens.pop(0)
        if first_op == "=":
            word2 = tokens.pop(0)
            if word2 == "-" or word2 == "~":
                reg2 = tokens.pop(0)
                if reg2 == first:#the source and destination registers are required to be the same
                    if word2 == "-":
                        return Neg(parse_dest_reg(first))
                    elif word2 == "~":
                        return Not(parse_dest_reg(first))
                elif is_int(reg2) and word2 == "-":
                    return Mov(parse_dest_reg(first),parse_int(64,reg2,"-"))
                else:
                    raise PsmSyntaxError("negation and bitwise not must have the same register on both sides of the '=' sign")
            elif word2 == "in":
                return Input(parse_dest_reg(first),Console,Stack)
            elif word2 == "rand":
                return Random(parse_dest_reg(first),Stack)
            elif word2 == "mem":
                (mem_loc,offset) = parse_mem_block(tokens,registers)
                return MemLoad(parse_dest_reg(first),Stack,mem_loc,offset)
            elif word2 == "pop":
                return Pop(parse_dest_reg(first),rSP,Stack)
            else:
                return Mov(parse_dest_reg(first),parse_reg_const(tokens,64,registers,word2))
        elif first_op == "++":
            return Inc(parse_dest_reg(first))
        elif first_op == "--":
            return Dec(parse_dest_reg(first))
        elif first_op == "+=":
            return Add(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "-=":
            return Sub(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "&=":
            return And(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "|=":
            return Or(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "^=":
            return Xor(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "*=":
            return Mul(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "/=":
            return Div(parse_dest_reg(first),parse_src(tokens))
        elif first_op == "%=":
            return Rem(parse_dest_reg(first),parse_src(tokens))
        elif first_op == ">>=":
            return SAR(parse_dest_reg(first),parse_shift_int(tokens))
        elif first_op == "<<=":
            return SAL(parse_dest_reg(first),parse_shift_int(tokens))
    elif first == "push":
        return Push(parse_src(tokens),rSP,Stack)
    elif first == "mem":
        (dest_reg,offset) = parse_mem_block(tokens,registers)
        if tokens.pop(0) == "=":
            return MemStore(parse_src(tokens),Stack,dest_reg,offset)
    elif first == "out":
        return Output(parse_src(tokens),Console,Stack)
    elif first == "goto":
        label = parse_label_ref(tokens,label_locs)
        return GoTo(label,label_locs[label],State)
    elif first == "if":
        cmpA = parse_src(tokens)
        if type(cmpA) == Const:
            raise PsmSyntaxError("Left side of comparision must be a register.")
        op = parse_operator(tokens)
        cmpB = parse_src(tokens)
        if tokens.pop(0) == "goto":
            label = parse_label_ref(tokens,label_locs)
            return Cond_jump(cmpA,cmpB,op,label,label_locs[label],State)
    elif first == "call":
        label = parse_label_ref(tokens,label_locs)
        return Call(label,label_locs[label],line_num,rSP,Stack,State)
    elif first == "return":
        return Return(rSP,Stack,State)
        
    #if it has not returned then it has not met any of the matches
    raise NO_MATCH
    
def parse_all(lines,registers,State,Console,Stack):
    label_locs = dict()
    Has_Errors = False
    com_n = start_rIP
    
    def handle_error(n,Err):
        print("on line: ",n + 1,".")
        print("syntax error: ",ErrStr,"\n")
        
    #puts the labels in the file into label_locs
    #indexing is by the rIP value, not the file line
    for n,l in enumerate(lines):
        try:
            tokens = tokenize(l)
            if is_label(tokens):
                parse_label(tokens,com_n,label_locs)
            elif tokens:
                com_n += 1
        except PsmSyntaxError as ErrStr:
            handle_error(n,ErrStr)
            Has_Errors = True
            
    if "main" not in label_locs:
        print("No main function in code, stopping parsing.")
        sys.exit(0)
    
    compiled_lines = []
    comp_to_file = dict()
    
    #parses the instructions
    for n,l in enumerate(lines):
        try:
            tokens = tokenize(l)
            if tokens and not is_label(tokens):
                comp_n = len(compiled_lines) + start_rIP
                comp_to_file[comp_n] = n
                compiled_lines.append(parse_line(tokens,comp_n,registers,label_locs,State,Console,Stack))
        except PsmSyntaxError as ErrStr:
            handle_error(n,ErrStr)
            Has_Errors = True
            
    if Has_Errors:
        print("Errors found in parsing")
        sys.exit(0)
    
    if not compiled_lines:
        print("File has to have instructions in it!")
        sys.exit(0)
    
    return label_locs,compiled_lines,comp_to_file
    