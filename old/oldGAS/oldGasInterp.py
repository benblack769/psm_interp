import array
from oldhelp import *
import numpy
import sys
def main():
    filename = input("Type File name: ")
    file = open(filename)
    lines = file.readlines()
    
    lines = DeleteComments(lines)
    
    for lnum in range(len(lines)):
        lines[lnum] = lines[lnum].lower()
    
    FuncPoints = GetFuncPoints(lines)
    
    lines,LineMap = RemoveEmptyLinesAndMapLines(lines)
    
    FuncPoints = {k : LineMap[v] for k,v in FuncPoints.items()}
    FuncPoints["input"] = inputfunc
    FuncPoints["print"] = printfunc
    
    MainProc(FuncPoints,lines,LineMap)
                
def MainProc(FuncPoints,lines,LineMap):
    registers = GetRegisters(lines)
    
    RevLineMap = {v: k for k, v in LineMap.items()}

    if "main" not in FuncPoints:
        raise AssertionError("No main function in assembly code, exiting.")
    curspot = FuncPoints["main"]
    
    keyword = ""
    Stack = array.array('B')#unsigned char array
    for n in range(StackSize):
        Stack.append(0)
    BreakPoints = set()
    CallStack = []
    Conditions = {N:False,Z:False,V:False,C:False}
    def thisexecute(line,thisspot):
        if thisspot >= len(lines):
            raise AssertionError("End of file reached without return.")
        return Execute(line,FuncPoints,Stack,registers,Conditions,CallStack,thisspot)
    while keyword != "quit":
        InCode = input()
        CodeChain = InCode.split()
        if len(CodeChain) == 0:
            continue
        else:
            keyword = CodeChain[0]
        if keyword == "step":
            numofsteps = int(CodeChain[1])
            curspot = thisexecute(lines[curspot],curspot)
            for s in range(numofsteps-1):
                if curspot in BreakPoints:
                    break
                curspot = thisexecute(lines[curspot],curspot)
        elif keyword == "run":
            curspot = thisexecute(lines[curspot],curspot)
            while curspot not in BreakPoints:
                curspot = thisexecute(lines[curspot],curspot)
        elif keyword == "setbreak":
            breakpoint = LineMap[int(CodeChain[1])]
            BreakPoints.add(breakpoint)
        elif keyword == "removebreak":
            breakpoint = LineMap[int(CodeChain[1])]
            BreakPoints.remove(breakpoint)
        elif keyword == "goto":
            FnName = CodeChain[1]
            curspot = FuncPoints[FnName]
        elif keyword == "execute":
            LineWord = InCode[7:]
            curspot = Execute(LineWord,FuncPoints,Stack,registers,Conditions,CallStack,curspot-1)
        elif keyword == "show":
            showthing = CodeChain[1]
            if showthing == "registers":
                PrintRegs(registers)
            elif showthing == "memory":
                PrintMem(Stack,registers["rsp"].GetVal())
            elif showthing == "breakpoints":
                for b in BreakPoints:
                    print(RevLineMap[b])
            elif showthing == "curline":
                print(RevLineMap[curspot])
            elif showthing == "line_info":
                print(RevLineMap[curspot])
            elif showthing == "bit_registers":
                print(Conditions)
            elif showthing == "callstack":
                for LNum in CallStack:
                    print(RevLineMap[LNum])
        else:
            print("Keyword not known")

def GetSizeOfInstrucAndStrip(instruc):
    AllInstructions = frozenset([ \
    "add","sub","imu","mov",\
    "sal","sar","shl","shr"\
    "or","xor","and",\
    "inc","dec",\
    "call","ret",\
    "push","pop",\
    "cmp",\
    "je","jg","jge","jl","jle","jmp","jne"])
    
    lastchar = len(instruc) - 1
    s = instruc[lastchar]
    size = 0 #useful value for void returns and stuff
    if instruc in AllInstructions:
        return instruc,0
    elif instruc[:lastchar] in AllInstructions:
        if s == 'q':
            size = 8
            instruc = instruc[:lastchar]
        elif s == 'l':
            size = 4
            instruc = instruc[:lastchar]
        return instruc,size
    else:
        raise AssertionError("Instruction: " + instruc + " not known in line ")

