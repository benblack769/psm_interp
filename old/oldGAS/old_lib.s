.OutInt:
	.ascii "%d\n\0"
.TempInt:
	.ascii "%d\0"
.globl print
print:
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp
	movl	%edi, 16(%rbp)
	movl	16(%rbp), %edx
	leaq	.OutInt(%rip), %rcx
	call	printf
	leave
	ret
.LC1:
	.ascii "? \0"
.globl input
input:
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$48, %rsp
	leaq	.LC1(%rip), %rcx
	call	printf
	leaq	-4(%rbp), %rax
	movq	%rax, %rdx
	leaq	.TempInt(%rip), %rcx
	call	scanf
	movl	-4(%rbp), %eax
	leave
	ret
.globl randint
randint:
	pushq	%rbp
	movq	%rsp, %rbp
	subq	$32, %rsp
	call	clock
	movl	%eax, %ecx
	call	srand
	call	rand
	leave
	ret
