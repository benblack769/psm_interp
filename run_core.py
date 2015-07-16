
bit64 = 1 << 64
def truncate(num):
    num &= bit64 - 1
    if num > (bit64 >> 1) - 1:
        num -= bit64
    return num

#error and warning core
class AssemblyRunError(Exception):
    def __init__(self,Str):
        self.message = Str
    def __str__(self):
        return self.message
        
instruc_warnings = set()
old_instruc_warnings = set()

#prints out the "instruc_warning" if there is one
#this will be called after every instruction unconditionally
def handle_run_warnings(line_num):
    for warn in instruc_warnings:
        warn_str = str(line_num) + warn
        if warn_str not in old_instruc_warnings:
            print("Warning: ")
            print("on line " +  str(line_num) + ":")
            print(warn,"\n")
            old_instruc_warnings.add(warn_str)
            
    instruc_warnings.clear()
        
#this will be called only if there is an exception
def handle_run_exception(line_num,Except):
    print("Error: ")
    print("on line " +  str(line_num) + ":")
    print(Except,"\n")
        
def to_hex(num):
    #this implementationf forces the entire 16 charachter hexidecimal display for 64 bit numbers
    hex_str = "0x"
    for n in range(15,-1,-1):
        #this way, it will only produce one digit at a time, so it will get all of the digits
        hex_str = hex_str + (hex((num >> (n * 4)) & 0xf)[2:])
    return hex_str
    
class Val(object):
    def __init__(self,val):
        self.int = val
            
class int_val(Val):
    descrip = "manipulated integer"
    def to_str(self,is_hex):
        if is_hex:
            return to_hex(self.int)
        else:
            return int(self.int)
            
class stack_ptr_val(Val):
    descrip = "stack pointer"
    def to_str(self,is_hex):
        return to_hex(self.int)
        
class instruc_val(Val):
    descrip = "instruction pointer"
    def to_str(self,is_hex):
        return to_hex(self.int)
        
class unknown_val(Val):
    descrip = "uninitialized value"
    def to_str(self,is_hex):
        if is_hex:
            return "0x" + "#" * 16
        else:
            return "#" * 20
