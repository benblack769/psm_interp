.globl main
callfn:
    pushq   %rBP                      #push rBP
    movq    %rSP,%rBP                 #rBP = rSP
    movq    $0,%rCX                   #rCX = 0
    cmpq    %rCX,%rDI                 
    je      EndRec                    #if rDI == rCX goto EndRec
    decq    %rDI                      #rDI--
    callq   callfn                    #call callfn
EndRec:
    movq    $999,%rCX                 #rCX = 999
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    %rBP,%rSP                 #rSP = rBP
    popq    %rBP                      #rBP = pop
    retq                              #return
    movq    $666,%rAX                 #rAX = 666
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX #this line should never be called
pushsucceed:
    jmp     resume                    #goto resume
pushfail:
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    retq                              #return
main:
    pushq   %rBP                      #push rBP
    movq    %rSP,%rBP                 #rBP = rSP
    subq    $32,%rSP                  #rSP -= 32
    callq   input                     #rAX = in
    pushq   %rAX                      
    subq    $8,%rSP                   
    callq   input                     
    movq    %rAX,%rBX                 
    addq    $8,%rSP                   
    popq    %rAX                      #rBX = in
    pushq   %rAX                      
    subq    $8,%rSP                   
    callq   input                     
    movq    %rAX,%rCX                 
    addq    $8,%rSP                   
    popq    %rAX                      #rCX = in
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    $10,%rBX                  #rBX = 10
    movq    $9,%rAX                   #rAX = 9
    pushq   %rAX                      #push rAX
    movq    (%rSP),%rCX               #rCX = mem[rSP]
    incq    %rCX                      #rCX++
    movq    %rCX,(%rSP)               #mem[rSP] = rCX
    popq    %rAX                      #rAX = pop
    cmpq    %rAX,%rBX                 
    je      pushsucceed               #if rBX == rAX goto pushsucceed
    cmpq    %rAX,%rBX                 
    jne     pushfail                  #if rBX != rAX goto pushfail
resume:
    movq    $5,%rCX                   #rCX = 5
    negq    %rCX                      #rCX = -rCX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    %rCX,%rDI                 #rDI = rCX
    negq    %rDI                      #rDI = -rDI
    notq    %rCX                      #rCX = ~rCX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    %rCX,%rSI                 #rSI = rCX
    movq    $1,%rAX                   #rAX = 1
    subq    %rAX,%rDI                 #rDI -= rAX
    cmpq    %rDI,%rSI                 
    jl      twiddlefail               #if rSI < rDI goto twiddlefail
    cmpq    %rDI,%rSI                 
    jg      twiddlefail               #if rSI > rDI goto twiddlefail
    cmpq    %rDI,%rSI                 
    je      twiddlesucceed            #if rSI == rDI goto twiddlesucceed
twiddlefail:
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rDI,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rDI
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rSI,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rSI
    movq    %rBP,%rSP                 #rSP = rBP
    popq    %rBP                      #rBP = pop
    retq                              #return
twiddlesucceed:
    movq    $63,%rAX                  #rAX = 63
    movq    $100,%rBX                 #rBX = 100
    movq    $99,%rDI                  #rDI = 99
    movq    %rAX,%rCX                 #rCX = rAX
    andq    %rBX,%rCX                 #rCX &= rBX
    movq    %rAX,%rDX                 #rDX = rAX
    xorq    %rBX,%rDX                 #rDX ^= rBX
    movq    %rAX,%rSI                 #rSI = rAX
    orq     %rBX,%rSI                 #rSI |= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rSI,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rSI
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rDX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rDX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rDI,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rDI
    movq    $1,%rAX                   #rAX = 1
    movq    $2,%rBX                   #rBX = 2
    incq    %rAX                      #rAX++
    cmpq    %rBX,%rAX                 
    jle     incNext                   #if rAX <= rBX goto incNext
    cmpq    %rBX,%rAX                 
    jg      incFail                   #if rAX > rBX goto incFail
incNext:
    movq    $50,%rAX                  #rAX = 50
incLoop:
    decq    %rAX                      #rAX--
    cmpq    %rBX,%rAX                 
    jge     incLoop                   #if rAX >= rBX goto incLoop
    jmp     incContinue               #goto incContinue
