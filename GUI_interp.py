from interp_core import *
from tkinter import *
from tkinter import font
from idlelib.WidgetRedirector import WidgetRedirector
from platform_check import *
import psm_parser

    
def write_change(Lab):
    Lab["relief"] = SUNKEN
def read_change(Lab):
    Lab["relief"] = RAISED
def reset(Lab):
    Lab["relief"] = FLAT
def goto_active_mode(Lab):
    Lab["relief"] = RIDGE

if is_mac():
    font_size = 18
else:
    font_size = 12
    
num_font = ("Courier",font_size)
code_font = ("Courier",font_size)
label_font = ("Lucida Calligraphy",font_size)
line_num_font = ("Courier",font_size)

def get_all_children(parent):
    children = [parent]
    for child in parent.children.values():
        children += get_all_children(child)
    return children
            
#taken from: http://tkinter.unpythonic.net/wiki/ReadOnlyText
class ReadOnlyText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
         
#taken from http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)
        
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
        self.scroll_canvas = canvas
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width() +1000)
        canvas.bind('<Configure>', _configure_canvas)
        
        self.bind('<Configure>', _configure_canvas)
        
    def config_mousewheel(self):
        def _on_mousewheel(event):
            self.scroll_canvas.yview_scroll(-1*(event.delta//80), "units")
            
        for child in get_all_children(self):
            if is_windows():
                child.bind("<MouseWheel>",_on_mousewheel)
            else:
                child.bind("<Button-4>",_on_mousewheel)
                child.bind("<Button-5>",_on_mousewheel)
    
class TextLine(object):
    def __init__(self,Master,line,label_locs):
        self.info = dict()#is a dictionary from names to lists
        self.data = []

        line = psm_parser.remove_comment(line).strip()
        self.line = line
        while True:
            min_pos = 1000000000
            min_name = None
            for this_name in reg_name_list + ["mem"]:
                if this_name in line:
                    pos = line.index(this_name)
                    if min_pos > pos:
                        min_pos = pos
                        min_name = this_name
                    
            if min_name == None:
                break
                
            if min_pos != 0:
                self.data.append(line[:min_pos])
            
            if min_name == "mem":
                word = line[min_pos : line.index("]") + 1]
            else:
                word = min_name
                
            size = len(word)
            
            loc = len(self.data)
            self.data.append(word)
            if min_name in self.info:
                self.info[min_name].append(loc)
            else:
                self.info[min_name] = [loc]
            
            line = line[min_pos + size:]
            
        if "goto" in line:
            goto_loc = line.index("goto")
            goto_lab = line[goto_loc + 4:].strip()
            self.data.append(line[:goto_loc])
            self.data.append(line[goto_loc:goto_loc+5])
            
            self.info["goto"] = [len(self.data)]
            self.data.append(hex(label_locs[goto_lab]))
            
        elif line:
            self.data.append(line)
        
        self.frame = Frame(Master)
        self.labels = [Label(self.frame,bd=2,text=d,font=code_font) for d in self.data]
        
    def grid(self,y,x):
        for n,l in enumerate(self.labels):
            l.pack(side=LEFT)
        self.frame.grid(row=y,column=x,sticky="NWSE")
          
    def set_mem(self):
        self.set_reg("mem")
        
    def get_mem(self):
        self.get_reg("mem")
        
    def set_reg(self,name):
        if name in self.info:
            for d in self.info[name]:
                write_change(self.labels[d])
            
    def get_reg(self,name):
        if name in self.info:
            for d in self.info[name]:
                read_change(self.labels[d])
    
    def read_goto(self):
        if "goto" in self.info:
            goto_active_mode(self.labels[self.info["goto"][0]])
            
    def reset(self):
        for l in self.labels:
            reset(l)
            
class CareSelect(object):
    to_colors = {0:"red",1:"yellow",2:"green"}
    def __init__(self,Master):
        self.care_setting = 2
        sq_size = TextGraphicLine.sq_size
        self.frame = Frame(Master)
        self.care_canv = Canvas(self.frame,height=sq_size,width=sq_size)
        self.care_canv.bind("<Button-1>",lambda event:self.rotate_care())
        self.draw_care()
    def grid(self, y, x):
        self.care_canv.pack(side=RIGHT)
        self.frame.grid(row=y,column=x,sticky="NSWE")
    def draw_care(self):
        self.care_canv.delete("ALL")
        sq_size = TextGraphicLine.sq_size
        startpos = sq_size // 4 + 3
        end_pos = (sq_size * 3) // 4 + 4
        self.care_canv.create_oval(startpos,startpos - 2,end_pos,end_pos - 2,fill=CareSelect.to_colors[self.care_setting])
    def rotate_care(self):
        self.care_setting += 1
        self.care_setting %= 3
        self.draw_care()
    def is_break(self):
        return self.care_setting == 0
    def is_pause(self):
        return self.care_setting == 1
        
class TextGraphicLine(object):
    sq_size = 15
    def __init__(self,Master,line,line_num,label_locs):
        self.arr_frame = Frame(Master)
        self.arr_canv = Canvas(self.arr_frame,height=TextGraphicLine.sq_size,width=TextGraphicLine.sq_size)
        self.care_g = CareSelect(Master)
        self.text = TextLine(Master,line,label_locs)
        
        self.line_num = line_num
        
        self.lab_frame = Frame(Master)
        self.label_g = Label(self.lab_frame,text=hex(line_num + start_rIP),font=line_num_font)
        
    def grid(self):
        self.arr_canv.pack(side=RIGHT)
        self.label_g.pack(side=RIGHT)
        self.lab_frame.grid(row=self.line_num,column=0,sticky="NSWE")
        self.arr_frame.grid(row=self.line_num,column=1,sticky ="NSWE")
        self.care_g.grid(self.line_num,2)
        self.text.grid(self.line_num,3)
        
    def get_grid_collum_sizes(self):
        return (self.lab_frame.winfo_width(),self.arr_frame.winfo_width(),self.care_g.frame.winfo_width(),self.text.frame.winfo_width())
        
    def highlight_label(self):
        goto_active_mode(self.label_g)
        
    def activate(self):
        arrow_coords = (0,5,8,5,8,0,15,7,8,15,8,10,0,10)
        self.arr_canv.create_polygon(*arrow_coords,fill="brown")
        self.text.read_goto()
            
    def reset(self):
        self.arr_canv.delete(ALL)
        self.text.reset()
        reset(self.label_g)
   
class TextGraphic(object):
    def __init__(self,Master,to_fnum,label_locs,is_follow_mode):
        self.frame = Frame(Master,relief=GROOVE,bd=2)
        self.header = Frame(self.frame,relief=RAISED,bd=2)
        self.arr_header = Label(self.header,text="A")
        self.care_header = Label(self.header,text="B")
        self.text_header = Label(self.header,text="Text")
        self.label_header = Label(self.header,text="Label")
        
        self.body = VerticalScrolledFrame(self.frame)
        active_lines = [None] * len(to_fnum)
        for comp_n,file_n in to_fnum.items():
            active_lines[comp_n - start_rIP] = flines[file_n]
            
        self.lines = [TextGraphicLine(self.body.interior,line,num,label_locs) for num,line in enumerate(active_lines)]
        
        self.body.config_mousewheel()
        
        is_follow_mode.set(True)
        is_follow_mode.trace("w",lambda *args:M.move_text_to_instruc())
        self.is_follow_mode = is_follow_mode
        
    def pack(self):        
        self.header.pack(side=TOP,fill=X)
        
        for l in self.lines:
            l.grid()
            
        self.body.pack(side=TOP,expand=True,fill=BOTH)
        
        self.label_header.grid(row=0,column=0,sticky="NW")
        self.arr_header.grid(row=0,column=1,sticky="NW")
        self.care_header.grid(row=0,column=2,sticky="NW")
        self.text_header.grid(row=0,column=3,sticky="NW")
        
        self.body.update_idletasks()
        
        row_sizes = self.lines[0].get_grid_collum_sizes()
        
        for n in range(4):
            self.header.grid_columnconfigure(n,minsize=row_sizes[n])
        
        self.frame.pack(side=LEFT,fill=BOTH,expand=True)
        
    def center_on(self,rIP):
        if self.is_follow_mode.get():
            #moves the center of the veiw to the current instruction
            move_loc = rIP.val.int - start_rIP
            line_size = self.lines[0].arr_frame.winfo_height() 
            place_spot = move_loc * line_size - self.body.winfo_height() / 2
            totsize = len(self.lines) * line_size
            fraction = place_spot / totsize
            
            self.body.scroll_canvas.yview("moveto",fraction)
            
    def highlight_label(self,line_num):
        self.lines[line_num - start_rIP].highlight_label()
    
    def reset_all(self):
        for t_l in self.lines:
            t_l.reset()
        
    def is_break(self,num):
        return self.lines[num - start_rIP].care_g.is_break()
        
    def is_pause(self,num):
        return self.lines[num - start_rIP].care_g.is_pause()
    
    def activate_line(self,line_num,mem_get,mem_set,reg_gets,reg_sets):
        line_g = self.lines[line_num - start_rIP]
        line_g.activate()
        line = line_g.text
        if mem_set:
            line.set_mem()
        if mem_get:
            line.get_mem()
        for name in reg_sets:
            line.set_reg(name)
        for name in reg_gets:
            line.get_reg(name)
            
class GUI_Register(Register):
    def __init__(self,Master,name,HexVar):
        Register.__init__(self,name)
        self.gotten = False
        self.was_set = False
        self.IsHexVar = HexVar
        self.name_lab = Label(Master,text=name + ".",font=num_font)
        self.val_lab = Label(Master,text=self.to_str(),font=num_font)
        
    def grid(self,n):
        self.name_lab.grid(row=n,column=0)
        self.val_lab.grid(row=n,column=1,sticky="NW")
        
    def to_str(self):
        return self.val.to_str(self.IsHexVar.get())
        
    def set(self,new_val):
        if M.is_changing:
            Register.set(self,new_val)
        else:
            self.was_set = True
            self.gotten = False
        
    def get(self):
        if M.is_changing:
            return Register.get(self)
        else:
            self.gotten = True
            self.was_set = False
            return Register.get(self)
        
    def redraw(self):
        self.val_lab.config(text=self.to_str())
        
    def write_mode(self):
        write_change(self.val_lab)
        
    def read_mode(self):
        read_change(self.val_lab)
        
    def reset_mode(self):
        self.gotten = False
        self.was_set = False
        reset(self.val_lab)
    
class RegisterGraphics(object):
    def __init__(self,Master,HexVar):
        self.frame = Frame(Master,relief=GROOVE,bd=2)
        self.regs = {name : GUI_Register(self.frame,name,HexVar) for name in reg_name_list}
        
    def pack(self):
        for n,name in enumerate(reg_name_list):
            self.regs[name].grid(n)
        self.frame.pack(fill=BOTH)
        
    def get_read_write_regs(self):
        reads = []
        writes = []
        for name,reg in self.regs.items():
            if reg.gotten:
               reads.append(name)
            if reg.was_set:
                writes.append(name)
        return reads,writes
        
    def redraw_all(self):
        for name,reg in self.regs.items():
            reg.redraw()
    
    def reset_all(self):
        for name,reg in self.regs.items():
            reg.reset_mode()
        
class GUI_MemLine(DataSegment):
    def __init__(self,Master,ptr_str,HexVar):
        DataSegment.__init__(self)
        self.IsHexVar = HexVar
        self.spot_lab = Label(Master,text=ptr_str,font=line_num_font)
        self.data_lab = Label(Master,text=self.to_str(),font=num_font)
        self.was_set = False
        self.gotten = False
        self.reg_ptr_lab = Label(Master,font=label_font)
        
    def grid(self,y):
        self.reg_ptr_lab.grid(row=y,column=0,sticky="NE")
        self.spot_lab.grid(row=y,column=1,sticky="NW")
        self.data_lab.grid(row=y,column=2,sticky="NW")
    
    def to_str(self):
        return self.val.to_str(self.IsHexVar.get())
        
    def redraw(self):
        self.data_lab.config(text=self.to_str())
        
    def read_mode(self):
        read_change(self.data_lab)
    
    def write_mode(self):
        write_change(self.data_lab)
        
    def reset_mode(self):
        reset(self.data_lab)
        self.was_set = False
        self.gotten = False
   
    def reset_ptr_lab(self):
        if self.reg_ptr_lab.cget("text"):
            self.reg_ptr_lab.config(text="")
        
    def make_stack(self):
        self.data_lab["fg"] = "black"
        
    def make_below(self):
        self.data_lab["fg"] = "grey"
        
    def make_above(self):
        self.data_lab["fg"] = "brown"
        
    def write_ptr(self,name):
        self.reg_ptr_lab.config(text=name)
        
    def set(self,new_val):
        if M.is_changing:
            DataSegment.set(self,new_val)
        else:
            self.was_set = True
            self.gotten = False
        
    def get(self):
        if M.is_changing:
            return DataSegment.get(self)
        else:
            self.was_set = False
            self.gotten = True
            return DataSegment.get(self)
        
class GUI_Memory(Memory):
    def __init__(self,Master,HexVar,is_follow_mode):
        Memory.__init__(self)
        
        self.data_frame = VerticalScrolledFrame(Master,relief=GROOVE,bd=2)
        self.data = [GUI_MemLine(self.data_frame.interior,hex((self.start_loc - n * 8) & 0xffff)[2:],HexVar) for n in range(self.max_size)]
        
        self.choice_frame = Frame(Master)
        self.int_choice = Checkbutton(self.choice_frame,text="ints as hex",variable=HexVar)
        
        self.is_stack_mode = BooleanVar()
        self.stack_mode = Checkbutton(self.choice_frame,text="follow rSP",variable=self.is_stack_mode)
        self.follow_inst_m = Checkbutton(self.choice_frame,text="follow rIP",variable=is_follow_mode)
        self.is_stack_mode.set(False)
        self.is_stack_mode.trace("w",lambda *args:M.change_reg_ptr_graphic())
        self.data_frame.config_mousewheel()
        
    def pack(self):
        for n,d in enumerate(self.data):
            d.grid(n)
        self.data_frame.pack(expand=True,fill=Y)
        
        self.int_choice.pack(side=LEFT)
        
        self.stack_mode.pack(side=LEFT)
        
        self.follow_inst_m.pack(side=LEFT)
        
        self.choice_frame.pack(side=BOTTOM)
        
    def get_read_write_spots(self):
        reads = []
        writes = []
        for n,mem in enumerate(self.data):
            if mem.gotten:
               reads.append(n)
            if mem.was_set:
                writes.append(n)
        return reads,writes
        
    def adjust_stack_frame(self,rSP,rBP):
        for ml in self.data:
            ml.reset_ptr_lab()
        
        rSP_spot = self.ref_to_data(rSP.val.int)
        rBP_spot = self.ref_to_data(rBP.val.int)
        
        in_range = lambda x : 0 <= x < self.max_size
        if in_range(rSP_spot):
            self.data[rSP_spot].write_ptr("rSP")
        if in_range(rBP_spot):
            self.data[rBP_spot].write_ptr("rBP")
        
        viable = lambda x : 0 if x < 0 else (self.max_size - 1 if x >= self.max_size else x)
        if rBP_spot <= rSP_spot:
            for n in range(viable(rBP_spot)):
                self.data[n].make_above()
        else:
            for n in range(viable(rBP_spot)):
                self.data[n].make_stack()
                
        for n in range(viable(rBP_spot),viable(rSP_spot + 1)):
            self.data[n].make_stack()
        for n in range(viable(rSP_spot + 1),self.max_size):
            self.data[n].make_below()
        
        if self.is_stack_mode.get():
            #moves the view to the middle of the stack frame
            mem_move_loc = (self.ref_to_data(rSP.val.int) + self.ref_to_data(rBP.val.int)) / 2
            if 0 <= mem_move_loc < self.max_size:
                slotsize = self.data[0].data_lab.winfo_height() 
                place_spot = mem_move_loc * slotsize - self.data_frame.winfo_height() / 2
                totsize = self.max_size * slotsize
                fraction = place_spot / totsize
                
                self.data_frame.scroll_canvas.yview("moveto",fraction)
            
    def redraw(self):
        for d in self.data:
            d.redraw()
            
    def reset(self):
        for part in self.data:
            part.reset_mode()

class ConsoleGraphic(object):
    def __init__(self,Master):
        self.frame = Frame(Master)
        self.text_frame = Frame(self.frame,relief=SUNKEN,bd=2)
        self.text_scroll = Scrollbar(self.text_frame)
        self.text = ReadOnlyText(self.text_frame,yscrollcommand=self.text_scroll.set,width=20)
        self.text_scroll.config(command=self.text.yview_scroll)
        self.entry = Entry(self.frame,bg="red",disabledbackground="gray")
        self.entry.bind_all("<Return>",self.enter_hit)
        self.entry.config(state=DISABLED)
        #callback fn is copied when querry_input is called
        self.in_callback = None
        self.text.insert(END,"\nconsole:\n\n")
        
    def pack(self):
        self.text.pack(side=LEFT)
        self.text_scroll.pack(side=RIGHT,fill=Y)
        self.text_frame.pack()
        self.entry.pack(fill=X)
        self.frame.pack()
        
    def console_restart(self):
        self.print_line("console: \n\n")
        
    def is_inputting(self):
        return bool(self.in_callback)
        
    def enter_hit(self,event):
        in_str = self.entry.get()
        self.entry.delete(0,len(in_str))
        if in_str:
            try:
                int(in_str)
            except ValueError:
                self.print_line("invalid input!")
            else:
                self.print_line("? " + in_str)
                self.entry.config(state=DISABLED)
                
                self.in_callback(in_str)
            
            
    def print_line(self,Str):
        #self.text.config(state=NORMAL)
        self.text.insert(END,"\n" + str(Str))
        self.text.yview_moveto(1.0)
        self.text.update_idletasks()
        #self.text.config(state=DISABLED)
        
    def place_input_into(self,input_reg):
        if M.is_changing:
            def input_callback(in_str):
                #it has already been checked for being an iteger
                input_reg.val = int_val(truncate(int(in_str)))
                   
                self.in_callback = None
                M.state.resume()
                
            self.in_callback = input_callback
            self.entry.config(state=NORMAL)
        else:
            input_reg.set(0)
        
    def print_val(self,val):
        if M.is_changing:
            self.print_line(str(val.int))
    
    def restart(self):
        self.console_restart()
        if self.is_inputting():
            self.entry.delete(0,len(self.entry.get()))
            self.entry.config(state=DISABLED)
            self.in_callback = None
                 
class GUI_State(ProgramState):
    def __init__(self,Master,M,*args):  
        ProgramState.__init__(self,*args)
        
        self.frame = Frame(Master)
        self.b_frame = Frame(self.frame)
        self.run_b = Button(self.b_frame,text="Run",command=self.run)
        self.step_b = Button(self.b_frame,text="Step",command=self.step)
        self.next_b = Button(self.b_frame,text="Next",command=self.next)
        self.restart_b = Button(self.b_frame,text="Restart",command=M.restart)
        
        self.speed_bar = Scale(self.frame,from_=0.5,to=5,resolution=0.1,label="Speed",orient=HORIZONTAL)
        self.speed_bar.set(2.0)
        
        self.possible_jmp = None
        self.is_running = False
        
        self.exited = False
        
    def pack(self):        
        self.run_b.pack(side=LEFT)
        self.step_b.pack(side=LEFT)
        self.next_b.pack(side=LEFT)
        self.restart_b.pack(side=LEFT)
        self.b_frame.pack(side=TOP)
        
        self.speed_bar.pack(side=TOP)
        
        self.frame.pack(side=TOP,fill=X)
        
    def poke(self):
        M.is_changing = True
        ret_val = ProgramState.poke(self)
        M.is_changing = False
        return ret_val
        
    def is_not_runnable(self):
        return self.exited or M.cons_g.is_inputting()
    
    def run(self):
        self.is_running = True
        ProgramState.run(self)
    
    def upon_exit(self):
        self.is_running = False
        M.reset()
        M.redraw()
        self.exited = True
        
    def upon_break(self):
        instruc = self.rIP.val.int
        if M.cons_g.is_inputting():
            #the previous line is still executing here
            M.represent_instruc(instruc-1)
        elif M.text_g.is_break(instruc) or self.next_break == instruc:
            M.represent_instruc(instruc)
            self.is_running = False
        elif M.text_g.is_pause(instruc):
            M.represent_instruc(instruc)
            wait_time = int(1000 / self.speed_bar.get())
            M.root.after(wait_time,self.resume)
        else:
            M.represent_instruc(instruc)
        
    def is_break(self):
        instruc = self.rIP.val.int
        return M.text_g.is_break(instruc) or \
                self.next_break == instruc or \
                M.text_g.is_pause(instruc) or \
                M.cons_g.is_inputting()
        
    def resume(self):
        if self.is_not_runnable():
            return
        M.represent_instruc(self.rIP.val.int)
        if self.is_running:
            self.run()
        
    def jmp_to(self,loc,will_jump):
        if M.is_changing:
            ProgramState.jmp_to(self,loc,will_jump)
        else:
            self.possible_jmp = loc.int
            
    def reset(self):
        self.possible_jmp = None
    
class GUI_Controller(object):
    def __init__(self):
        self.root = Tk()
        self.root.title("psm Interpreter(" + filename + ")")
        self.def_color = self.root["bg"]
        
        self.is_changing = False
        
        self.IsHexVar = IntVar(self.root)
        self.IsHexVar.set(0)
        self.IsHexVar.trace("w",lambda *args:self.redraw())
        
        center_on_instruc_var = IntVar(self.root)
        
        self.mem_reg_frame = Frame(self.root)
        self.mem_g = GUI_Memory(self.mem_reg_frame,self.IsHexVar,center_on_instruc_var)
        self.reg_g = RegisterGraphics(self.mem_reg_frame,self.IsHexVar)
        
        self.inter_frame = Frame(self.root)
        
        regs = self.registers()
        self.state = GUI_State(self.inter_frame,self,regs["rBP"],regs["rIP"])
        self.cons_g = ConsoleGraphic(self.inter_frame)
        self.label_locs,exprs,to_fnum = psm_parser.parse_all(flines,regs,self.state,self.cons_g,self.mem_g)
        
        self.text_g = TextGraphic(self.root,to_fnum,self.label_locs,center_on_instruc_var)
        
        init_all(self.registers(),self.mem_g,self.state,self.label_locs,exprs,to_fnum)
        
        self.pack()
        
    def pack(self):
        self.reg_g.pack()
        self.mem_g.pack()
        self.mem_reg_frame.pack(side=LEFT,fill=Y)
        
        self.state.pack()
        self.cons_g.pack()
        self.inter_frame.pack(side=RIGHT,fill=Y)
        
        self.text_g.pack()
        
    def represent_instruc(self,line_num):
        self.reset()
        self.state.exprs[line_num - start_rIP].eval()
        
        self.change_reg_ptr_graphic()
        
        read_regs,write_regs = self.reg_g.get_read_write_regs()
        for name in read_regs:
            self.read_reg_graphic(name)
        for name in write_regs:
            self.write_reg_graphic(name)
            
        read_mems,write_mems = self.mem_g.get_read_write_spots()
        for spot in read_mems:
            self.read_mem_graphic(spot)
        for spot in write_mems:
            self.write_mem_graphic(spot)
        
        if self.state.possible_jmp != None:
            self.text_g.highlight_label(self.state.possible_jmp)
            
        self.text_g.activate_line(line_num,bool(read_mems),bool(write_mems),read_regs,write_regs)
        
        self.redraw()
        
        self.move_text_to_instruc()
    
    def redraw(self):
        self.reg_g.redraw_all()
        self.mem_g.redraw()
                
    def read_reg_graphic(self,name):
        self.get_reg(name).read_mode()
    def write_reg_graphic(self,name):
        self.get_reg(name).write_mode()
    def read_mem_graphic(self,spot):
        self.get_memline(spot).read_mode()
    def write_mem_graphic(self,spot):
        self.get_memline(spot).write_mode()
    def alert_label_graphic(self,line_num):
        self.text_g.highlight_mode(line_num)
    def change_reg_ptr_graphic(self):
        self.mem_g.adjust_stack_frame(self.get_reg("rSP"),self.get_reg("rBP"))
    def move_text_to_instruc(self):
        self.text_g.center_on(self.get_reg("rIP"))
    def get_memline(self,spot):
        return self.mem_g.data[spot]
    def get_reg(self,name):
        return self.registers()[name]
    def registers(self):
        return self.reg_g.regs
    def reset(self):
        self.state.reset()
        
        self.mem_g.reset()
        self.reg_g.reset_all()
        self.text_g.reset_all()
        
    def restart(self):
        init_all(self.registers(),self.mem_g,self.state,self.label_locs,self.state.exprs,self.state.to_fnum)
        self.cons_g.restart()
        self.represent_instruc(self.state.rIP.val.int)
        self.state.exited = False

M = GUI_Controller()
M.root.update_idletasks()
M.represent_instruc(M.state.rIP.val.int)
M.root.mainloop()