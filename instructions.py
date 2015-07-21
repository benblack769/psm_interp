from run_core import *
from state_holders import *
import operator
import math
import platform_check
import random
#
#x86 maker helpers
#
def make_x86(inst,Str1 = None,Str2 = None):
    x86_str = "    " + inst
    if Str1 != None:
        x86_str += " " * (12 - len(x86_str)) + Str1 #makes sure everything lines up
    if Str2 != None:
        x86_str += "," + Str2
    
    x86_str += " " * (38 - len(x86_str))
    return x86_str
    
def make_value(reg):
    return reg.make_x86()
    
def make_offset(reg,off=Const(0)):
    offint = off.val.int
    offstr = ""
    if offint != 0:
        offstr = str(offint)
    return offstr + "(" + reg.make_x86() + ")"
    
def make_lit(lit):
    return "$"+str(lit)
    
def make_div(src,dest,return_mod):
    #x86 implementation for Div and Rem
    is_rax = dest.make_x86() == "%rAX"
    is_rdx = dest.make_x86() == "%rDX"
    
    this_str = ""
    if not is_rax:
        this_str += make_x86("pushq","%rAX") + "\n"
    if not is_rdx:
        this_str += make_x86("pushq","%rDX") + "\n"
        
    divisor = make_value(src)
    if divisor == "%rAX" or divisor == "%rDX" or type(src) == Const:
        this_str += make_x86("movq",make_value(src),"%r8") + "\n"
        divisor = "%r8"
    
    this_str += make_x86("movq",make_value(dest),"%rAX") + "\n"
        
    this_str += make_x86("movq","$0","%rDX") + "\n"
    this_str += make_x86("cqto") + "\n"
    this_str += make_x86("idivq",divisor) + "\n"
    out_reg = "%rDX" if return_mod else "%rAX"
    
    this_str += make_x86("movq",out_reg,make_value(dest))
    
    if not is_rdx:
        this_str += "\n" + make_x86("popq","%rDX")
    if not is_rax:
        this_str += "\n" + make_x86("popq","%rAX")
    
    return this_str
#
#psm runtime helpers
#
    
def eval_expr(oper,first,second=None):
    """
    Evaluates the expression using the passed in oper function, 
    then truncates the result into 64 bits, then 
    
    """
    first_ty = type(first)
    if second == None:
        second_ty = int_val
        new_val = truncate(oper(first.int))
    else:
        second_ty = type(second)
        new_val = truncate(oper(first.int,second.int))
    
    def are_types(ty1,ty2):
        return (first_ty == ty1 and second_ty == ty2)
    def is_comb(ty1,ty2):
        return are_types(ty1,ty2) or are_types(ty2,ty1)
    def ty_exists(ty):
        return first_ty == ty or second_ty == ty
    
    if are_types(int_val,int_val):
        ty = int_val
    elif is_comb(stack_ptr_val,int_val) or are_types(stack_ptr_val,stack_ptr_val):
        ty = stack_ptr_val
    elif ty_exists(instruc_val): 
        instruc_warnings.add("instruction ptr value changed")
        ty = unknown_val
    elif ty_exists(unknown_val):
        instruc_warnings.add("Unknown value accessed.")
        ty = unknown_val
        
    return ty(new_val)
    
def check_val(val):
    if type(val) == unknown_val:
        instruc_warnings.add("Unknown value loaded.")
    elif type(val) == instruc_val:
        instruc_warnings.add("Instruction pointer loaded.")
    
    return val
        
def inc_rSP(rSP):
    rSP.set(eval_expr(operator.add,rSP.get(),int_val(8)))
def add_offset(loc_reg,offset):
    return eval_expr(operator.add,loc_reg.get(),offset.get())
    
#
#base classes which do nothing themselves but help make similar instructions more concise
#

class Single(object):
    def __init__(self,in_dest):
        self.dest = in_dest
    #helper fns to aid child class methods of eval and to_x86  
    def eval_with(self,oper):
        self.dest.set(eval_expr(oper,self.dest.get()))
    def sing_to_x86(self,instr):
        return make_x86(instr,make_value(self.dest))
        
class Double(object):
    def __init__(self,in_dest,in_src):
        self.dest = in_dest
        self.src = in_src
    #helper fns to aid child class methods of eval and to_x86  
    def eval_with(self,oper):
        self.dest.set(eval_expr(oper,self.dest.get(),self.src.get()))
    def doub_to_x86(self,instr):
        return make_x86(instr,make_value(self.src),make_value(self.dest))
        
