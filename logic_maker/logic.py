from tkinter import *
from enum import Enum
from math import sqrt
import tkinter.messagebox as messagebox
import string
import copy

def top_sort(Nodes):
    new_order = []
    S = []
    for N in Nodes:
        N.incounter = len(N.ins)
        if N.incounter == 0:
            S.append(N)
            
    while S:
        u = S.pop()
        new_order.append(u)
        for out in u.out_nodes():
            out.incounter -= 1
            if out.incounter == 0:
                S.append(out)
                
    return new_order
#ordinary update that cuts out loops

def normal_update(Nodes):
    for n in Nodes:
        if n.type != GateTy.In:
            n.state = None
            
    ordered = top_sort(Nodes)
    #if there are nodes in Nodes that are not in ordered, then there is a circle
    for n in ordered:
        n.eval()

top = Tk()

Radio_Height = 70
Radio_Width = 2000
SelectTyVar = IntVar()
EDIT_VAL = 1
EVAL_VAL = 2
MenuFrame = Frame(top,relief=GROOVE,height=Radio_Height,width=Radio_Width)
Radiobutton(MenuFrame,text="Edit",variable=SelectTyVar,value=EDIT_VAL).pack(side=LEFT)
Radiobutton(MenuFrame,text="Evaluate",variable=SelectTyVar,value=EVAL_VAL).pack(side=LEFT)
SelectTyVar.set(EDIT_VAL)

canv_color = "white"
BodyFrame = Frame(top)
canv_width = 4000
canv_height = 3000
canv = Canvas(BodyFrame,bg=canv_color,width=canv_width,height=canv_height)
VertScrollBar = Scrollbar(BodyFrame,orient=VERTICAL,command=canv.yview)
HorizScrollBar = Scrollbar(BodyFrame,orient=HORIZONTAL,command=canv.xview)
canv.config(scrollregion=(0,0,canv_width,canv_height),yscrollcommand=VertScrollBar.set,xscrollcommand=HorizScrollBar.set)

MOUSEX = MOUSEY = 0

class GateTy(Enum):
    In = 0
    Out = 1
    And = 2
    Or = 3
    Xor = 4
    Not = 5
    
def get_image(s):
    return PhotoImage(file=s+".gif")
    
GateBMPs = { GateTy.In:get_image("in"),
             GateTy.Out:get_image("out"),
             GateTy.And:get_image("and"),
             GateTy.Or:get_image("or"),
             GateTy.Xor:get_image("xor"),
             GateTy.Not:get_image("not")}

comp_size = 64
comp_sel_size = 10
con_size = 25
line_width = 2.5
link_size = 10
con_color = "black"

def distance(x1,y1,x2,y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)
    
class Component(object):
    def __init__(self,which,max_inputs=float("inf"),has_outputs=True):

        self.type = which
        self.image = GateBMPs[which]

        self.state = False
        self.ins = []
        self.outs = []
        self.arity = max_inputs
        self.can_link = has_outputs

        self.width = comp_size
        self.height = comp_size
        self.x = -comp_size
        self.y = -comp_size
        self.is_selected = False

    def input_click(self):
        if SelectTyVar.get() == EDIT_VAL and Context.selec_con_start != None:
            Context.place_link(self)
            return True
        else:
            return False
            
    def output_click(self):
        if SelectTyVar.get() == EDIT_VAL and not Context.is_busy():   
            Context.selec_con_start = self
            return True
        else:
            return False
            
    def main_click(self):
        if SelectTyVar.get() == EDIT_VAL:
            if Context.is_busy() == False:
                Context.comps.remove(self)
                Context.selected = self
                return True
            elif self is Context.selected:
                Context.place_gate()
                return True
            else:
                return False
        else:
            if self.type == GateTy.In:
                self.state = not self.state
                Context.update()
                return True
            else:
                return False
        
    def try_click(self,x,y):
        if distance(x,y,self.input_x(),self.input_y()) <= comp_sel_size // 2:
            if self.input_click():
                return True
                
        if distance(x,y,self.output_x(),self.output_y()) <= comp_sel_size // 2:
            if self.output_click():
                return True
                
        if x >= self.x and y >= self.y and x <= self.x + self.width and y <= self.y + self.height:
            if self.main_click():
                return True
        
        for link in self.ins:
            if link.try_click(x,y):
                return True
                
        return False
        
    def in_nodes(self):
        return [link.source for link in self.ins]
        
    def out_nodes(self):
        return [link.target for link in self.outs]
        
    def place(self,x,y):
        self.x = x
        self.y = y

    def input_x(self):
        return self.x + 2

    def input_y(self):
        return self.y + self.height // 2

    def output_x(self):
        return self.x + self.width - 2

    output_y = input_y

    def render(self,is_selected):
        canv.create_rectangle(self.x,self.y,self.x + self.width, self.y + self.height,fill=self.color(is_selected),outline="")
        canv.create_image(self.x,self.y, image=GateBMPs[self.type],anchor="nw")

    def color(self,is_selected):
        if is_selected:
            return "red"
        elif SelectTyVar.get() == EDIT_VAL:
            return "yellow"
        elif self.state == False:
            return "red"
        elif self.state == True:
            return "green"
        else:
            return "blue"
        
    def delete(self):
        for con in self.ins+self.outs:
            con.delete()  
            
