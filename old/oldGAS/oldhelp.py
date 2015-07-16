#helper modual for AsseblyStepper.py
N = "negative"
Z = "zero"
V = "overflow"
C = "cary"
StackSize = 100000
inputfunc = -1
printfunc = -2
class IntHolder(object):
    def __init__(self,num=0):
        self.int = num
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
            FNames[name] = lnum + 1#converts lnum to user line number, which is one above
            
    return FNames
    
   
def DeleteComments(lines):#removes the one line comments only!
    def RemoveLineComment(com):
        for l in range(len(lines)):
            line = lines[l]
            if line.count(com) > 0:
                lines[l] = line[:line.index(com)]
                
    RemoveLineComment('#')
    RemoveLineComment(';')
    RemoveLineComment('//')
    
    return lines

def RemoveEmptyLinesAndMapLines(lines):
    new = []
    LineMap = dict()
    for lnum in range(len(lines)):
        l = lines[lnum]
        
        LineMap[lnum+1] = len(new)#line numbers start at 1 for user, 0 for computer
        
        if len(l.split()) > 0 and not IsFunction(l):#if it has any non-whitespace and is not a function
            new.append(l)
            
    return new,LineMap

def RemoveFunctionCalls(lines):
    new = []
    for l in lines:
        Fn = False
        for c in l:
            if c == '"':#nothing with a quote will be useful, and it could have a colon in it
                break
            elif c == ':':
                Fn = True
        if not Fn:
            new.append(l)

def IsWhite(c):
    return c == ' ' or c == '\t'
 
def BreakIntoBasicParts(line):#only handles basic 3 part things right now
    splitted = line.split()
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
    
    