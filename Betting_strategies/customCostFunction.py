import numpy as np


def generalised_logistic_func(x,A,K,B,nu,Q,C):

    #A: the lower asymptote;
    #K: the upper asymptote. If A = 0 then K is called the carrying capacity;
    #B: the growth rate;
    #nu >0 : affects near which asymptote maximum growth occurs.
    #Q: is related to the value Y(0)
    #C: typically takes a value of 1

    y= A + (K-A) / (C+Q*np.exp(-B*x))**(1/nu)

    return y



def cost_func(EV, n_bets_placed,total_games, DD):

    
    F1= generalised_logistic_func(EV, -1, 1, 6, 1, 1, 1)

    F2= n_bets_placed/total_games

    F3 = 1- DD

    w1= 10
    w2= 3
    w3= 1
    sw=w1+w2+w3
    w1=w1/sw
    w2=w2/sw
    w3=w3/sw


    C= 1/3 *(w1*F1+w2*F2+w3*F3)

    return C
