def Fixed_Variance_Strategy(our_prediction,our_probs,market_odds,Fixed_bet_amount,var_threshold):

    import math
    
    Bets=[]
    Stakes=[]

    #Calculate bet stakes
    for i in  range(len(our_prediction)):

        bet=int(our_prediction[i])
        Bets.append(bet)

        if all(market_odds[i]) > 0:

            #Calculate bet expectation
            p=our_probs[i,bet-1]
            q=1-p
            d=market_odds[i,bet-1]

            E=  (p*(d-1) -q)

            profP=  p*(d-1)
            profQ=  -q

            #Calculate variance
            
            R=    math.sqrt( p*(profP-E)**2  +  q*(profQ-E)**2)

            if R <= var_threshold:
                Stakes.append(Fixed_bet_amount)
            else:
                Stakes.append(0.0)

        else:
             Stakes.append(0.0)

    return (Stakes,Bets)