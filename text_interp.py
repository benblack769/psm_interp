from interp_core import *
import psm_parser

class TextRegister(Register):
    def represent(self):
        print(self.name + " = " + self.val.to_str(False))

class TextMemory(Memory):
    def represent(self,n):
        if self.in_bounds(rSP.val.int):
            endn = self.ref_to_data(rSP.val.int)
        else:
            endn = self.max_size
        for n in range(0, endn):
            print(int(self.data[n]))
            
class TextConsole(object):
    def print_val(self,val):
        print(val.int)
    def place_input_into(self,input_reg):
        input_reg.set(int_val(truncate(int(input("? ")))))
    
class TextState(ProgramState):
    def __init__(self,*args):
        ProgramState.__init__(self,*args)
        self.breaks = set()
    def upon_exit(self):
        restart()
    def is_break(self):
        instruc = self.rIP.val.int
        return instruc in self.breaks or instruc == self.next_break

    
regs = {name:TextRegister(name) for name in reg_name_list}
mem = TextMemory()
state = TextState(regs["rBP"],regs["rIP"])

cons = TextConsole()
label_locs,exprs,to_fnum = psm_parser.parse_all(flines,regs,state,cons,mem)

init_all(regs,mem,state,label_locs,exprs,to_fnum)

to_unum = {inum:fnum + 1 for inum,fnum in to_fnum.items()}
to_inum = {unum:inum for inum,unum in to_unum.items()}
      
def restart():
    init_all(regs,mem,state,label_locs,exprs,to_fnum)

restart()

keyword = ""
while keyword != "quit":
    InCode = input()
    CodeChain = InCode.split()
    if len(CodeChain) == 0:
        continue
    else:
        keyword = CodeChain[0]
    if keyword == "step":
        state.step()
    elif keyword == "next":
        state.next()
    elif keyword == "run":
        state.run()
    elif keyword == "restart":
        restart()
    elif keyword == "clear":
        state.breaks.clear()
    elif keyword == "break":
        breakpoint = int(CodeChain[1])
        state.breaks.add(to_inum[breakpoint])
    elif keyword == "delete":
        breakpoint = int(CodeChain[1])
        state.breaks.remove(to_inum[breakpoint])
    elif keyword == "print":
        showthing = CodeChain[1]
        if showthing == "mem":
            if len(CodeChain) == 1:
                mem.represent()
            elif showthing in reg_name_list:
                if len(CodeChain) == 2:
                    state.mem.invalid
        elif showthing == "breakpoints":
            for b in state.breaks:
                print(b)
        elif showthing == "line":
            print(to_unum[state.rIP.val.int])
            print(flines[to_fnum[state.rIP.val.int]])
        else:
            print('"print" keyword expects register name\n or memory location as compared to the top of the stack or\n"stack_frame"')
    else:
        print("Keyword not known")
        