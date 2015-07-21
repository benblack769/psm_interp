from tkinter import *

top = Tk()
canv = Canvas(top)
var = IntVar()
def sel():
   selection = "You selected the option " + str(var.get())
   label.config(text = selection)
BITMAP = """
#define im_width 1
#define im_height 1
static char im_bits[] = { 0x54 };
"""
    
bmp = BitmapImage(data=BITMAP)
class Gate_Image(object):
    def __init__(self,xpix,ypix,main_image):
        self.B_In = Button(canv,image=bmp,command=self.input_click)
        self.B_Out = Button(canv,image=bmp,command=self.output_click)
        self.B_Main = Button(canv,image=main_image,command=self.main_click)
        self.x = xpix
        self.y = ypix
        self.is_selected = False
        self.draw()
    def input_click(self):
        asdas = 0x54
    def output_click(self):
        asdasd=34
    def main_click(self):
        line = canv.create_line(10,10,500,500,fill="black")
        canv.scale(line, 0, 0, 1.5, 2)
        print("outch!")
    def draw(self):
        sm = 7
        bg = 50
        y_adj = (bg-sm) // 2
        self.B_In.place(height=sm,width=sm,x=self.x-sm,y=self.y+y_adj)
        self.B_Out.place(height=sm,width=sm,x=self.x+bg,y=self.y+y_adj)
        self.B_Main.place(height=bg,width=bg,x=self.x,y=self.y)

        
or_bitmap = PhotoImage(file="or.gif")
gi = Gate_Image(10,10,or_bitmap)
gi = Gate_Image(70,70,or_bitmap)
canv.create_rectangle(100,200,200,300,fill="black")

canv.place(x=0,y=0,width=5000,height=5000)
top.mainloop()