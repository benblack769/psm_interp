import array
from helper import *
import numpy
import sys

def main():
    filename = input("Type File name: ")
    file = open(filename)
    lines = file.readlines()
    
    MainProc(lines)

def MainProc(lines):
    registers = GetRegisters()
    
    FuncPoints = GetFuncPoints(lines)
    
    FuncPoints["input"] = inputfunc
    FuncPoints["print"] = printfunc
    print(FuncPoints)
    if "main" not in FuncPoints:
        raise AssertionError("No main function in assembly code.")
        
    curspot = IntHolder(FuncPoints["main"])
    
    keyword = ""
    Stack = array.array('B')#unsigned char array
    for n in range(StackSize):
        Stack.append(0x00)
    BreakPoints = set()
    CallStack = []
    Conditions = {N:False,Z:False,V:False,C:False}
    LineFns = CreateLineFns(lines,FuncPoints,Stack,registers,Conditions,CallStack,curspot)
    def thisexecute():
        if curspot.num >= len(lines):
            raise AssertionError("End of file reached without return.")
        Fn = LineFns[curspot.num]
        curspot.num += 1#default value, Fn() can still change this
        if Fn != None:
            Fn()
    while keyword != "quit":
        InCode = input()
        CodeChain = InCode.split()
        if len(CodeChain) == 0:
            continue
        else:
            keyword = CodeChain[0]
        if keyword == "step":
            numofsteps = int(CodeChain[1])
            
            for s in range(numofsteps):
                thisexecute()
                if curspot.num in BreakPoints:
                    break
        elif keyword == "run":
            thisexecute()
            while curspot.num not in BreakPoints:
                thisexecute()
        elif keyword == "setbreak":
            breakpoint = int(CodeChain[1])
            BreakPoints.add(breakpoint)
        elif keyword == "removebreak":
            breakpoint = int(CodeChain[1])
            BreakPoints.remove(breakpoint)
        elif keyword == "evaluate":
            Code = InCode[len(keyword):]
            FnL = CreateLineFns([Code],FuncPoints,Stack,registers,Conditions,CallStack,curspot)
            FnL[0]()
        elif keyword == "exec":
            LineNum = int(CodeChain[1])
            LineFns[LineNum]()
        elif keyword == "goto":
            FnName = CodeChain[1]
            curspot.num = FuncPoints[FnName]
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
                print(curspot.num)
            elif showthing == "line_info":
                print(lines[curspot.num])
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
    
    lastchspt = len(instruc) - 1
    size = 0 #useful value for void returns and stuff
    if instruc in AllInstructions:
        return instruc,0
    elif instruc[:lastchspt] in AllInstructions:
        s = instruc[lastchspt]
        if s == 'q':
            size = 8
            instruc = instruc[:lastchspt]
        elif s == 'l':
            size = 4
            instruc = instruc[:lastchspt]
        return instruc,size
    else:
        return NO_INSTRUCT,0

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
    def __init__(self):
        self.size = 8
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

