from tkinter import *
from logic import *
from enum import Enum
top = Tk()

Radio_Height = 70
Radio_Width = 500
SelectTyVar = IntVar()
EDIT_VAL = 1
CHANGE_VAL = 2
MenuFrame = Frame(top,relief=GROOVE,height=Radio_Height,width=Radio_Width)
Radiobutton(MenuFrame,text="Edit",variable=SelectTyVar,value=EDIT_VAL).pack(side=LEFT)
Radiobutton(MenuFrame,text="Change",variable=SelectTyVar,value=CHANGE_VAL).pack(side=LEFT)

canv = Canvas(top,bg="white")
canv_color = canv["background"]

class GateTy(Enum):
    In = 0
    Out = 1
    And = 2
    Or = 3
    XOr = 4
    Not = 5
    
def get_image(s):
    return BitmapImage(file=s+".xbm")
    
GateBMPs = { GateTy.In:get_image("input"),
             GateTy.Out:get_image("output"),
             GateTy.And:get_image("and"),
             GateTy.Or:get_image("or"),
             GateTy.XOr:get_image("xor"),
             GateTy.Not:get_image("not")}

ConBMP = get_image("connect")
gate_size = 50
con_size = 25
con_color = "black"
MOUSEX = 0
MOUSEY = 0

evalfns = {GateTy.In:None,
           GateTy.Out:(lambda Ns:Ns[0].state),
           GateTy.And:and_eval,
           GateTy.Or:or_eval,
           GateTy.XOr:xor_eval,
           GateTy.Not:(lambda Ns:not Ns[0].state)}

class Component(object):
    def __init__(self,xpos,ypos,which,max_inputs,has_outputs=False):

        self.type = which
        self.eval = evalfns[which]
        self.image = GateBMPs[which]

        self.ins = []
        self.outs = []
        self.arity = max_inputs
        self.can_link = has_outputs

        self.x = position.x
        self.y = position.y
        self.width = component_width
        self.height = component_width
        self.is_selected = False

    def input_click(self):
        if SelectTyVar.get() == EDIT_VAL and not self.holder.is_busy():   
            self.holder.adopt_float_line(self,MOUSEX,MOUSEY)
            
    def output_click(self):
        if SelectTyVar.get() == EDIT_VAL and self.holder.selec_con_start != None:
            self.holder.place_link(self)
            
    def main_click(self):
        if SelectTyVar.get() == EDIT_VAL:
            if self.holder.selected == None and self.holder.selec_con_start == None:
                self.holder.selected = self
            elif self is self.holder.selected:
                self.holder.place_gate()
        else:
            if self.type == GateTy.In:
                self.state = not self.state
                self.holder.update()
        
    def place(self,x,y):
        self.x = x
        self.y = y

    def input_x(self):
        return self.x

    def input_y(self):
        return self.y + component_height // 2

    def output_x(self):
        return self.x + component_width

    def output_y(self):
        return self.y + component_height // 2

    def render(self):
        # draw the component
        # ... !

    def color(self):
        if self.state == False:
            return "red"
        elif self.state == True:
            return "green"
        else:
            return "blue"
        
    def delete(self):
        for con in self.ins+self.outs:
            con.delete()

class AndGate(Component):
    def __init__(self,holder,xpos,ypos):
        super(AndGate,self).__init__(self,holder,xpos,ypos,GateTy.And,2)

class OrGate(Component):

class XorGate(Component):

class NotGate(Component):

class InputPin(Component):
    def __init__(self,xpos,ypos):
        super(InputPin,self).__init__(self,xpos,ypos,GateTy.Input,0)

class OutputProbe(Component):
    def __init__(self,xpos,ypos):
        super(OutputProbe,self).__init__(self,xpos,ypos,GateTy.Output,1,False)

