def Edge_based_Strategy_with_threshold(our_prediction,our_probs,market_probs,f,prob_threshold,min_bet,strategy_balance):

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


        if all(market_probs[i]) > 0:

            # Calculate bet edge
            p=our_probs[i,bet-1]

            market_p= market_probs[i,bet-1] #market probability for our bet prediction, NOT market's own prediction

            Edge=p-market_p


            market_bet= np.argmax(market_probs[i,:])+1
            
    
            if ((Edge>0) or (p>=prob_threshold and market_p>=prob_threshold  and bet==market_bet )):
                weight.append(np.log(p/(1-p))) #Logit weighting of probs
            else:
                Stakes[i]=0
                weight.append(0)
 
        else:
            Stakes[i]=0
            weight.append(0)
            

     #Re-arrange the weightings of the individual stakes according to our probabilities
    if sum(weight)>0:
        weight=(weight/sum(weight))*sum(np.asarray(weight)>0) #normalize weights and reduce total stake amount if we do not place some bets
        Stakes=Stakes*weight

    return (Stakes,Bets)