def GetRegisters():
    regs = {name: Register() for name in ORDERED_REGISTERS}
    regs.update({("e"+name[1:]): Register() for name in ORDERED_REGISTERS})
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
    Val = None
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

        if parts[0] == "-":
            offset = -int(parts[1])
        elif parts[0] == "(":#if there is no number
            offset = 0
        else:#if the first part is an integer
            offset = int(parts[0])
        reg = registers[RegStr]
        return lambda : GetValFromStack(size,reg.GetVal() + offset,Stack)
        
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
        
        if parts[0] == "-":
            offset = -int(parts[1])
        elif parts[0] == "(":#if there is no number
            offset = 0
        else:#if the first part is an integer
            offset = int(parts[0])
        reg = registers[RegStr]
        return lambda SetVal : SetStackToVal(size,SetVal,reg.GetVal() + offset,Stack)
        
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
        curspot.num = CallStack.pop()
    #one argument instructions
    def _inc(word,ws):
        return word + 1
    def _dec(word,ws):
        return word - 1
    def _call(word,ws):
        if word == inputfunc:
            inputval = int(input("Please input an integer"))
            SetRegister(inputval,"rax",registers)
        elif word == printfunc:
            print(registers["rdi"].GetVal())
        else:
            CallStack.append(curspot.num)
            curspot.num = word
            
    def _push (word,ws):
        SetStackToVal(ws,word,registers["rsp"].GetVal(),Stack)
        newval = registers["rsp"].GetVal() - ws
        SetRegister(newval,"rsp",registers)#shifts stack pointer
        
    def _pop(word,ws):
        newval = registers["rsp"].GetVal() + ws
        SetRegister(newval,"rsp",registers)#shifts stack pointer
        return GetValFromStack(ws,registers["rsp"].GetVal(),Stack)
    def _jl(word,ws):
        if Conditions[N]:
            curspot.num = word
    def _jg(word,ws):
        if not (Conditions[N] or Conditions[Z]):
            curspot.num = word
    def _jle(word,ws):
        if Conditions[N] or Conditions[Z]:
            curspot.num = word
    def _jge(word,ws):
        if not Conditions[N]:
            curspot.num = word
    def _je(word,ws):
        if Conditions[Z]:
            curspot.num = word
    def _jne(word,ws):
        if not Conditions[Z]:
            curspot.num = word
    def _jmp(word,ws):
        curspot.num = word
    #two argument instructions
    def _mov(w1,w2,ws):
        return w1
    def _add(w1,w2,ws):
        return w2 + w1
    def _sub(w1,w2,ws):
        return w2 - w1
    def _xor(w1,w2,ws):
        return w2 ^ w2
    def _and(w1,w2,ws):
        return w2 & w1
    def _or(w1,w2,ws):
        return w2 | w1
    def _sal(w1,w2,ws):
        return w2 >> w1
    def _sar(w1,w2,ws):
        return w2 << w1
    _shr = _sar
    def _shl(w1,w2,ws):
        return ~((-w2) >> w1)#I think this works but I am not 100% sure
    def _cmp(w1,w2,ws):
        Conditions[N] = (w2 - w1 < 0)
        Conditions[Z] = (w2 - w1 == 0)
    SimpGetGetFn = lambda string,size : GetGetFn(string,size,Stack,registers,FuncPoints)
    SimpGetSetFn = lambda string,size : GetSetFn(string,size,Stack,registers,FuncPoints)
    for line in lines:
        basic_line = DeleteComments(line)
        parts = BreakIntoBasicParts(basic_line)
        
        if parts[0] == None:
            InstrucArgs.append(None)
            continue
        instruc,wordsize = GetSizeOfInstrucAndStrip(parts[0])
        if instruc == NO_INSTRUCT:
            InstrucArgs.append(None)
            continue
        FnName = "_" + instruc
        base_fn = eval(FnName)
        if parts[1] == None:#no argument intructions
            def outfn_overlord(basefn):
                return basefn
            out_fn = outfn_overlord(base_fn)
        elif parts[2] == None:#one argument intruction
            def outfn_overlord(basefn):
                GetWord = SimpGetGetFn(parts[1],wordsize)
                SetWord = SimpGetSetFn(parts[1],wordsize)
                loc_wordsize = wordsize
                def outfn():
                    newval = basefn(GetWord(),loc_wordsize)
                    if newval != None:#if the instruction stores a value
                        SetWord(newval)
                return outfn
            out_fn = outfn_overlord(base_fn)
        else:#three argument instructions
            def outfn_overlord(basefn):
                GetWord1 = SimpGetGetFn(parts[1],wordsize)
                GetWord2 = SimpGetGetFn(parts[2],wordsize)
                SetWord = SimpGetSetFn(parts[2],wordsize)
                loc_wordsize = wordsize
                def outfn():
                    newval = basefn(GetWord1(),GetWord2(),loc_wordsize)
                    if newval != None:#if the instruction stores a value
                        SetWord(newval)
                return outfn
            out_fn = outfn_overlord(base_fn)
            
        InstrucArgs.append(out_fn)
        
    return InstrucArgs

if __name__ == "__main__":
    main()