def ToNumpy(word,size):
    word = int(word)
    if size == 4:
        Convert = numpy.int32
        UnsignedScreen = 0x7fffffff
    elif size == 8:
        Convert = numpy.int64
        UnsignedScreen = 0x7fffffffffffffff
        
    SignScreen = UnsignedScreen + 1
    val = Convert(word & UnsignedScreen)#gets the unsigned bits
    halfsignbitval = Convert((word & SignScreen)/2)
    val += halfsignbitval * 2
    
    return val
    
class Register(object):
    def __init__(self,size):
        self.size = size
        if size == 4:
            self._val = numpy.int32(0)
        elif size == 8:
            self._val = numpy.int64(0)
    def __str__(self):
        string = ""
        val = int(self._val)
        
        for x in range(self.size * 2):
            Part1 = hex(val & 0xf)
            string += Part1[2:]#cuts off the Ox
            val >>= 4
            
        return "0x" + string[::-1]#puts the Ox back on and flips the value over
    def SetValue(self,val):
        #makes sure the size stays insize the bounds
        self._val = ToNumpy(val,self.size)
    def SetValInSize(self,val,ValSize):
        #trust me that this works, and don't change anything
        if ValSize >= self.size:
            self.SetValue(val)
        else:#this means that self.size is 8 and ValSize is 4
            self.SetValue((int(self._val) & 0xffffffff00000000) | (val & 0xffffffff))
    def GetVal(self):
        return self._val

def GetRegisters(lines):
    regs = dict()
    regs["eax"] = Register(4)
    regs["ebx"] = Register(4)
    regs["ecx"] = Register(4)
    regs["edx"] = Register(4)
    regs["ebp"] = Register(4)
    regs["esi"] = Register(4)
    regs["edi"] = Register(4)
    regs["esp"] = Register(4)
    
    regs["rax"] = Register(8)
    regs["rbx"] = Register(8)
    regs["rcx"] = Register(8)
    regs["rdx"] = Register(8)
    regs["rbp"] = Register(8)
    regs["rsi"] = Register(8)
    regs["rdi"] = Register(8)
    regs["rsp"] = Register(8)
    
    regs["r8"] = Register(8)
    regs["r9"] = Register(8)
    regs["r10"] = Register(8)
    regs["r11"] = Register(8)
    regs["r12"] = Register(8)
    regs["r13"] = Register(8)
    regs["r14"] = Register(8)
    regs["r15"] = Register(8)
    
    return regs

def SetRegister(val,regname,registers):
    changereg = registers[regname]
    changereg.SetValue(val)
    #changes the namelikes (like rax and eax) of changedreg to its value
    for name,reg in registers.items():
        if name[1:] == regname[1:]:
            reg.SetValInSize(val,changereg.size)#specialized setval that does not change more bytes than the size of the value

def PrintRegs(regs):
    for name,reg in regs.items():
        print("%" + name + "\t" + str(reg))

def PrintMem(Stack,stackptrval):
    string = ""
    for n in range(StackSize-1,StackSize-1 + stackptrval,-1):
        s = hex(Stack[n])
        if len(s) == 3:#it should be 4
            string += "0"
        string += s[2:]
    print("0x" + string)

def SetStackToVal(Size,Val,Spot,Stack):
    for x in range(Size):
        Stack[StackSize-8 + Spot + x] = (Val >> (x*8)) & 0xff

def GetValFromStack(Size,Spot,Stack):
    if Size == 4:
        Val = numpy.int32(0)
        for x in range(Size):
            Val += numpy.int32(Stack[StackSize-8 + Spot + x]) << (x*8)
    elif Size == 8:
        Val = numpy.int64(0)
        for x in range(Size):
            Val += numpy.int64(Stack[StackSize-8 + Spot + x]) << (x*8)
    return Val
    
def GetGetFn(string,size,Stack,registers,FuncPoints):
    parts = string.split()
    parts = SplitStrList(parts,")")
    parts = SplitStrList(parts,"(")
    parts = SplitStrList(parts,"-")
    parts = SplitStrList(parts,"$")
    parts = SplitStrList(parts,"%")
    
    if parts.count("(") > 0:#If there is a parenthasis, then it is a memory value
        #there should only be one parenthasis in parts
        RegStr = parts[parts.index("(") + 2]#one for the % sign, one for the Paren
        
        Pointer = registers[RegStr].GetVal()

        if parts[0] == "-":
            offset = -int(parts[1])
        elif parts[0] == "(":#if there is no number
            offset = 0
        else:#if the first part is an integer
            offset = int(parts[0])

        spot = offset + Pointer
        return lambda : GetValFromStack(size,spot,Stack)
        
    elif parts[0] == "$":#it is a static value
        numpy_val = ToNumpy(int(parts[1]),size)
        return lambda : numpy_val
        
    elif parts[0] in FuncPoints:
        line_num = FuncPoints[parts[0]]
        return lambda : line_num
    else:#it is a register
        #parts[0] will be the % marker
        regname = parts[1]
        return lambda : registers[regname].GetVal()
        
