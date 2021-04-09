def Kelly_Strategy(our_prediction,our_probs,market_odds,f,cutoff, strategy_balance):
   
    import numpy as np
    
    #Calculate bet stakes
    individual_kelly_stake=np.floor(strategy_balance/len(our_prediction))
    

    Stakes=[]
    Bets=[]
    
    for i in range(len(our_prediction)):

        bet=int(our_prediction[i])
        
        if all(market_odds[i]) > 0:

           

            p=our_probs[i,bet-1]
            q=1-p
            d=market_odds[i,bet-1]



            Kelly=(p*(d-1) -q)/(d-1)

      
            if Kelly>0:
                Stakes.append(  individual_kelly_stake* min(Kelly*f, cutoff)  )
            else:
                Stakes.append(0.0)
        
        
        else:
            Stakes.append(0.0)

        
        Bets.append(bet)

    return (Stakes,Bets)
        
        

   