incFail:
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    retq                              #return
incContinue:
    movq    $5,%rAX                   #rAX = 5
    imulq   $2,%rAX                   #rAX *= 2
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $5,%rAX                   #rAX = 5
    pushq   %rDX                      
    movq    $2,%r8                    
    movq    %rAX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %r8                       
    movq    %rAX,%rAX                 
    popq    %rDX                      #rAX /= 2
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $5,%rAX                   #rAX = 5
    pushq   %rDX                      
    movq    $2,%r8                    
    movq    %rAX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %r8                       
    movq    %rDX,%rAX                 
    popq    %rDX                      #rAX %= 2
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $21,%rBX                  #rBX = 21
    movq    %rBX,(%rSP)               #mem[rSP] = rBX
    movq    %rSP,%rAX                 #rAX = rSP
    movq    $-64,%rDX                 #rDX = -64
    addq    %rDX,%rAX                 #rAX += rDX
    movq    %rBX,-8(%rAX)             #mem[rAX-8] = rBX
    incq    %rAX                      #rAX++
    movq    -9(%rAX),%rAX             #rAX = mem[rAX-9]
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    (%rSP),%rAX               #rAX = mem[rSP]
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $10,%rDI                  #rDI = 10
    callq   callfn                    #call callfn
    movq    $888,%rAX                 #rAX = 888
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $9223372036854775807,%rAX #rAX = 0x7fffffffffffffff
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $5,%rBX                   #rBX = 5
    movq    %rAX,%rCX                 #rCX = rAX
    addq    %rBX,%rCX                 #rCX += rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    $-9223372036854775808,%rCX#rCX = -0x8000000000000000
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    subq    %rAX,%rCX                 #rCX -= rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    addq    %rAX,%rCX                 #rCX += rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    subq    %rBX,%rCX                 #rCX -= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    $5,%rAX                   #rAX = 5
    subq    $-5,%rAX                  #rAX -= -5
    xorq    $12,%rAX                  #rAX ^= 12
    addq    $-12,%rAX                 #rAX += -12
    addq    $0,%rAX                   #rAX += -0
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $123123123123123123,%rAX  #rAX = 123123123123123123
    movq    $321321321321321,%rBX     #rBX = 321321321321321
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rAX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX /= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    imulq   %rBX,%rCX                 #rCX *= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    negq    %rAX                      #rAX = -rAX
    imulq   %rCX,%rCX                 #rCX *= rCX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    negq    %rBX                      #rBX = -rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rDX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX %= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    %rBX,%rCX                 #rCX = rBX
    movq    $-123123,%rAX             #rAX = -123123
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rAX,%r8                  
    movq    %rBX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %r8                       
    movq    %rDX,%rBX                 
    popq    %rDX                      
    popq    %rAX                      #rBX %= rAX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    movq    $123,%rAX                 #rAX = 123
    movq    $10,%rBX                  #rBX = 10
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rAX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX /= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    negq    %rAX                      #rAX = - rAX
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rAX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX /= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    negq    %rBX                      #rBX = -rBX
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rAX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX /= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    negq    %rAX                      #rAX = -rAX
    movq    %rAX,%rCX                 #rCX = rAX
    pushq   %rAX                      
    pushq   %rDX                      
    movq    %rCX,%rAX                 
    movq    $0,%rDX                   
    cqto                              
    idivq   %rBX                      
    movq    %rAX,%rCX                 
    popq    %rDX                      
    popq    %rAX                      #rCX /= rBX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    movq    $-10000000,%rAX           #rAX = -10000000
    salq    $5,%rAX                   #rAX <<= 5
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    sarq    $10,%rAX                  #rAX >>= 10
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    movq    $10,%rBX                  #rBX = 10
    movq    $11,%rCX                  #rCX = 11
    callq   random                    #rAX = rand
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rAX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rAX
    pushq   %rAX                      
    subq    $8,%rSP                   
    callq   random                    
    movq    %rAX,%rCX                 
    addq    $8,%rSP                   
    popq    %rAX                      #rCX = rand
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rCX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rCX
    pushq   %rDI                      
    subq    $8,%rSP                   
    movq    %rBX,%rDI                 
    callq   print                     
    addq    $8,%rSP                   
    popq    %rDI                      #out rBX
    movq    %rBP,%rSP                 #rSP = rBP
    popq    %rBP                      #rBP = pop
    retq                              #return