def has_bad_input(InNodes):
    if len(InNodes) == 0:
        return True
    else:
        for N in InNodes:
            if N.state == None:
                return True
                
    return False

class AndGate(Component):
    def __init__(self):
        super(AndGate,self).__init__(GateTy.And)
    def eval(self):
        in_ns = self.in_nodes()
        if has_bad_input(in_ns):
            self.state = None
        else:
            self.state = True
            for N in in_ns:
                if not N.state:
                    self.state = False
                    return

class OrGate(Component):
    def __init__(self):
        super(OrGate,self).__init__(GateTy.Or)
    def eval(self):
        in_ns = self.in_nodes()
        if has_bad_input(in_ns):
            self.state = None
        else:
            self.state = False
            for N in in_ns:
                if N.state:
                    self.state = True
                    return

class XorGate(Component):
    def __init__(self):
        super(XorGate,self).__init__(GateTy.Xor)
    def eval(self):
        in_ns = self.in_nodes()
        if has_bad_input(in_ns):
            self.state = None
        else:
            self.state = False
            for N in in_ns:
                if N.state and self.state:
                    self.state = False
                    return
                elif N.state:
                    self.state = True

class NotGate(Component):
    def __init__(self):
        super(NotGate,self).__init__(GateTy.Not,1)
    def eval(self):
        in_ns = self.in_nodes()
        if has_bad_input(in_ns) or len(in_ns) > 1:
            self.state = None
        else:
            self.state = not in_ns[0].state

class InputPin(Component):
    def __init__(self):
        super(InputPin,self).__init__(GateTy.In,0)
    def eval(self):
        return

class OutputProbe(Component):
    def __init__(self):
        super(OutputProbe,self).__init__(GateTy.Out,1,False)
    def eval(self):
        in_ns = self.in_nodes()
        if has_bad_input(in_ns) or len(in_ns) > 1:
            self.state = None
        else:
            self.state = in_ns[0].state

class Link(object):
    def __init__(self,start,end):
        self.source = start
        self.target = end
        
    def click_action(self):
        if SelectTyVar.get() == EDIT_VAL and not Context.is_busy():
            self.delete()
            Context.selec_con_start = self.source
            return True
        else:
            return False
        
    def delete(self):
        self.source.outs.remove(self)
        self.target.ins.remove(self)

    def render(self):
        midx,midy = self.get_midpoint()
        dif = con_size // 2
        if SelectTyVar.get() == EVAL_VAL:
            color = self.source.color(False)
            canv.create_line(self.source.output_x(),self.source.output_y(),self.target.input_x(),self.target.input_y(),fill=color,width=line_width+2)
            canv.create_oval(midx - dif,midy - dif, midx + dif,midy + dif,fill="",outline=color,width=line_width+2)
            
        canv.create_line(self.source.output_x(),self.source.output_y(),self.target.input_x(),self.target.input_y(),fill=con_color,width=line_width)
        
        canv.create_oval(midx - dif,midy - dif, midx + dif,midy + dif,fill="",outline=con_color,width=line_width) 
        
    def get_midpoint(self):
        midx = (self.source.output_x() + self.target.input_x()) // 2
        midy = (self.source.output_y() + self.target.input_y()) // 2
        return midx,midy
        
    def try_click(self,x,y):
        midx,midy = self.get_midpoint()
        if SelectTyVar.get() == EDIT_VAL and distance(x,y,midx,midy) <= con_size // 2:
            if self.click_action():
                return True
        
        return False
        
