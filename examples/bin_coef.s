.globl main
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
pos_div:
	pushq  	%rBP
	movq  	%rSP,%rBP
	movq  	%rDI,%rCX
	movq  	%rSI,%rDX
	movq  	$0,%rBX
div_loop:
	cmpq  	%rDX,%rCX
	jl  	end_div
	subq  	%rDX,%rCX
	incq  	%rBX
	jmp  	div_loop
end_div:
	movq  	%rBX,%rAX
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
factorial:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	movq  	%rDI,-8(%rBP)
	movq  	$1,-16(%rBP)
fact_loop:
	movq  	-8(%rBP),%rDX
	cmpq  	$0,%rDX
	jle  	end_fact
	movq  	%rDX,%rDI
	movq  	-16(%rBP),%rSI
	callq  	positive_product
	movq  	%rAX,-16(%rBP)
	movq  	-8(%rBP),%rDX
	decq  	%rDX
	movq  	%rDX,-8(%rBP)
	jmp  	fact_loop
end_fact:
	movq  	-16(%rBP),%rAX
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
main:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$32,%rSP
	callq  	input
	movq  	%rAX,-8(%rBP)
	pushq  	%rAX
	callq  	input
	movq  	%rAX,%rBX
	popq  	%rAX
	movq  	%rBX,-16(%rBP)
	movq  	-8(%rBP),%rDI
	callq  	factorial
	movq  	%rAX,-24(%rBP)
	movq  	-16(%rBP),%rDI
	callq  	factorial
	movq  	%rAX,-32(%rBP)
	movq  	-16(%rBP),%rBX
	movq  	-8(%rBP),%rDI
	subq  	%rBX,%rDI
	callq  	factorial
	movq  	%rAX,%rDI
	movq  	-32(%rBP),%rSI
	callq  	positive_product
	movq  	-24(%rBP),%rDI
	movq  	%rAX,%rSI
	callq  	pos_div
	pushq  	%rDI
	movq  	%rAX,%rDI
	callq  	print
	popq  	%rDI
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
