COMMANDS:
	PATTERN: python3.4 [interpreter/compiler] [filename.psm]
	INTERPRETERS/COMPILERS:
		GUI_Interp.py 
			brings up a GUI that displays errors and warnings
			on the command line
		text_interp.py
			

FILES:
GUI_

LANGUAGE:

	GUIDE TO MATH 221 PSEUDO-ASSEMBLY 

	Registers: rAX, rBX, rCX, rDX, rSI, rDI, rBP, rSP

	In the below rS means source and rD means destination
	rS can be a register or a constant, rD can only be a register


	Instructions:
		All instructions must have exactly 4 spaces or a tab
		behind it.
		
		push rS         "push"
		rD = pop        "pop"

		out rS          "output"
		rD = in         "input"

		rD = rS         "register-register move"
		rD = -rD        "negate"
		rD = ~rD        "invert"
		rD += rS        "add accumulate"
		rD -= rS        "subtract accumulate"
		rD &= rS        "and ..."
		rD |= rS        "or ..."
		rD ^= rS        "xor ..."
		rD ++           "increment"
		rD --           "decrement"
		rD *= 2			"arithmetic shift left 1"
		rD /= 2			"arithmetic shift right 1"
		rD %= 2         "and accumulate with x0001"

		mem[rD] = rS   "register-to-memory store"
		rD = mem[rD]   "memory-to-register load"

		mem[rD+offset] = rS "register-to-memory store with offset"
		rD = mem[rD+offset] "memory-to-register load with offset"

		goto LABEL          "(unconditional) jump"
		if rD op rS goto LABEL "conditional jump"

		op is one of <, >, <=, >=, ==, !=

		call LABEL   "subroutine call"
		return       "return from subroutine"
		
	Label creation:
		Labels cannot have any spacing before them.
		
		LABEL:			"create label"
