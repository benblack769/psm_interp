.globl main
main:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	pushq  	%rAX
	callq  	input
	movq  	%rAX,%rDI
	popq  	%rAX
	pushq  	%rAX
	callq  	input
	movq  	%rAX,%rSI
	popq  	%rAX
	callq  	power
	pushq  	%rDI
	movq  	%rAX,%rDI
	callq  	print
	popq  	%rDI
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
positive_product:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	movq  	%rDI,%rBX
	movq  	%rSI,%rCX
	movq  	$0,%rAX
	cmpq  	$0,%rCX
	jle  	end_prod
prod_loop:
	decq  	%rCX
	addq  	%rBX,%rAX
	cmpq  	$0,%rCX
	jg  	prod_loop
end_prod:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
power:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	movq  	%rDI,-8(%rBP)
	movq  	%rSI,-16(%rBP)
	cmpq  	$0,%rSI
	je  	zero_case
	movq  	%rSI,%rBX
	andq  	$1,%rBX
	cmpq  	$1,%rBX
	je  	odd_case
	sarq  	$1,%rSI
	callq  	power
	movq  	%rAX,%rDI
	movq  	%rAX,%rSI
	callq  	positive_product
	jmp  	exit_pow
odd_case:
	subq  	$1,%rSI
	callq  	power
	movq  	-8(%rBP),%rDI
	movq  	%rAX,%rSI
	callq  	positive_product
	jmp  	exit_pow
zero_case:
	movq  	$1,%rAX
exit_pow:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
