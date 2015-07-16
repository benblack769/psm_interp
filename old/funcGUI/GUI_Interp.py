#!/usr/bin/python
import tkinter.messagebox
from tkinter import *
from GUI_Interp_core import *
#filename = input("Type File name: ")

class codeline(object):
    def __init__(self,Str,InMaster):
        self.code = Str
        self.flag = IntVar(InMaster)
#filename = input("Type File name: ")
file = open("Assembly.s")
flines = file.readlines()
registers = GetRegisters()

FuncPoints = GetFuncPoints(flines)

FuncPoints["input"] = inputfunc
FuncPoints["print"] = printfunc
print(FuncPoints)
if "main" not in FuncPoints:
    raise AssertionError("No main function in assembly code, exiting.")
    
curspot = IntHolder(FuncPoints["main"])

Stack = array.array('L')#unsigned long array of 4 bytes per int
for n in range(StackSize):
    Stack.append(0)

BreakPoints = set()
CallStack = []
Conditions = {N:False,Z:False,V:False,C:False}
LineFns = CreateLineFns(flines,FuncPoints,Stack,registers,Conditions,CallStack,curspot)

def thisexecute():
    if curspot.num >= len(lines):
        raise AssertionError("End of file reached without return.")
    Fn = LineFns[curspot.num]
    curspot.num += 1#default value, Fn() can still change this
    if Fn != None:
        Fn()

text_width = 600
register_width = 200
def_height = 600

root = Tk()

top = PanedWindow(root,height=def_height,width=(text_width+register_width))
top.pack(fill=BOTH, expand=1)
'''
makes text_holder
'''
#puts in the code and the associated breakpoint checkboxes
text_holder=Frame(top,relief=GROOVE,width=text_width,height=def_height,bd=1)
text_holder.pack(side=LEFT)

text_canvas=Canvas(text_holder)
textframe=Frame(text_canvas)
myscrollbar=Scrollbar(text_holder,orient="vertical",command=text_canvas.yview)
text_canvas.configure(yscrollcommand=myscrollbar.set)

myscrollbar.pack(side="right",fill="y")
text_canvas.pack(side="left")

def text_redraw(event):
    text_canvas.configure(scrollregion=text_canvas.bbox("all"),width=text_width,height=def_height)

def text_on_mousewheel(event):
    text_canvas.yview_scroll(-1*(event.delta//80), "units")

text_canvas.create_window((0,0),window=textframe,anchor='nw')
textframe.bind("<Configure>",text_redraw)
fcode = [codeline(s,textframe) for s in flines]

for n in range(len(fcode)):
    cl = fcode[n]
    CB = Checkbutton (textframe,variable=cl.flag)
    CB.grid(row=n,column=0)
    Lab = Label(textframe,text=cl.code)
    Lab.grid(row=n,column=1,sticky="W")
    
    Lab.bind("<MouseWheel>", text_on_mousewheel)
    CB.bind("<MouseWheel>", text_on_mousewheel)
    #OSX stuff to do
    '''root.bind("<Button-4>", mouse_wheel)
    root.bind("<Button-5>", mouse_wheel)'''
    
textframe.bind("<MouseWheel>", text_on_mousewheel)
'''
makes the registers and memory set
'''

reg_mem_frame = PanedWindow(top,height=def_height,width=register_width,orient=VERTICAL)
reg_height = 200
mem_height = (def_height - reg_height)
reg_holder = Frame(reg_mem_frame,relief=GROOVE,width=register_width,height=reg_height,bd=1)
X = 0
for name in ORDERED_REGISTERS:
    reg = registers[name]
    SV = StringVar()
    reg.graphic_rep = IntVar()
    def GetCallback(SV,IV):
        def Callback(*args):
            SV.set(hex(IV.get()))
        return Callback

    reg.graphic_rep.trace("w",GetCallback(SV,reg.graphic_rep))
    Label(reg_holder,text=name).grid(row=X,column=0,sticky="W")
    Label(reg_holder,textvariable=SV).grid(row=X,column=1,sticky="W")
    reg.graphic_rep.set(0)
    X += 1

mem_holder = Frame(reg_mem_frame,relief=GROOVE,width=register_width,height=mem_height,bd=1)
mem_canvas = Canvas(mem_holder)
mem_frame = Frame(mem_canvas)
myscrollbar = Scrollbar(mem_holder,orient="vertical",command=mem_canvas.yview)
mem_canvas.configure(yscrollcommand=myscrollbar.set)

myscrollbar.pack(side="right",fill="y")
mem_canvas.pack(side="left")

def mem_redraw(event):
    mem_canvas.configure(scrollregion=mem_canvas.bbox("all"),width=register_width,height=mem_height)

def mem_on_mousewheel(event):
    mem_canvas.yview_scroll(-1*(event.delta//80), "units")

mem_canvas.create_window((0,0),window=mem_frame,anchor='nw')
mem_frame.bind("<Configure>",mem_redraw)

mem_var_list = []
for X in range(len(Stack)):
    SV = StringVar()
    IV = IntVar()
    mem_var_list.append(IntVar())
    def GetCallback(SV,IV):
        def CallBack(*args):
            SV.set(hex(IV.get()))
        return CallBack
    
    IV.trace("w",GetCallback(SV,IV))
    IV.set(0)
    mem_var_list[X] = IV
    Lab = Label(mem_frame,textvariable=SV)
    Lab.grid(row=X,column=0,sticky="W")
    Lab.bind("<MouseWheel>", mem_on_mousewheel)

mem_frame.bind("<MouseWheel>", mem_on_mousewheel)
mem_canvas.bind("<MouseWheel>", mem_on_mousewheel)
mem_holder.bind("<MouseWheel>", mem_on_mousewheel)

def run_callback(event):
    thisexecute()
    while curspot.num not in BreakPoints:
        thisexecute()

def pause_update_callback(event):
    for r in registers:
        if r.size == 8:
            r.graphic_rep.set(int(r._val))

button_frame = Frame(top)
run_button = Button(button_frame, text="run",command=run_callback)
run_button.pack()

reg_mem_frame.add(reg_holder)
reg_mem_frame.add(mem_holder)

top.add(reg_mem_frame)
top.add(text_holder)
top.add(button_frame)

root.mainloop()