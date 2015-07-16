	.file	"lib.c"
	.section .rdata,"dr"
.LC0:
	.ascii "%lld\12\0"
	.text
	.globl	print_help
	.def	print_help;	.scl	2;	.type	32;	.endef
	.seh_proc	print_help
print_help:
	pushq	%rbp
	.seh_pushreg	%rbp
	movq	%rsp, %rbp
	.seh_setframe	%rbp, 0
	subq	$32, %rsp
	.seh_stackalloc	32
	.seh_endprologue
	movq	%rcx, 16(%rbp)
	movq	16(%rbp), %rdx
	leaq	.LC0(%rip), %rcx
	call	printf
	nop
	addq	$32, %rsp
	popq	%rbp
	ret
	.seh_endproc
	.globl	print
	.def	print;	.scl	2;	.type	32;	.endef
	.seh_proc	print
print:
	pushq	%rbp
	.seh_pushreg	%rbp
	movq	%rsp, %rbp
	.seh_setframe	%rbp, 0
	subq	$48, %rsp
	.seh_stackalloc	48
	.seh_endprologue
/APP
 # 9 "../lib.c" 1
	pushq %rax
	pushq %rbx
	pushq %rcx
	pushq %rdx
	pushq %rsi
	pushq %rdi
	movq  %rdi,%rax
	subq  $32,%rsp
 # 0 "" 2
/NO_APP
	movq	%rax, -8(%rbp)
	movq	-8(%rbp), %rax
	movq	%rax, %rcx
	call	print_help
/APP
 # 19 "../lib.c" 1
	addq $32,%rsp 
	popq %rdi 
	popq %rsi 
	popq %rdx
	popq %rcx
	popq %rbx
	popq %rax
 # 0 "" 2
/NO_APP
	nop
	addq	$48, %rsp
	popq	%rbp
	ret
	.seh_endproc
	.section .rdata,"dr"
.LC1:
	.ascii "? \0"
.LC2:
	.ascii "%lld\0"
	.text
	.globl	input_help
	.def	input_help;	.scl	2;	.type	32;	.endef
	.seh_proc	input_help
input_help:
	pushq	%rbp
	.seh_pushreg	%rbp
	movq	%rsp, %rbp
	.seh_setframe	%rbp, 0
	subq	$48, %rsp
	.seh_stackalloc	48
	.seh_endprologue
	leaq	.LC1(%rip), %rcx
	call	printf
	leaq	-8(%rbp), %rax
	movq	%rax, %rdx
	leaq	.LC2(%rip), %rcx
	call	scanf
	movq	-8(%rbp), %rax
	addq	$48, %rsp
	popq	%rbp
	ret
	.seh_endproc
	.globl	input
	.def	input;	.scl	2;	.type	32;	.endef
	.seh_proc	input
input:
	pushq	%rbp
	.seh_pushreg	%rbp
	movq	%rsp, %rbp
	.seh_setframe	%rbp, 0
	subq	$48, %rsp
	.seh_stackalloc	48
	.seh_endprologue
/APP
 # 35 "../lib.c" 1
	pushq %rbx
	pushq %rcx
	pushq %rdx
	pushq %rsi
	pushq %rdi
	subq  $40,%rsp
 # 0 "" 2
/NO_APP
	call	input_help
	movq	%rax, -8(%rbp)
	movq	-8(%rbp), %rax
/APP
 # 43 "../lib.c" 1
	movq %rax,%rax
	addq  $40,%rsp
	popq %rdi 
	popq %rsi 
	popq %rdx
	popq %rcx
	popq %rbx
 # 0 "" 2
/NO_APP
	nop
	addq	$48, %rsp
	popq	%rbp
	ret
	.seh_endproc
	.globl	random
	.def	random;	.scl	2;	.type	32;	.endef
	.seh_proc	random
random:
	pushq	%rbp
	.seh_pushreg	%rbp
	movq	%rsp, %rbp
	.seh_setframe	%rbp, 0
	subq	$48, %rsp
	.seh_stackalloc	48
	.seh_endprologue
	call	rand
	cltq
	movq	%rax, -8(%rbp)
	movq	-8(%rbp), %rax
/APP
 # 54 "../lib.c" 1
	movq %rax,%rax
 # 0 "" 2
/NO_APP
	nop
	addq	$48, %rsp
	popq	%rbp
	ret
	.seh_endproc
/APP
	prod:
	movq %rDI,%rAX
	imulq %rSI,%rSI
	ret
	quot:
	push %rDX
	movq %rDI,%rAX
	movq $0,%rDX
	idivq %rSI
	pop %rDX
	ret
	mod:
	push %rDX
	movq %rDI,%rAX
	movq $0,%rDX
	idivq %rSI
	movq %rDI,%rAX
	pop %rDX
	ret
	.ident	"GCC: (x86_64-win32-seh-rev0, Built by MinGW-W64 project) 5.1.0"
	.def	printf;	.scl	2;	.type	32;	.endef
	.def	scanf;	.scl	2;	.type	32;	.endef
	.def	rand;	.scl	2;	.type	32;	.endef