class Gate_Holder(object):
    def __init__(self):
        self.comps = []
        self.selected = None
        self.selec_con_start = None
        
    def place_gate(self):
        self.comps.append(self.selected)
        self.selected = None
        
    def is_busy(self):
        return bool(self.selected) or bool(self.selec_con_start)
        
    def place_link(self,EndNode):
        StartNode = self.selec_con_start
        if StartNode is not EndNode and len(EndNode.ins) < EndNode.arity:
            CI = Link(StartNode,EndNode)
            
            StartNode.outs.append(CI)
            EndNode.ins.append(CI)
        
        self.selec_con_start = None
        
    def create_and_select(self,type):
        if self.is_busy():
            return
        self.selected = type_to_comp[type]()
            
    def mouse_motion(self,event):
        if SelectTyVar.get() != EDIT_VAL:
            return
        global MOUSEX,MOUSEY
        MOUSEX = canv.canvasx(event.x)
        MOUSEY = canv.canvasy(event.y)
        
        global canv_width,canv_height
        win_buffer = 700
        if MOUSEX + win_buffer > canv_width:
            canv_width += win_buffer
            canv.config(width=canv_width,scrollregion=(0,0,canv_width,canv_height))
            self.render()
        
        if MOUSEY + win_buffer > canv_height:
            canv_height += win_buffer
            canv.config(height=canv_height,scrollregion=(0,0,canv_width,canv_height))
            self.render()
            
        if self.selected != None:
            self.selected.x = MOUSEX - self.selected.width // 2
            self.selected.y = MOUSEY - self.selected.height // 2
            self.render()
        elif self.selec_con_start != None:
            self.render()
    
    def click(self,event):
        if self.selected != None:
            self.comps.append(self.selected)
            self.selected = None
            self.render()
        else:
            for comp in self.comps:
                if comp.try_click(canv.canvasx(event.x),canv.canvasy(event.y)):
                    self.render()
                    return
    
    def update(self):
        normal_update(self.comps)
    
    def delete(self,event):  
        if SelectTyVar.get() != EDIT_VAL:
            return
        elif self.selected:
            self.selected.delete()
            self.selected = None
            self.render()
        elif self.selec_con_start:
            self.selec_con_start = None
            self.render()
    
    def render(self):
        canv.delete("all")               
        for comp in self.comps:
            comp.render(False)
            
        for comp in self.comps: 
            for link in comp.outs:
                link.render()
                
        if self.selected != None:
            self.selected.render(True)
            for link in self.selected.outs:
                link.render()
            
        scs = self.selec_con_start
        if scs != None:
            canv.create_line(MOUSEX,MOUSEY,scs.output_x(),scs.output_y(),fill=con_color,width=line_width)

type_to_comp = {GateTy.In:InputPin,GateTy.Out:OutputProbe,GateTy.And:AndGate,GateTy.Or:OrGate,GateTy.Xor:XorGate,GateTy.Not:NotGate}

Context = Gate_Holder()

canv.bind_all('<Motion>', Context.mouse_motion)
canv.bind_all('<Button-1>', Context.click)
canv.bind_all('<Delete>', Context.delete)
canv.bind_all('<BackSpace>', Context.delete)
canv.bind_all('d', Context.delete)

def place_button(type):
    def event_handler():
        if SelectTyVar.get() == EDIT_VAL:
            Context.create_and_select(type)
    Button(MenuFrame,image=GateBMPs[type],command=event_handler).pack(side=LEFT)
    
place_button(GateTy.In)
place_button(GateTy.Out)
place_button(GateTy.Not)
place_button(GateTy.Or)
place_button(GateTy.And)
place_button(GateTy.Xor)

def make_file():
    file = open("logic_output.logic","w")
    ordered = top_sort(Context.comps)
    letters = iter(string.ascii_letters)
    for comp in ordered:
        comp.letter = next(letters)
        
    OrderFailed = False
    for comp in Context.comps:
        if comp not in ordered:
            OrderFailed = True
            comp.letter = next(letters)
            
    def concat_gates(comps):
        return " ".join([c.letter for c in comps])
    
    g_to_word = {GateTy.In:"input",GateTy.Xor: "xor",GateTy.And: "and",GateTy.Out: "out",GateTy.Or: "or",GateTy.Not: "not"}
    
    for comp in ordered:
        file.write(comp.letter + " = " + g_to_word[comp.type] + " " + concat_gates(comp.in_nodes()) + "\n")
    if OrderFailed:
        file.write("# the following's output cannot be computed due to cicularity\n")
        
        for comp in Context.comps:
            if comp not in ordered:
                file.write(comp.letter + " = " + g_to_word[comp.type] + " " + concat_gates(comp.in_nodes()) + "\n")
    
    for comp in Context.comps:
        del comp.letter
    
    file.close()

