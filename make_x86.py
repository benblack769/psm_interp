from interp_core import *
import psm_parser
from platform_check import *
regs = {name:Register(name)for name in reg_name_list}
label_locs,comp_lines,to_fnum = psm_parser.parse_all(flines,regs,ProgramState(regs["rBP"],regs["rIP"]),object(),Memory())

assembly_filename = filename[:filename.index(".")] + ".s"

file = open(assembly_filename,"w")

main_name = "_main" if is_mac() else "main"

file.write(".globl " + main_name + "\n")

loc_labels = {num - start_rIP:name for name,num in label_locs.items()}

for n,line in enumerate(comp_lines):
    if n in loc_labels:
        lab_name = main_name if loc_labels[n] == "main" else loc_labels[n]
        
        file.write(lab_name + ":\n")
        
    file.write(line.to_x86() + "\n")
    
file.close()