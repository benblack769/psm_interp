.globl main
main:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
	movq  	%rSP,%rSI
place_loop:
	subq  	$16,%rSP
	callq  	input
	cmpq  	$-1,%rAX
	je  	stop_placing
	movq  	%rAX,8(%rSP)
	subq  	$8,%rSI
	callq  	input
	cmpq  	$-1,%rAX
	je  	stop_placing
	movq  	%rAX,(%rSP)
	subq  	$8,%rSI
	jmp  	place_loop
stop_placing:
	movq  	%rSI,-8(%rBP)
	movq  	-8(%rBP),%rDI
	movq  	%rBP,%rSI
	subq  	$16,%rSI
	callq  	sort
user_bin_loop:
	callq  	input
	cmpq  	$-1,%rAX
	je  	quit
	movq  	-8(%rBP),%rDI
	movq  	%rBP,%rSI
	subq  	$16,%rSI
	movq  	%rAX,%rCX
	callq  	bin_search
	pushq  	%rDI
	movq  	%rAX,%rDI
	callq  	print
	popq  	%rDI
	jmp  	user_bin_loop
quit:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
round_8:
	movq  	%rDI,%rAX
	sarq  	$1,%rAX
	sarq  	$1,%rAX
	sarq  	$1,%rAX
	salq  	$1,%rAX
	salq  	$1,%rAX
	salq  	$1,%rAX
	retq
bin_search:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$32,%rSP
	movq  	%rDI,-8(%rBP)
	movq  	%rSI,-16(%rBP)
	movq  	%rCX,-24(%rBP)
	cmpq  	%rSI,%rDI
	jge  	search_failed
	addq  	%rSI,%rDI
	sarq  	$1,%rDI
	callq  	round_8
	movq  	%rAX,%rBX
	movq  	(%rBX),%rDX
	movq  	-24(%rBP),%rCX
	cmpq  	%rDX,%rCX
	je  	search_succeded
	movq  	-8(%rBP),%rDI
	movq  	-16(%rBP),%rSI
	cmpq  	%rDX,%rCX
	jg  	end_assign
	movq  	%rBX,%rSI
	subq  	$8,%rSI
search_call:
	callq  	bin_search
	jmp  	exit
end_assign:
	movq  	%rBX,%rDI
	addq  	$8,%rDI
	jmp  	search_call
search_failed:
	movq  	$0,%rAX
	jmp  	exit
search_succeded:
	movq  	$1,%rAX
exit:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
sort:
	pushq  	%rBP
	movq  	%rSP,%rBP
	subq  	$16,%rSP
outer_loop:
	cmpq  	%rSI,%rDI
	je  	end_sort
	movq  	(%rDI),%rBX
	movq  	%rDI,%rAX
inner_loop:
	addq  	$8,%rAX
	cmpq  	%rSI,%rAX
	je  	end_inner_loop
	movq  	(%rAX),%rDX
	cmpq  	%rDX,%rBX
	jge  	inner_loop
	movq  	%rBX,(%rAX)
	movq  	%rDX,(%rDI)
	movq  	(%rDI),%rBX
	jmp  	inner_loop
end_inner_loop:
	addq  	$8,%rDI
	jmp  	outer_loop
end_sort:
	movq  	%rBP,%rSP
	popq  	%rBP
	retq
