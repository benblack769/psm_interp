//lib.c
#include <stdio.h>
#include <stdlib.h>
void print_help(long long f){
	printf("%lld\n",f);
}
void print(){
	long long f;
	asm (
	"pushq %%rax\n\
	pushq %%rbx\n\
	pushq %%rcx\n\
	pushq %%rdx\n\
	pushq %%rsi\n\
	pushq %%rdi\n\
	movq  %%rdi,%[f]\n\
	subq  $32,%%rsp" :[f] "=r" (f) : : "rsp");
	print_help(f);
	asm (
	"addq $32,%%rsp \n\
	popq %%rdi \n\
	popq %%rsi \n\
	popq %%rdx\n\
	popq %%rcx\n\
	popq %%rbx\n\
	popq %%rax" : : : "rsp");
}
long long input_help(){		
  long long value;		
  printf("? ");			
  scanf("%lld",&value);	
  return value;
}
void input(){ 	
	asm (			
	"pushq %%rbx\n\
	pushq %%rcx\n\
	pushq %%rdx\n\
	pushq %%rsi\n\
	pushq %%rdi\n\
	subq  $40,%%rsp" : : : "rsp"); 
    long long value = input_help();
	asm (				
	"movq %[value],%%rax\n\
	addq  $40,%%rsp\n\
	popq %%rdi \n\
	popq %%rsi \n\
	popq %%rdx\n\
	popq %%rcx\n\
	popq %%rbx" : : [value] "r" (value): "rsp");
}
void random(){
	long long r = rand();
	asm ("movq %[r],%%rax" : : [r] "r" (r):);
}
//(rDI * rSI)
asm ("prod:");
asm ("movq %rDI,%rAX");
asm ("imulq %rSI,%rSI");
asm ("ret");

//(rDI / rSI)
asm ("quot:");
asm ("push %rDX");
asm ("movq %rDI,%rAX");
asm ("movq $0,%rDX");
asm ("idivq %rSI");
asm ("pop %rDX");
asm ("ret");

//(rDI % rSI)
asm ("mod:");
asm ("push %rDX");
asm ("movq %rDI,%rAX");
asm ("movq $0,%rDX");
asm ("idivq %rSI");
asm ("movq %rDI,%rAX");
asm ("pop %rDX");
asm ("ret");