import numpy as np
import itertools


def outcomes_HACK(n):

    #returns a 2^n by n matrix of 1,-1s that represent all the possible outcomes of n games (1=success, 2=fail)
    #Note this is only valid and fast for small n

    flag=False

    trials=2*int(pow(2,n))

    while not flag:

        out = np.unique(np.random.randint(1,3,size=(trials,n)),axis=0)

        if len(out)< int(pow(2,n)):
            trials=2*trials
        else:
            flag=True
    
    return out



def PoissonBinomialPDF(k,n,Probs):
 
    #Note that this works best for small n and k close to n.
    #Also Probs must be in range [0,1]
    
    F_k=list(itertools.combinations(range(1,n+1),k))
    
    sz=len(F_k)
    
    sum_A=0

    for l in range(sz): #loop over rows of F_k
        A=F_k[l][:]
        A_c= np.setdiff1d(list(range(1,n+1)),A)


        prod_pi=1
        for i in range(len(A)): #loop over the elements of A (i.e. the success events)
            prod_pi=prod_pi*Probs[A[i]-1]

        prod_pj=1
        for j in range(len(A_c)):  #loop over the elements of A_c (i.e. the fail events)
            prod_pj=prod_pj*(1-Probs[A_c[j]-1])
        
        sum_A=sum_A+(prod_pi*prod_pj)
    
    return sum_A

