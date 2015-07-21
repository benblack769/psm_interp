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
Radiobutton(MenuFrame,text="Evaluate",variable=SelectTyVar,value=CHANGE_VAL).pack(side=LEFT)

canv = Canvas(top,bg="white")
canv_color = canv["background"]
var = IntVar()

class GateTy(Enum):
    In = 0
    Out = 1
    And = 2
    Or = 3
    XOr = 4
    Not = 5
    
def get_image(s):
    return BitmapImage(file=s+".xbm")
    
GateBMPs = {GateTy.In:get_image("input"),GateTy.Out:get_image("output"),GateTy.And:get_image("and"),GateTy.Or:get_image("or"),GateTy.XOr:get_image("xor"),GateTy.Not:get_image("not")}
ConBMP = get_image("connect")
gate_size = 64
con_size = 25
con_color = "black"
MOUSEX = 0
MOUSEY = 0

evalfns = {GateTy.In:None,GateTy.Out:(lambda Ns:Ns[0].state),GateTy.And:and_eval,GateTy.Or:or_eval,GateTy.XOr:xor_eval,GateTy.Not:(lambda Ns:not Ns[0].state)}

def get_coord(NI,is_input):
    x = NI.x
    if not is_input:
        x += gate_size
    y = NI.y + gate_size // 2
    return x,y

#there might be a python function for this, I don't know
def del_exact_ref(L,I):
    for n,i in enumerate(L):
        if I is i:
            L.pop(n)
            return
            
class Connection_Image(object):
    def __init__(self,start,end):
        self.start = start
        self.end = end
        self.B = Button(canv,image=ConBMP,relief=FLAT,command=self.command,bg=canv_color)
        self.L = self.make_line()
        self.place_button()
        
    def move(self):
        self.reposition_line()
        self.place_button()
    
    def command(self):
        if SelectTyVar.get() != EDIT_VAL:
            return
        start = self.start
        if start.holder.is_busy():
            return
        self.delete()
        start.holder.adopt_float_line(start,MOUSEX,MOUSEY)
        
    def reposition_line(self):
        if self.L == None:
            return
        ix,iy = get_coord(self.start,False)
        ox,oy = get_coord(self.end,True)
        canv.coords(self.L,ix,iy,ox,oy)
        
    def place_button(self):
        if self.B == None:
            return
        ix,iy = get_coord(self.start,False)
        ox,oy = get_coord(self.end,True)
        midx = (ix + ox) // 2
        midy = (iy + oy) // 2
        half_con_s = con_size // 2
        self.B.place(x=midx - half_con_s, y = midy - half_con_s, height = con_size,width=con_size)
        
    def make_line(self):
        ix,iy = get_coord(self.start,False)
        ox,oy = get_coord(self.end,True)
        return canv.create_line(ix,iy,ox,oy,fill=con_color)
    
    def delete(self):
        if self.B == None:   
            return
        del_exact_ref(self.start.out_nodes,self.end)
        del_exact_ref(self.end.in_nodes,self.start)
        del_exact_ref(self.start.in_cons,self)
        del_exact_ref(self.end.out_cons,self)
        
        self.B.destroy()
        canv.delete(self.L)
        self.B = None
        self.L = None
        
class Node_Image(Node):
    def __init__(self,holder,xpix,ypix,GateType):
        super(Node_Image, self).__init__(evalfns[GateType])
        self.type = GateType
        
        if self.type != GateTy.Out:
            self.B_In = Button(canv,command=self.input_click)
        if self.type != GateTy.In:
            self.B_Out = Button(canv,command=self.output_click)
        self.B_Main = Button(canv,image=GateBMPs[self.type],command=self.main_click,bg=canv_color)
        self.in_cons = []
        self.out_cons = []
        self.x = xpix
        self.y = ypix
        self.is_selected = False
        self.holder = holder
        self.move(xpix,ypix)#places it initially
        
    def input_click(self):
        if SelectTyVar.get() == EDIT_VAL and not self.holder.is_busy():   
            self.holder.adopt_float_line(self,MOUSEX,MOUSEY)
            
    def output_click(self):
        if SelectTyVar.get() == EDIT_VAL and self.holder.selec_con_start != None:
            self.holder.place_connection(self)
            
    def main_click(self):
        if SelectTyVar.get() == EDIT_VAL:
            if self.holder.selected == None and self.holder.selec_con_start == None:
                self.holder.select_built(self)
            elif self is self.holder.selected:
                self.holder.place_gate()
        else:#elif SelectTyVar.get() == CHANGE_VAL:
            if self.type == GateTy.In:
                self.state = not self.state
                self.holder.update()
        
    def move(self,x,y):
        self.x = x
        self.y = y
        sm = 10
        bg = gate_size
        y_adj = (bg-sm) // 2
        if self.type != GateTy.Out:
            self.B_In.place(height=sm,width=sm,x=self.x+bg,y=self.y+y_adj)
        if self.type != GateTy.In:
            self.B_Out.place(height=sm,width=sm,x=self.x-sm,y=self.y+y_adj)
        self.B_Main.place(height=bg,width=bg,x=self.x,y=self.y)
        
        for Con in self.in_cons:
            Con.move()
        for Con in self.out_cons:
            Con.move()
        
    def update_color(self):
        if self.state == False:
            color = "red"
        elif self.state == True:
            color = "green"
        else:
            color = "blue"
        
        self.B_Main["bg"] = color
        
    def delete(self):
        for con in self.in_cons+self.out_cons:
            con.delete()

        if self.type != GateTy.Out:
            self.B_In.destroy()
        if self.type != GateTy.In:
            self.B_Out.destroy()
        self.B_Main.destroy()
        self.B_Main = None
        
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
        
    def place_connection(self,EndNode):
        StartNode = self.selec_con_start
        single_input = EndNode.type == GateTy.Out or EndNode.type == GateTy.Not
        if StartNode is not EndNode and \
            StartNode.out_nodes.count(EndNode) == 0 and \
            ((single_input and len(EndNode.in_nodes) < 1) or \
            (not single_input and len(EndNode.in_nodes) < 2)):
            CI = Connection_Image(StartNode,EndNode)
            
            StartNode.out_cons.append(CI)
            StartNode.out_nodes.append(EndNode)
            
            EndNode.in_cons.append(CI)
            EndNode.in_nodes.append(StartNode)
        
        self.selec_con_start = None
        canv.delete(self.con_line)
    
    def select_built(self,Gate):
        del_exact_ref(self.gates,Gate)
        self.selected = Gate
    
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
            g.B_Main["bg"] = canv_color
            for con in g.in_cons:
                if con.B != None:
                    con.B["bg"] = canv_color
        

GH = Gate_Holder()

canv.bind_all('<Motion>', GH.mouse_motion)
canv.bind_all('<Delete>', GH.delete)

def place_button(type):
    def event_handler():
        if SelectTyVar.get() == EDIT_VAL:
            GH.selected = Node_Image(GH,MOUSEX,MOUSEY, type)
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