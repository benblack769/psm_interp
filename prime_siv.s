.globl main
main:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	callq  	input
	movq  	%rAX,-8(%rBP)
	cmpq  	$1,%rAX
	jle  	exit
	movq  	$1,(%rSP)
	decq  	%rAX
initloop:
	pushq  	$1
	decq  	%rAX
	cmpq  	$0,%rAX
	jge  	initloop
	movq  	$2,%rBX
	movq  	$16,%rCX
mainloop:
	movq  	%rBP,%rSI
	subq  	%rCX,%rSI
	movq  	(%rSI),%rDX
	cmpq  	$0,%rDX
	je  	skip
	pushq  	%rDI
	movq  	%rBX,%rDI
	callq  	print
	popq  	%rDI
elim_composites:
	subq  	%rCX,%rSI
	cmpq  	%rSP,%rSI
	jl  	skip
	movq  	$0,(%rSI)
	jmp  	elim_composites
skip:
	addq  	$8,%rCX
	incq  	%rBX
	movq  	-8(%rBP),%rAX
	cmpq  	%rAX,%rBX
	jle  	mainloop
exit:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
