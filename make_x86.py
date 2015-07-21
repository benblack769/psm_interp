"""
produces an filename.s file with x86 instructions that can be
compiled with gcc and lib.s. 
"""
from interp_core import *
import psm_parser
from platform_check import *

regs = {name:Register(name)for name in reg_name_list}
label_locs,comp_lines,to_fnum = psm_parser.parse_all(flines,regs,ProgramState(regs["rBP"],regs["rIP"]),object(),Memory(regs["rSP"]))

assembly_filename = filename[:filename.index(".")] + ".s"

file = open(assembly_filename,"w")

#necessary gcc framework 
main_name = "main" if is_gcc() else "_main"
file.write(".globl " + main_name + "\n")

#map from comp_lines indices to label names
loc_labels = {num - start_rIP:name for name,num in label_locs.items()}

for n,line in enumerate(comp_lines):
    if n in loc_labels:
        lab_name = main_name if loc_labels[n] == "main" else loc_labels[n]
        
        file.write(lab_name + ":\n")
    
    file.write(line.to_x86() + "#" + flines[to_fnum[n + start_rIP]].strip() + "\n")
    
file.close()