def load_file():
    word_to_g = {"input":GateTy.In,"xor":GateTy.Xor,"and":GateTy.And,"out":GateTy.Out,"or":GateTy.Or,"not":GateTy.Not}
    file = open("logic_output.logic")
    lines = file.readlines()
    file.close()
    #remove empty lines and commented lines
    new_lines = []
    for l in lines:
        if l.count("#"):
            l = l[:l.index("#")]
        if len(l) != 0 and not l.isspace():
            new_lines.append(l)
            
    lines = new_lines
    
    let_to_c = dict()
    for line in lines:
        tokens = line.split()
        let_to_c[tokens[0]] = type_to_comp[word_to_g[tokens[2]]]()
            
    for line in lines:
        tokens = line.split()
        if tokens[0] != "input" and len(tokens) >= 4:
            comp = let_to_c[tokens[0]]
            for in_let in tokens[3:]:
                in_comp = let_to_c[in_let]
                link = Link(in_comp,comp)
                comp.ins.append(link)
                in_comp.outs.append(link)
    
    def top_sort_depth(Nodes):
        changed = []
        layers = [changed]
        for n in Nodes:
            if len(n.ins) == 0:
                n.depth = 0
                changed.append(n)
            else:
                n.depth = float("inf")
        
        while changed:
            new_changed = []
            i = len(layers)
            layers.append(new_changed)
            for comp in changed:
                for c in comp.out_nodes():
                    if c.depth > i and c not in new_changed:
                        is_at_depth = True
                        for n in c.in_nodes():
                            if n.depth > i:
                                is_at_depth = False
                        if is_at_depth:
                            c.depth = i + 1
                            new_changed.append(c)
                    
            changed = new_changed
            
        for n in Nodes:
            if n.depth == float("inf"):
                changed.append(n)
                
            del n.depth
        
        return layers
    
    Context.comps = [comp for let,comp in let_to_c.items()]
    
    layers = top_sort_depth(Context.comps)
    for x,layer in enumerate(layers):
        for y,comp in enumerate(layer):
            comp.x = comp_size * x * 2 + comp_size
            comp.y = comp_size * y * 2 + comp_size
            
    Context.update()
    Context.render()

def print_karnaugh_maps():
            
    def combs(size):
        if size == 0:
            return [[False]]
        elif size == 1:
            return [[False],[True]]
        else:
            prev_greys = combs(size-1)
            false_greys = prev_greys
            true_greys = copy.deepcopy(prev_greys)[::-1]#deep copys and reverses the list
            for cbs in false_greys:
                cbs.append(False)
                    
            for cbs in true_greys:
                cbs.append(True)
                    
            return false_greys + true_greys
                
    nodes = Context.comps
    inputs = []
    outputs = []
    for n in nodes:
        if n.type == GateTy.In:
            inputs.append(n)
        elif n.type == GateTy.Out:
            outputs.append(n)
            
    for n in inputs:
        n.state = False
        
    top = inputs[:len(inputs) // 2]
    left = inputs[len(inputs) // 2:]
    def to_str(b):
        return "1" if b else "0"
        
    for out in outputs:
        first_line = " " * len(left)
        for top_states in combs(len(top)):
            first_line += "|"
            for b in top_states:
                first_line += to_str(b)
                
        print(first_line)
        
        for left_states in combs(len(left)):
            this_line = ""
            for i,ln in enumerate(left):
                b = left_states[i]
                ln.state = b
                this_line += to_str(b)
                
            for top_states in combs(len(top)):
                for i,tn in enumerate(top):
                    b = top_states[i]
                    tn.state = b
                
                normal_update(nodes)
                this_line += "|" + " " * (len(top)-1) + to_str(out.state)
            print(this_line)
                
        print("\n")

def show_about_box():
    messagebox.showinfo("About","""Logic GUI
by Benjamin Black
Reed College 2015

Made possible due to donations make by Google.""")
    
Button(MenuFrame,text="Produce File",command=make_file).pack(side=LEFT)
Button(MenuFrame,text="Load File",command=load_file).pack(side=LEFT)
Button(MenuFrame,text="Karnaugh",command=print_karnaugh_maps).pack(side=LEFT)
Button(MenuFrame,text="About",command=show_about_box).pack(side=LEFT)
    
def sel_var_change(*args):
    if SelectTyVar.get() == EVAL_VAL:
        Context.update()
        Context.render()
    else:
        is_updating = False

SelectTyVar.trace("w",sel_var_change)

MenuFrame.pack(side=TOP,fill=X)

VertScrollBar.pack(side=RIGHT,fill=Y)
HorizScrollBar.pack(side=BOTTOM,fill=X)
HorizScrollBar.pack(side=BOTTOM)
canv.pack(side=LEFT)
BodyFrame.pack(side=TOP,fill=BOTH)
top.mainloop()
