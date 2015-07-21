#returns 0 if edi is prime, nonzero if not prime
Mod:  			# def main():
	 pushq   %rbp			#
	 movq    %rsp, %rbp		#
	 
	 movq    %rdi, %rcx 		# save numerator
	 movq    %rsi, %rdx			#place denomenator
	 #rcx = numnerator is subtracted by denominator over the loop
	 #rdx = denominator
	 #rbx = count
	 movq    $0, %rbx		# count = 0

ModLoop:
	 cmpq    %rdx, %rcx		# if numnerator < denominator go to output
	 jl      KillLoop

	 subq	 %rdx, %rcx		# numnerator -= denominator
	 incq 	%rbx			#count += 1
	 jmp	 ModLoop			#loop here

KillLoop:	
	 movq	%rbp,%rsp
	 popq    %rbp			#
	 ret
IsPrime:
	pushq	%rbp
	movq 	%rsp,%rbp
	subq 	$16,%rsp
	movl	%edi,-8(%rbp) 	#x is transfered
	movl 	%edi,-4(%rbp)	#TryNum is transfered
IsPrimeLoop:
	decl	-4(%rbp)		#TryNum -= 1
	movq	$0,%rdx			#necessary for idiv to work 
	movl	-8(%rbp),%edi	#idiv initialized
	movl	-4(%rbp),%esi		#x / TryNum
	call 	Mod
	cmpl 	$0,%ecx			#if remainder != 0 loop again
	jne		IsPrimeLoop
	
	subl	$1,-4(%rbp)	#turns TryNum into the return value, 0 if prime(last number with no remainder == 0)
	movl 	-4(%rbp),%eax
	movq 	%rbp,%rsp
	popq 	%rbp
	ret
.globl main
main:
	pushq   %rbp
	movq 	%rsp,%rbp
	subq 	$16,%rsp
	call 	input
	movl	%eax,-4(%rbp)	#saves MaxPrime
	movl	$2,-8(%rbp)	#initializes CurPrime
PrimeLoop:
	movl	-4(%rbp),%eax
	cmpl	%eax,-8(%rbp)	#if curprime > maxprime,break
	jg		ExitPrimeLoop
	
	movl	-8(%rbp),%edi
	call 	IsPrime
	cmpl	$0,%eax		#if it is not a prime, continue
	jne		SkipPrint
	
	movl	-8(%rbp),%edi	#print CurPrime
	call 	print
SkipPrint:
	incl	-8(%rbp)
	jmp		PrimeLoop
ExitPrimeLoop:
	movq 	%rbp,%rsp
	popq 	%rbp
	ret

	
	