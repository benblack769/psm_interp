import sys
import platform_check
from state_holders import *

def init_all(regs,mem,state,label_locs,expressions,to_fnum):
    #initializes registers and stack with random values that are unknown to programmer
    for name,reg in regs.items():
        reg.val = unknown_val(rand_int())
    for ml in mem.data:
        ml.val = unknown_val(rand_int())
        
    #rSP starts out pointing to the start of the stack
    regs["rSP"].val = stack_ptr_val(mem.start_loc)
    
    #rBP starts out some ways above the start of the stack, indicating that whatever called "main" is another function
    regs["rBP"].val = stack_ptr_val(mem.start_loc + 2500)
    state.rBP_start = regs["rBP"].val.int
    
    #rIP starts at the loction of "main"
    regs["rIP"].val = instruc_val(label_locs["main"])
    #the caller of "main" is a function in an arbitrary memory location
    state.parent_rIP = start_rIP - 500
    #the location of the caller will have been pushed onto the stack when it called main
    #when return is called, this value will be poped off of the stack, and will give back controll to the parent, exiting the program
    mem.data[0].val = instruc_val(state.parent_rIP)
    
    #this part of init does not have to happen upon a reset, so it is optional
    state.exprs = expressions
    state.to_fnum = to_fnum
    


#main script that executes on all interfaces
this_own_filename,filename = sys.argv
if filename[filename.rindex("."):] != ".psm":
    print("Interpreted file must be a .psm file")
    sys.exit(0)
    
file = open(filename)
flines = file.readlines()
file.close()