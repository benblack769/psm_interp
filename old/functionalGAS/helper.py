#helper modual for AsseblyStepper.py
N = "negative"
Z = "zero"
V = "overflow"
C = "cary"
NO_INSTRUCT = "_NOINST"
StackSize = 1000
inputfunc = -1
printfunc = -2
ORDERED_REGISTERS = [\
"rax",\
"rbx",\
"rcx",\
"rdx",\
"rbp",\
"rsi",\
"rdi",\
"rsp",\
"r8",\
"r9",\
"r10",\
"r11",\
"r12",\
"r13",\
"r14",\
"r15",\
]
class IntHolder(object):
    def __init__(self,num=0):
        self.num = num
def make_raise_assert_fn(message):
    def assertion(mess):
        AssertionError(mess)
    return assertion
    
def IsFunction(line):
    if line.count('"') > 0:#nothing with a quote will be useful, and it could have a colon in it
        return False
    elif line.count(':') > 0:
        return True
    else:
        return False
    
#returns a map of line locations keyed to the function names
def GetFuncPoints(lines):
    FNames = {}
    for lnum in range(len(lines)):
        l = lines[lnum]
        if IsFunction(l):
            #gets the word(s) before the colon without whitespace
            name = l[:l.index(':')].split()
            name = name[0]
            FNames[name] = lnum#converts lnum to user line number, which is one above
            
    return FNames

def DeleteComments(line):#removes the one line comments only!
    def RemoveLineComment(L,com):
        if L.count(com) > 0:
            return L[:L.index(com)]
        else:
            return L
                
    line = RemoveLineComment(line,'#')
    
    return line

def IsWhite(c):
    return c == ' ' or c == '\t'
 
def BreakIntoBasicParts(line):#only handles basic 3 part things right now,real assembly can handle 4
    splitted = line.split()
    #splitted = SplitStrList(splitted, "\t")
    if len(splitted) == 0:
        return(None,None,None)
    instruc = splitted[0]
    remainder = line[line.find(instruc)+len(instruc):]#the stuff after the 
    commacount = remainder.count(',')
    if commacount == 1:
        commaloc = remainder.find(',')
            
        source = remainder[:commaloc]
        dest = remainder[commaloc + 1:]
        
        return (instruc,source, dest)
    elif commacount == 0:
        if len(splitted) == 1:
            return (instruc,None,None)
        else:
            return (instruc,remainder,None)
    else:
        raise AssertionError("Too many commas in line")
    
def SplitStrList(slist,char):
    NewL = []
    for s in slist:
        thisstr = s
        for n in range(s.count(char)):
            if(not thisstr):
                break
            strs = thisstr.partition(char)
            if(strs[0]):
                NewL.append(strs[0])
            if(strs[1]):
                NewL.append(strs[1])

            thisstr = strs[2]
        if(thisstr):
            NewL.append(thisstr)
    return NewL
    
    