class PP(object):
    def __init__(self,loc,rSP,Stack):
        self.loc = loc
        self.rSP = rSP
        self.Stack = Stack
        
#
#full list of instructions
#

class Add(Double):
    def eval(self):
        self.eval_with(operator.add)
    def to_x86(self):
        return self.doub_to_x86("addq")
class Sub(Double):
    def eval(self):
        self.eval_with(operator.sub)
    def to_x86(self):
        return self.doub_to_x86("subq")
class SAL(Double):
    def eval(self):
        self.eval_with(operator.lshift)
    def to_x86(self):
        return self.doub_to_x86("salq")
class SAR(Double):
    def eval(self):
        self.eval_with(operator.rshift)
    def to_x86(self):
        return self.doub_to_x86("sarq")
class Rem(Double):
    def eval(self):
        self.eval_with(lambda dest,src: int(math.copysign(abs(dest) % abs(src),dest)))
    def to_x86(self):
        return make_div(self.src,self.dest,True)
class Div(Double):
    def eval(self):
        self.eval_with(lambda dest,src: int(math.copysign(abs(dest) / abs(src),dest * src)))#integer division
    def to_x86(self):
        return make_div(self.src,self.dest,False)
class Mul(Double):
    def eval(self):
        self.eval_with(operator.mul)
    def to_x86(self):
        return self.doub_to_x86("imulq")
class And(Double):
    def eval(self):
        self.eval_with(operator.and_)
    def to_x86(self):
        return self.doub_to_x86("andq")
class Or(Double):
    def eval(self):
        self.eval_with(operator.or_)
    def to_x86(self):
        return self.doub_to_x86("orq")
class Xor(Double):
    def eval(self):
        self.eval_with(operator.xor)
    def to_x86(self):
        return self.doub_to_x86("xorq")
class Mov(Double):
    def eval(self):
        self.dest.set(check_val(self.src.get()))
    def to_x86(self):
        return self.doub_to_x86("movq")
class Push(PP):
    def eval(self):
        new_val = eval_expr(operator.sub,self.rSP.get(),int_val(8))
        self.Stack.set(new_val,check_val(self.loc.get()))
        self.rSP.set(new_val)
    def to_x86(self):
        return make_x86("pushq",make_value(self.loc))
class Pop(PP):
    def eval(self):
        self.loc.set(check_val(self.Stack.get(self.rSP.get())))
        inc_rSP(self.rSP)
    def to_x86(self):
        return make_x86("popq",make_value(self.loc))
class Inc(Single):
    def eval(self):
        self.eval_with(lambda dest:dest + 1)
    def to_x86(self):
        return self.sing_to_x86("incq")
class Dec(Single):
    def eval(self):
        self.eval_with(lambda dest:dest - 1)
    def to_x86(self):
        return self.sing_to_x86("decq")
class Neg(Single):
    def eval(self):
        self.eval_with(operator.neg)
    def to_x86(self):
        return self.sing_to_x86("negq")
class Not(Single):
    def eval(self):
        self.eval_with(operator.invert)
    def to_x86(self):
        return self.sing_to_x86("notq")
#MemStore and MemLoad's version without the offset is the same as when the offset is zero
class MemStore(object):
    def __init__(self,in_source,Stack,mem_loc,mem_off=Const(0)):
        self.src = in_source
        self.dest_loc = mem_loc
        self.offset = mem_off
        self.Stack = Stack
    def eval(self):
        new_loc = add_offset(self.dest_loc,self.offset)
        self.Stack.set(new_loc,check_val(self.src.get()))
    def to_x86(self):
        return make_x86("movq",make_value(self.src),make_offset(self.dest_loc,self.offset))
    
class MemLoad(object):
    def __init__(self,in_dest,Stack,mem_loc,mem_off=Const(0)):
        self.dest = in_dest
        self.src_loc = mem_loc
        self.offset = mem_off
        self.Stack = Stack
    def eval(self):
        loc = add_offset(self.src_loc,self.offset)
        self.dest.set(check_val(self.Stack.get(loc)))
    def to_x86(self):
        return make_x86("movq",make_offset(self.src_loc,self.offset),make_value(self.dest))

class GoTo(object):
    def __init__(self,in_label,in_loc,State):
        self.label = in_label
        self.loc = instruc_val(in_loc)
        self.PState = State
    def eval(self):
        self.PState.jmp_to(self.loc,True)
    def to_x86(self):
        return make_x86("jmp",self.label)
        
