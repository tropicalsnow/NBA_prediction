def Experimental_Strategy(our_prediction, market_odds, Probs, alpha, beta,  max_exposure, max_bet_pcnt, balance, existingStakes=None):
    # The  constraint limits the probability of a drop in wealth to value alpha to be no more than beta
    #for alpha=0 or beta=1 then lambda=0 which results to the unconstrained Kelly. alpha, beta in [0,1]
    
    import numpy as np
    import cvxpy as cvx
    import math
    from multibet_utils import outcomes_HACK, PoissonBinomialPDF


    Bets=our_prediction #just pass through


    n=len(our_prediction)  #number of bets
    K=int(pow(2,n)) #number of outcomes
    
    #convert existingStakes from monetary value to balance percentage
    if existingStakes is None:
        existingStakes=[]   
    if len(existingStakes)>0:
        existingStakes =  existingStakes/balance


    #generate returns, including risk-free (i.e. hold money)
    outc=outcomes_HACK(n).T #all the possible outcomes
    r=np.zeros((n+1,K))
    
    for i in range(K):
        for j in range(n):
            if our_prediction[j]==outc[j,i]:
                r[j,i]=market_odds[j,our_prediction[j]-1]  
            else:
                r[j,i]=0
    r[-1,:] = 1.0 #the risk-free bets
   
    I=np.identity(n+1)
    I[n,n]=0
    
    
    #generate associated probs
    k=n
    pi=np.ones((K))

    for i in range(K):
        individual_probs=np.diag(Probs[:,outc[:,i]-1])
        pi[i]= PoissonBinomialPDF(k,n,individual_probs) #For binary bets, just the product of individual probs

    


    #defince RCK
    b_rck = cvx.Variable(n+1)
    lambda_rck = cvx.Parameter(nonneg=True)    
    growth_rate = pi.T@cvx.log(r.T@b_rck)
    risk_constraint = cvx.log_sum_exp(  np.log(pi) - lambda_rck*cvx.log(r.T@b_rck)   ) <= 0
    constraints = [cvx.sum(b_rck) == 1,  b_rck[n]>= 0.0, cvx.max(b_rck@I)<=max_exposure, risk_constraint, b_rck[0:n]<=max_bet_pcnt] 
    #include existing stake constraints
    for i in range(len(existingStakes)):
        if not math.isnan(existingStakes[i]):
            constraints.append(b_rck[i]==existingStakes[i]) #also include 0 bets as constraints. Only nans are unconstrained


    probl_rck = cvx.Problem(cvx.Maximize(growth_rate), constraints)
    



    #Define QRCK
    mu = np.sum(r * pi, 1) - 1
    rhos = np.matrix(r-1)
    second_moment = np.zeros((n+1,n+1))
    for i in range(K):
        second_moment += pi[i] * rhos[:,i] * rhos[:,i].T
        
    b_qrck = cvx.Variable(n+1)
    lambda_qrck = cvx.Parameter(nonneg=True)
    growth = b_qrck.T@mu
    variance = cvx.quad_form(b_qrck, second_moment)
    risk_constraint_qrck = lambda_qrck*(lambda_qrck + 1) * variance/2. <= lambda_qrck*growth
    constraints = [cvx.sum(b_qrck) == 1, b_rck[n]>= 0.0,  cvx.max(b_qrck@I)<=max_exposure, risk_constraint_qrck,  b_qrck[0:n]<=max_bet_pcnt] 
    #include existing stake constraints
    for i in range(len(existingStakes)):
        if not math.isnan(existingStakes[i]):
            constraints.append(b_qrck[i]==existingStakes[i])
    
    probl_qrck = cvx.Problem(cvx.Maximize(growth - variance/2.), constraints)




    #Solve RCK or QRCK
    try: #Not the best way of dealing with numerical issues. Try scaling data or using a different solver
        lambda_rck.value = np.log(beta)/np.log(alpha)
        probl_rck.solve(solver=cvx.ECOS)
        Stakes=b_rck.value[0:-1]*balance #ignore the last value i.e. percentage of balance not wagered
    except cvx.error.SolverError:
        lambda_qrck.value = np.log(beta)/np.log(alpha)
        probl_qrck.solve(solver=cvx.ECOS)
        Stakes=b_qrck.value[0:-1]*balance #ignore the last value i.e. percentage of balance not wagered



    #fix bets and stakes
    for i in range(n):
        if Stakes[i]<0:
            #flip the bet
            if Bets[i]==1:
                Bets[i]=2
            else:
                Bets[i]=1

    Stakes =abs(Stakes)



    return (Stakes,Bets)
