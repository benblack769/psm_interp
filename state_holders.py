import copy
import random
from run_core import *

#
#random number generators
#
bit64 = 1 << 64
def rand_int():
    bit63 = (bit64 >> 1)
    return random.randint(-bit63, bit63 - 1)
    
def make_rIP():
    return random.randint(0x1000,0xafff)
    
def make_rSP():
    #guarentees a positive multiple of 8 that is not extremely large
    return (abs(rand_int()) // 16) * 8 
    
#
#global variables
#
start_rIP = make_rIP()

reg_name_list = ["rAX","rBX","rCX","rDX","rSI","rDI","rSP","rBP","rIP"]

'''
The data classes have get and set methods which are used by GUI_interp
to alert the display as to what the instruction is accessing or setting. 
Their current value .val is used directly when signaling the display is 
not desired.
'''
class Const(object):
    def __init__(self,val):
        self.val = int_val(val)
    def get(self):
        return self.val
    def make_x86(self):
        return "$" + str(self.val.int)

class DataSegment(object):
    def __init__(self):
        self.val = unknown_val(rand_int())
        
    def get(self):
        return self.val
        
    def set(self,new_val):
        self.val = copy.deepcopy(new_val)
        
class Register(DataSegment):
    def __init__(self,name):
        self.name = name
        DataSegment.__init__(self)
    def make_x86(self):
        return "%" + self.name

#
#higher level machine classes
#
class Memory(object):
    '''general purpose stack implementation. 
    note that max_size is in terms of the numbers of quadwords, but 
    rSP is in terms of bytes, and is at an offset of start_loc, so it 
    must be converted to its real locaion in the data list.
    '''
    def __init__(self,rSP):
        self.max_size = 500
        self.rSP = rSP
        self.start_loc = make_rSP()
        self.data = [DataSegment() for n in range(self.max_size)]
        
    def check_16byte_stack_alignment(self):
        if (self.rSP.val.int+8 - self.start_loc) % 16 != 0:
            instruc_warnings.add("rSP must be a multiple of 16 from its starting value at times of calls, rands, inputs and outputs on OS X")
                
    def in_bounds(self,n):
        return n > self.start_loc - self.max_size * 8 and n <= self.start_loc and n % 8 == 0
    
    def get(self,loc_ptr):
        if self.in_bounds(loc_ptr.int):
            return self.data[self.ref_to_data(loc_ptr.int)].get()
        else:
            raise StackError(loc_ptr,self)
            
    def set(self,loc_ptr,val):
        if self.in_bounds(loc_ptr.int):
            self.data[self.ref_to_data(loc_ptr.int)].set(val)
        else:
            raise StackError(loc_ptr,self)
            
    def ref_to_data(self,n):
        return (self.start_loc - n) // 8
            
class StackError(Exception):
    def __init__(self,bad_loc,Stack):
        begin = Stack.start_loc
        end = Stack.start_loc - Stack.max_size * 8
        loc = bad_loc.int
        if loc >= begin:
            self.str_rep = "memory accessed " + str(loc - begin) + " bytes before the beginning of the stack."
        elif loc <= end:
            self.str_rep = "memory accessed " + str(end - loc) + " bytes after the end of the stack."
            if end - loc < 2:#if it is barely passed the end of the stack 
                self.str_rep += "\nPerhaps there was too much recursion?"
        elif loc % 8 != 0:
            self.str_rep = "Segmentation fault. \nMemory can only be accessed in 8 bytes chunks counting from the beginning of the stackm"
        
        if type(bad_loc) != stack_ptr_val:
            self.str_rep += "\nPerhaps this is because the pointer originated from an "  + bad_loc.descrip
            
    def __str__(self):
        return self.str_rep
        
class ExitMessage(Exception):
    pass
    
class ProgramState(object):
    '''ProgramState handles gotos and also checks proper returns.
    
    It also handle running, steping and other debugging controll.
    It makes this general purpose across interfaces by handling the 
    core logic of running while letting its subclasses implement 
    overloads for is_not_runnable, upon_break, upon_exit and is_break.
    '''
    def __init__(self,rBP,rIP):      
        self.exprs = []
        self.to_fnum = dict()
        self.next_break = None
        self.rBP = rBP
        self.rIP = rIP
        self.rBP_start = rBP.val.int
        self.parent_rIP = make_rIP()
    #  
    #methods instructions access
    #
    def jmp_to(self,loc,will_jump):
        if type(loc) != instruc_val:
            raise AssemblyRunError("jumped to an invalid location\nonly unaltered values of rIP are valid") 
        elif will_jump:
            self.rIP.val.int = loc.int
            
    def check_proper_return(self):
        if self.rIP.val.int == self.parent_rIP:
            if self.rBP.val.int == self.rBP_start:
                raise ExitMessage()
            else:
                raise AssemblyRunError("Program exited with rBP != the starting rBP")
        elif not (0 <= self.rIP.val.int - start_rIP < len(self.exprs)):
            raise AssemblyRunError("rIP returned to invalid locatino (this should not actually be possible!)")
    #
    #interface specific functions
    #
    def is_not_runnable(self):
        return False
    def upon_break(self):
        return
    def upon_exit(self):
        return
    def is_break(self):
        return False
    #
    #increments isntruction pointer, evaluates, and handles warnings and exceptions
    #
    def poke(self):
        cur_instruc = self.rIP.val.int
        
        f_line_num = self.to_fnum[cur_instruc] + 1
        
        expr = self.exprs[cur_instruc - start_rIP]
        self.rIP.val.int += 1
        
        try:
            expr.eval()
            instruc_val = self.rIP.val.int
            if instruc_val - start_rIP == len(self.exprs):
                raise AssemblyRunError("reached end of file without return")
        except ExitMessage:
            return True
        except AssemblyRunError as ae:
            handle_run_exception(f_line_num,ae)
            return True
        except StackError as se:
            handle_run_exception(f_line_num,se)
            return True
        else:
            handle_run_warnings(f_line_num)
            return False
    
    #
    #debugging flow control
    #
    def run(self):
        if self.is_not_runnable():
            return
            
        if self.poke():
            self.upon_exit()
            return
        
        while(True):
            if self.is_break():
                self.upon_break()
                return
                
            if self.poke():
                self.upon_exit()
                return
            
    def next(self):
        if self.is_not_runnable():
            return
        instruc = self.rIP.val.int
        evalfn = self.exprs[instruc - start_rIP]
        
        if evalfn.__class__.__name__ == "Call":
            self.next_break = self.rIP.val.int + 1
            self.run()
            self.next_break = None
        else:
           self.step()
        
    def step(self):
        if self.is_not_runnable():
            return
            
        if self.poke():
            self.upon_exit()
            return
            
        self.upon_break()
   