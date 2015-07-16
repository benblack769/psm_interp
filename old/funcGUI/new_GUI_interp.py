#!/usr/bin/python
import tkinter.messagebox
from p_interp import *

text_width = 300
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
textscrollbar=Scrollbar(text_holder,orient="vertical",command=text_canvas.yview)
text_canvas.configure(yscrollcommand=textscrollbar.set)
textscrollbar.pack(side="right",fill="y")
text_canvas.pack(side="left")

def text_redraw(event):
    text_canvas.configure(scrollregion=text_canvas.bbox("all"),width=text_width,height=def_height)

def text_on_mousewheel(event):
    text_canvas.yview_scroll(-1*(event.delta//80), "units")

text_canvas.create_window((0,0),window=textframe,anchor='nw')
textframe.bind("<Configure>",text_redraw)

        
class codeline(object):
    def __init__(self,line_num,InMaster):
        self.code = flines[line_num]
        self.line = line_num
        self.break_flag = IntVar(InMaster)
        self.break_flag.trace("w",self.break_change)
        self.pause_flag = IntVar(InMaster)
        self.pause_flag.trace("w",self.pause_change)
        self.Label = Label(InMaster,text=self.code,height=2)
        
    def break_change(self,*args):
        if self.line in break_points:
            break_points.remove(self.line)
        else:
            break_points.add(self.line)
            
    def pause_change(self,*args):
        if self.line in pause_points:
            pause_points.remove(self.line)
        else:
            pause_points.add(self.line)
        
fcode = [codeline(n,textframe) for n in range(len(flines))]

for n,cl in enumerate(fcode):
    CBB = Checkbutton (textframe,variable=cl.break_flag)
    CBB.grid(row=n,column=0)
    CBP = Checkbutton (textframe,variable=cl.pause_flag)
    CBP.grid(row=n,column=1)
    cl.Label.grid(row=n,column=2,sticky="W")
    
    cl.Label.bind("<MouseWheel>", text_on_mousewheel)
    CBB.bind("<MouseWheel>", text_on_mousewheel)
    CBP.bind("<MouseWheel>", text_on_mousewheel)
    #OSX stuff to do
    '''root.bind("<Button-4>", mouse_wheel)
    root.bind("<Button-5>", mouse_wheel)'''

textframe.bind("<MouseWheel>", text_on_mousewheel)
text_canvas.bind("<MouseWheel>", text_on_mousewheel)
text_holder.bind("<MouseWheel>", text_on_mousewheel)
'''
makes the registers and memory set
'''
    
def GetCallback(SV,IV):
    def Callback(*args):
        SV.set(to_hex(IV.get()))
    return Callback
    
reg_mem_frame = PanedWindow(top,height=def_height,width=register_width,orient=VERTICAL)
reg_height = 200
mem_height = (def_height - reg_height)
reg_holder = Frame(reg_mem_frame,relief=GROOVE,width=register_width,height=reg_height,bd=1)

for X,name in enumerate(reg_name_list):
    reg = registers[name]
    SV = StringVar()
    reg.graphic_rep = IntVar()
    #this is necessary to make sure SV is not the same among all registers

    reg.graphic_rep.trace("w",GetCallback(SV,reg.graphic_rep))
    Label(reg_holder,text=name).grid(row=X,column=0,sticky="W")
    Label(reg_holder,textvariable=SV).grid(row=X,column=1,sticky="W")

mem_holder = Frame(reg_mem_frame,relief=GROOVE,width=register_width,height=mem_height,bd=1)
mem_canvas = Canvas(mem_holder)
mem_frame = Frame(mem_canvas)
memscrollbar = Scrollbar(mem_holder,orient="vertical",command=mem_canvas.yview)
mem_canvas.configure(yscrollcommand=memscrollbar.set)

memscrollbar.pack(side="right",fill="y")
mem_canvas.pack(side="left")

def mem_redraw(event):
    mem_canvas.configure(scrollregion=mem_canvas.bbox("all"),width=register_width,height=mem_height)

def mem_on_mousewheel(event):
    mem_canvas.yview_scroll(-1*(event.delta//80), "units")

mem_canvas.create_window((0,0),window=mem_frame,anchor='nw')
mem_frame.bind("<Configure>",mem_redraw)

for X,num in enumerate(Stack.data):
    SV = StringVar()
    IV = IntVar()
    
    IV.trace("w",GetCallback(SV,IV))
    Stack.graphic_reps.append(IV)
    Lab = Label(mem_frame,textvariable=SV)
    Lab.grid(row=X,column=0,sticky="W")
    Lab.bind("<MouseWheel>", mem_on_mousewheel)

mem_frame.bind("<MouseWheel>", mem_on_mousewheel)
mem_canvas.bind("<MouseWheel>", mem_on_mousewheel)
mem_holder.bind("<MouseWheel>", mem_on_mousewheel)

def represent_all():
    for n,r in registers.items():
        r.represent(True)
    Stack.represent(True)
    
represent_all()

def run_callback():
    fcode[instruc.val].Label["bg"] = text_canvas["bg"]
    thisexecute()
    while instruc.val not in break_points:
        if instruc.val in pause_points:
            pause_update_callback()
            return
        thisexecute()
    #it hit a breakpoint
    fcode[instruc.val].Label["bg"] = "blue"
    represent_all()

def pause_update_callback():
    represent_all()
    root.after(500,run_callback)
    fcode[instruc.val].Label["bg"] = "red"
    
button_frame = Frame(top)
run_button = Button(button_frame, text="run",command=run_callback)
run_button.pack()
entry_widget = Entry(button_frame,text="out file",bd=5)
entry_widget.pack(side=LEFT)

reg_mem_frame.add(reg_holder)
reg_mem_frame.add(mem_holder)

top.add(reg_mem_frame)
top.add(text_holder)
top.add(button_frame)

root.mainloop()