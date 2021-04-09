import numpy as np
from math import pow, sqrt
 
from platypus import NSGAII, Problem, Real
import functools

from multibet_utils import outcomes_HACK, PoissonBinomialPDF


import matplotlib.pyplot as plt 


def ExpectationRisk(x,arg1,arg2,arg3,arg4,arg5):
    
    n=arg1
    odds=arg2
    Event_Probs=arg3
    bets=arg4
    outc=arg5

 

    num_events=int(pow(2,n))

    ## Expectation

    # Calculate profit for each of the events

    Event_profits=np.zeros(num_events)

    for i in range(num_events):
        Profit=0

        for j in range(n):

            if all(odds[j])>0:

                if bets[j] == outc[i,j]:

                    Profit=Profit+  x[j]*(odds[j,bets[j]-1]-1)
                else:
                    Profit = Profit - x[j]
            else:
                Profit=0

        if sum(x)==0:
            Event_profits[i]   =0
        else:
            Event_profits[i]=Profit/sum(x)
    
    W=Event_Probs*Event_profits

    e=sum(W)

    
    ## Risk
    r_sq =   sum(Event_Probs*(Event_profits-e)**2)


    #output
    y1= -e #change for minimisation
    y2= r_sq

    return [y1,y2], [sum(x)]  #return [expecation,risk] and [constraints]


    

def Pareto_Front_Strategy(Probs,odds,Total_BetMax,Max_individual_bet,Min_individual_bet):
 
    #NOTE: The order of bets and Probs is as follows: 1st (1) is AWAY win and 2nd (2) is HOME win

    
    Bets=np.argmax(Probs,1)+1

    n=len(Probs) #number of games

 
    # Calculate probabilities for ALL the events together (i.e. each outcome). This will be used as weights for our optimisation
    k=n
    num_events=int(pow(2,n))
    Event_Probs=np.zeros(num_events)
    
    outc=outcomes_HACK(n)


    for i in range(num_events):
        individual_probs=np.diag(Probs[:,outc[i,:]-1])
        Event_Probs[i]= PoissonBinomialPDF(k,n,individual_probs)


    #Pareto optimization
    problem = Problem(n, 2, 1) #vars, problem dim, constraints
    problem.types[:] = Real(Min_individual_bet,Max_individual_bet)  #lower and upper bounds for all decision variables
    problem.function = functools.partial(ExpectationRisk, arg1=n, arg2=odds, arg3=Event_Probs, arg4=Bets, arg5=outc) 
    problem.constraints[:] = "<="+str(Total_BetMax)+"" #inequality constraints: sum of bets no more than BetMax           
    algorithm = NSGAII(problem)
    algorithm.run(5000)

    
    plt.scatter([s.objectives[0] for s in algorithm.result],  [s.objectives[1] for s in algorithm.result])
    plt.show()
 



    Stakes=[]

    Ratio=0

    for i in range(len(algorithm.result)):
        #objectives are: -data[0] = Expectation, data[1] = Variance
        
        #Exp/Variance ration threshold
        Exp=algorithm.result[i].objectives._data[0]
        Var= algorithm.result[i].objectives._data[1]
        curRatio= Exp/Var

        if curRatio>Ratio:
            Ratio=curRatio
            Stakes=algorithm.result[i].variables
            ExpOut=Exp
            VarOut= Var


    return (Stakes, Bets, ExpOut, VarOut)        