class Cond_jump(object):
    def __init__(self,rA,rB,Op,in_label,in_loc,State):
        self.label = in_label
        self.loc = instruc_val(in_loc)
        self.op = Op
        self.rA = rA
        self.rB = rB
        self.PState = State
    def eval(self):
        rA_ty = type(self.rA.val)
        rB_ty = type(self.rB.val)
        if rA_ty != rB_ty or rA_ty == unknown_val:
            instruc_warnings.add("comparison registers originated from different sources \nobjectivity of comparision not guarenteed")
        will_jump = self.op(self.rA.val.int,self.rB.val.int)
        self.PState.jmp_to(self.loc,will_jump)
    def to_x86(self):
        #rA and rB are flipped because the AT&T syntax is really weird
        part1 = make_x86("cmpq",make_value(self.rB),make_value(self.rA))
        op_dict = {operator.eq:"je",operator.ne:"jne",operator.lt:"jl",operator.le:"jle",operator.gt:"jg",operator.ge:"jge"}
        
        part2 = make_x86(op_dict[self.op],self.label)
        return part1 + "\n" + part2
    
class Call(object):
    def __init__(self,in_label,in_loc,call_loc,rSP,Stack,State):
        self.label = in_label
        self.loc = instruc_val(in_loc)
        #the location of the return is that of the next instruction, not this one
        self.ret_loc = instruc_val(call_loc + 1)
        self.rSP = rSP
        self.PState = State
        self.Stack = Stack
    def eval(self):
        self.Stack.check_16byte_stack_alignment()
        new_val = eval_expr(operator.sub,self.rSP.get(),int_val(8))
        self.Stack.set(new_val,self.ret_loc)
        self.rSP.set(new_val)
        self.PState.jmp_to(self.loc,True)
    def to_x86(self):
        return make_x86("callq",self.label)
        
class Return(object):
    def __init__(self,rSP,Stack,State):
        self.PState = State
        self.Stack = Stack
        self.rSP = rSP
    def eval(self):
        loc = self.Stack.get(self.rSP.get())
        self.PState.jmp_to(loc,True)
        inc_rSP(self.rSP)
        
        self.PState.check_proper_return()
        
    def to_x86(self):
        return make_x86("retq")

class Output(object):
    def __init__(self,src,Console,Stack):
        self.src = src
        self.Cons = Console
        self.Stack = Stack
    def eval(self):
        self.Stack.check_16byte_stack_alignment()
        self.Cons.print_val(self.src.get())
    def to_x86(self):
        return make_x86("pushq","%rDI") + "\n" + \
            make_x86("subq","$8","%rSP") + "\n" + \
            make_x86("movq",make_value(self.src),"%rDI") + "\n" + \
            ((make_x86("addq","$16","%rDI")  + "\n") if (self.src.name == "rSP") else "") + \
            make_x86("callq",("print" if platform_check.is_gcc() else "_print")) + "\n" + \
            make_x86("addq","$8","%rSP") + "\n" + \
            make_x86("popq","%rDI")
        
class Input(object):
    def __init__(self,dest,Console,Stack):
        self.dest = dest
        self.Cons = Console
        self.Stack = Stack
    def eval(self):
        self.Stack.check_16byte_stack_alignment()
        self.Cons.place_input_into(self.dest)
    def to_x86(self):
        is_not_rax = (self.dest.name != "rAX")
        
        this_str = ""
        if is_not_rax:
            this_str += make_x86("pushq","%rAX") + "\n"
            this_str += make_x86("subq","$8","%rSP") + "\n"
           
        this_str += make_x86("callq",("input" if platform_check.is_gcc() else "_input"))
            
        if is_not_rax:
            this_str += "\n" + make_x86("movq","%rAX",make_value(self.dest))
            this_str += "\n" + make_x86("addq","$8","%rSP")
            this_str += "\n" + make_x86("popq","%rAX")
            
        return this_str

class Random(object):
    def __init__(self,dest,Stack):
        self.dest = dest
        self.Stack = Stack
    def eval(self):
        self.Stack.check_16byte_stack_alignment()
        self.dest.set(int_val(random.randint(0,32767)));
    def to_x86(self):
        is_not_rax = (self.dest.name != "rAX")
        
        this_str = ""
        if is_not_rax:
            this_str += make_x86("pushq","%rAX") + "\n"
            this_str += make_x86("subq","$8","%rSP") + "\n"
           
        this_str += make_x86("callq",("random" if platform_check.is_gcc() else "_random"))
            
        if is_not_rax:
            this_str += "\n" + make_x86("movq","%rAX",make_value(self.dest))
            this_str += "\n" + make_x86("addq","$8","%rSP")
            this_str += "\n" + make_x86("popq","%rAX")
            
        return this_str
        