def GetSetFn(string,size,Stack,registers,FuncPoints):
    parts = string.split()
    parts = SplitStrList(parts,")")
    parts = SplitStrList(parts,"(")
    parts = SplitStrList(parts,"-")
    parts = SplitStrList(parts,"$")
    parts = SplitStrList(parts,"%")
    
    if parts.count("(") > 0:#If there is a parenthasis, then it is a memory value
        #there should only be one parenthasis in parts
        RegStr = parts[parts.index("(") + 2]#one for the % sign, one for the Paren
        
        Pointer = registers[RegStr].GetVal()
        
        if parts[0] == "-":
            offset = -int(parts[1])
        elif parts[0] == "(":#if there is no number
            offset = 0
        else:#if the first part is an integer
            offset = int(parts[0])
            
        spot = offset + Pointer
        return lambda SetVal : SetStackToVal(size,SetVal,spot,Stack)
        
    elif parts[0] == "$":#it is a static value
        return make_raise_assert_fn("Static Values cannot be used there!")
        
    elif parts[0] in FuncPoints:
        return make_raise_assert_fn("Jumps doe not change any values!!!")#if it is a function call, then it doesn't change anything
    else:#it is a register
        #parts[0] will be the % marker
        regname = parts[1]
        return lambda SetVal : SetRegister(SetVal,regname,registers)

def CreateLineFns(lines,FuncPoints,Stack,registers,Conditions,CallStack,curspot):
    InstrucArgs = []
    #no argument instructions
    def _ret():
        if instruc == "ret":
            curspot.num = CallStack.pop()
    #one argument instructions
    def _inc(word):
        return word + 1
    def _dec(word):
        return word - 1
    def _call(word):
        if word == inputfunc:
            inputval = int(input("Please input an integer"))
            SetRegister(inputval,"rax",registers)
        elif word == printfunc:
            print(registers["rdi"].GetVal())
        else:
            CallStack.append(curspot.num)
            curspot.num = word
            
    def _push(word):
        SetStackToVal(wordsize,word,registers["rsp"].GetVal(),Stack)
        newval = registers["rsp"].GetVal() - wordsize
        SetRegister(newval,"rsp",registers)#shifts stack pointer
        
    def _pop(word):
        newval = registers["rsp"].GetVal() + wordsize
        SetRegister(newval,"rsp",registers)#shifts stack pointer
        return GetValFromStack(wordsize,registers["rsp"].GetVal(),Stack)
    def _jl(word):
        if(Conditions[N]):
            curspot.num = word
    def _jg(word):
        if(not (Conditions[N] or Conditions[Z])):
            curspot.num = word
    def _jle(word):
        if(Conditions[N] or Conditions[Z]):
            curspot.num = word
    def _jge(word):
        if(not Conditions[N]):
            curspot.num = word
    def _je(word):
        if(Conditions[Z]):
            curspot.num = word
    def _jne(word):
        if(not Conditions[Z]):
            curspot.num = word
    def _jmp(word):
        curspot.num = word
    #two argument instructions
    def _mov(w1,w2):
        return w1
    def _add(w1,w2):
        return w2 + w1
    def _sub(w1,w2):
        return w2 - w1
    def _xor(w1,w2):
        return w2 ^ w2
    def _and(w1,w2):
        return w2 & w1
    def _or(w1,w2):
        return w2 | w1
    def _sal(w1,w2):
        return w2 >> w1
    def _sar(w1,w2):
        return w2 << w1
    _shr = _sar
    def _shl(w1,w2):
        return ~((-w2) >> w1)#I think this works but I am not 100% sure
    def _cmp(w1,w2):
        Conditions[N] = (w2 - w1 < 0)
        Conditions[Z] = (w2 - w1 == 0)
    SimpGetGetFn = lambda string : GetGetFn(string,size,Stack,registers,FuncPoints)
    SimpGetSetFn = lambda string : GetSetFn(string,size,Stack,registers,FuncPoints)
    for line in lines:
        parts = BreakIntoBasicParts(line)
        instruc,wordsize = GetSizeOfInstrucAndStrip(parts[0])
        FnName = "_" + instruc
        base_fn = eval(FnName)
        if parts[1] == None:#no argument intructions
            out_fn = base_fn
        elif parts[2] == None:#one argument intructions
            GetWord = SimpGetGetFn(parts[1])
            SetWord = SimpGetSetFn(parts[1])
            def outfn():
                newval = base_fn(GetWord())
                if newval != None:#if the instruction stores a value
                    SetWord(newval)
            out_fn = outfn
        else:#three argument instructions
            GetWord1 = SimpGetGetFn(parts[1])
            GetWord2 = SimpGetGetFn(parts[2])
            SetWord = SimpGetSetFn(parts[2])
            def outfn():
                newval = base_fn(GetWord1(),GetWord2())
                if newval != None:#if the instruction stores a value
                    SetWord(newval)
            out_fn = outfn
        
        InstrucArgs.append(out_fn)
    return InstrucArgs
    
