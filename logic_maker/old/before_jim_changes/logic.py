class Node(object):
    def __init__(self,eval):
        self.in_nodes = []
        self.out_nodes = []
        self.state = False
        self.eval_fn = eval
    def eval(self):
        if self.in_nodes:
            self.state = self.eval_fn(self.in_nodes)
            
def and_eval(InNodes):
    if not InNodes:
        return None
        
    for N in InNodes:
        if N.state == None:
            print("Sort failed.")
            return None
        if not N.state:
            return False
            
    return True
    
def or_eval(InNodes):
    if not InNodes:
        return None
        
    for N in InNodes:
        if N.state == None:
            print("Sort failed.")
            return None
        if N.state:
            return True
            
    return False
    
def xor_eval(InNodes):
    if not InNodes:
        return None
    Value = False
    for N in InNodes:
        if N.state == None:
            print("Sort failed.")
            return None
        if N.state and Value:
            return False
        elif N.state:
            Value = True
            
    return Value

def top_sort(Nodes):
    new_order = []
    S = []
    for N in Nodes:
        N.incounter = len(N.in_nodes)
        if N.incounter == 0:
            S.append(N)
            
    while S:
        u = S.pop()
        new_order.append(u)
        for out in u.out_nodes:
            out.incounter -= 1
            if out.incounter == 0:
                S.append(out)
                
    return new_order

def update(Nodes):
    ordered = top_sort(Nodes)
    #if there are nodes in Nodes that are not in ordered, then there is a circle
    for n in ordered:
        n.eval()
        