class Link(object):
    def __init__(self,start,end):
        self.source = start
        self.target = end
        self.button = Button(canv,image=ConBMP,relief=FLAT,command=self.command,bg=canv_color)
        self.line = self.make_line()
        self.place_button()
        
    def move(self):
        self.reposition_line()
        self.place_button()
    
    def command(self):
        if SelectTyVar.get() != EDIT_VAL:
            return
        start = self.source
        if start.holder.is_busy():
            return
        self.delete()
        start.holder.adopt_float_line(start,MOUSEX,MOUSEY)
        
    def reposition_line(self):
        if self.line == None:
            return
        ix,iy = get_coord(self.source,False)
        ox,oy = get_coord(self.target,True)
        canv.coords(self.line,ix,iy,ox,oy)
        
    def place_button(self):
        if self.button == None:
            return
        ix,iy = get_coord(self.source,False)
        ox,oy = get_coord(self.target,True)
        midx = (ix + ox) // 2
        midy = (iy + oy) // 2
        half_con_s = con_size // 2
        self.button.place(x=midx - half_con_s, y = midy - half_con_s, height = con_size,width=con_size)
        
    def make_line(self):
        ix,iy = get_coord(self.source,False)
        ox,oy = get_coord(self.target,True)
        return canv.create_line(ix,iy,ox,oy,fill=con_color)
    
    def delete(self):
        del_exact_ref(self.start.ins,self)
        del_exact_ref(self.target.outs,self)
        



class Gate_Holder(object):
    def __init__(self):
        self.gates = []
        self.selected = None
        self.selec_con_start = None
        self.con_line = None
        
    def place_gate(self):
        self.gates.append(self.selected)
        self.selected = None
        
    def is_busy(self):
        return bool(self.selected) or bool(self.selec_con_start)
        
    def adopt_float_line(self,start,xpos,ypos):
        self.selec_con_start = start
        xs,ys = get_coord(start,False)
        self.con_line = canv.create_line(xpos,ypos,xs,ys,fill=con_color)
        
    def place_link(self,EndNode):
        StartNode = self.selec_con_start
        single_input = EndNode.type == GateTy.Out or EndNode.type == GateTy.Not
        if StartNode is not EndNode and \
            StartNode.out_nodes.count(EndNode) == 0 and \
            ((single_input and len(EndNode.in_nodes) < 1) or \
            (not single_input and len(EndNode.in_nodes) < 2)):
            CI = Link_Image(StartNode,EndNode)
            
            StartNode.outs.append(CI)
            StartNode.out_nodes.append(EndNode)
            
            EndNode.ins.append(CI)
            EndNode.in_nodes.append(StartNode)
        
        self.selec_con_start = None
        canv.delete(self.con_line)
        
    def mouse_motion(self,event):
        if SelectTyVar.get() != EDIT_VAL:
            return
        global MOUSEX,MOUSEY
        MOUSEX = event.x_root - canv.winfo_rootx()
        MOUSEY = event.y_root - canv.winfo_rooty()
        #MOUSEX, MOUSEY = event.x_root , event.y_root - Radio_Height - gate_size // 2
        if self.selected != None:
            self.selected.move(MOUSEX-gate_size//2, MOUSEY-gate_size//2)
        elif self.selec_con_start != None:
            sx,sy = get_coord(self.selec_con_start,False)
            canv.coords(self.con_line,sx,sy,MOUSEX,MOUSEY)
            
    def update(self):
        for n in self.gates:
            if n.type != GateTy.In:
                n.state = None
        update(self.gates)
        for g in self.gates:
            g.update_color()
    
    def delete(self,event):  
        if SelectTyVar.get() != EDIT_VAL:
            return
        elif self.selected:
            self.selected.delete()
            del_exact_ref(self.gates,self.selected)
            self.selected = None
        elif self.selec_con_start:
            self.selec_con_start = None
            canv.delete(self.con_line)
            self.con_line = None
    
    def clear_color(self):
        for g in self.gates:
            g.button_Main["bg"] = canv_color
            for con in g.ins:
                if con.button != None:
                    con.button["bg"] = canv_color
        

GH = Gate_Holder()

canv.bind_all('<Motion>', GH.mouse_motion)
canv.bind_all('<Delete>', GH.delete)

def place_button(type):
    def event_handler():
        if SelectTyVar.get() == EDIT_VAL:
            GH.selected = Node_Image(GH,gate_size // 2, 0, type)
    Button(MenuFrame,image=GateBMPs[type],command=event_handler).pack(side=LEFT)
    
place_button(GateTy.In)
place_button(GateTy.Out)
place_button(GateTy.Not)
place_button(GateTy.Or)
place_button(GateTy.And)
place_button(GateTy.XOr)

def var_change(*args):
    if SelectTyVar.get() == EDIT_VAL:
        GH.clear_color()
    else:
        GH.update()

SelectTyVar.trace("w",var_change)

MenuFrame.place(x=0,y=0,width=Radio_Width,height=Radio_Height)

canv.place(x=0,y=Radio_Height,width=5000,height=5000)
top.mainloop()