def Execute(line,FuncPoints,Stack,registers,Conditions,CallStack,curspot):
    parts = BreakIntoBasicParts(line)
    
    curspot += 1#default value, jumping will change to other values
    
    instruc,wordsize = GetSizeOfInstrucAndStrip(parts[0])
    
    if parts[1] == None:#no argument intructions
        if instruc == "ret":
            curspot = CallStack.pop()

    elif parts[2] == None:#one argument intructions
        word = GetGetFn(parts[1],wordsize,Stack,registers,FuncPoints)()
        
        if instruc == "inc":
            word += 1
        elif instruc == "dec":
            word -= 1
        elif instruc == "call":
            if word == inputfunc:
                inputval = int(input("Please input an integer"))
                SetRegister(inputval,"rax",registers)
            elif word == printfunc:
                print(registers["rdi"].GetVal())
            else:
                CallStack.append(curspot)
                curspot = word
        elif instruc == "push":
            SetStackToVal(wordsize,word,registers["rsp"].GetVal(),Stack)
            newval = registers["rsp"].GetVal() - wordsize
            SetRegister(newval,"rsp",registers)#shifts stack pointer
        elif instruc == "pop":
            newval = registers["rsp"].GetVal() + wordsize
            SetRegister(newval,"rsp",registers)#shifts stack pointer
            word = GetValFromStack(wordsize,registers["rsp"].GetVal(),Stack)
        elif (instruc == "jl" and Conditions[N]) \
        or (instruc == "jg" and not (Conditions[N] or Conditions[Z])) \
        or (instruc == "jle" and (Conditions[N] or Conditions[Z])) \
        or (instruc == "jge" and not Conditions[N]) \
        or (instruc == "je" and Conditions[Z]) \
        or (instruc == "jne" and not Conditions[Z]) \
        or (instruc == "jmp"):
            curspot = word
            
        GetSetFn(parts[1],wordsize,Stack,registers,FuncPoints)(word)
    else:   
        word1 = GetGetFn(parts[1],wordsize,Stack,registers,FuncPoints)()
        word2 = GetGetFn(parts[2],wordsize,Stack,registers,FuncPoints)()
        if instruc == "mov":
            word2 = word1
        elif instruc == "add":
            word2 += word1
        elif instruc == "sub":
            word2 -= word1
        elif instruc == "imu":
            word2 *= word1
        elif instruc == "xor":
            word2 ^= word1
        elif instruc == "and":
            word2 &= word1
        elif instruc == "or":
            word2 |= word1
        elif instruc == "sal":
            word2 >>= word1
        elif instruc == "sar":
            word2 <<= word1
        elif instruc == "shl":
            #blocks out the arithmetic shift adding of extra ones
            if word2 < 0:
                word2 = (word2 >> word1) ^ ((1<<(wordsize*8-1) >> word1) << 1)
            else:
                word2 >>= word1
        elif instruc == "shr":
            word2 <<= word1
        elif instruc == "cmp":
            Conditions[N] = (word2 - word1 < 0)
            Conditions[Z] = (word2 - word1 == 0)
            
        GetSetFn(parts[2],wordsize,Stack,registers,FuncPoints)(word2)
        
    return curspot
main()





