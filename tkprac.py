#!/usr/bin/python
from tkinter import *

root = Tk()
import tkinter.font as tkFont

list_fonts = list( tkFont.families() )

list_fonts.sort()

for this_family in list_fonts :
    print (this_family)
'''B1 = Button(root)
B2 = Button(root)
B3 = Button(root)
B1.pack(side=LEFT,fill=Y)
B2.pack(side=LEFT,fill=BOTH,expand=1)
B3.pack(side=RIGHT,fill=Y)
root.mainloop()'''