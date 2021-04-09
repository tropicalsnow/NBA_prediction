def Expectation_based_Strategy(our_prediction,our_probs,market_odds,f,min_bet,strategy_balance):

    import numpy as np

    Bets=[]
    weight=[]

    amount=np.floor(f*strategy_balance*len(our_prediction))
    if amount>strategy_balance:
        amount=strategy_balance
    
    Stakes=(max(np.floor(amount/len(our_prediction)),min_bet)*np.ones(len(our_prediction))).tolist()

    
    for i in  range(len(our_prediction)):

 
        bet=int(our_prediction[i])
        Bets.append(bet)


        if all(market_odds[i]) > 0:

            #Calculate bet expectation
            p=our_probs[i,bet-1]
            q=1-p
            d=market_odds[i,bet-1]

            E=  (p*(d-1) -q)
            
        
            if E>0:
                weight.append(np.log(p/(1-p)))  #Logit weighting of probs
            else:
                Stakes[i]=0.0
                weight.append(0)

        else:
            Stakes[i]=0.0
            weight.append(0)
            
        
    #Re-arrange the weightings of the individual stakes according to our probabilities
    if sum(weight)>0:
        weight=(weight/sum(weight))*sum(np.asarray(weight)>0) #normalize weights and reduce total stake amount if we do not place some bets
        Stakes=Stakes*weight

    return (Stakes,Bets)

