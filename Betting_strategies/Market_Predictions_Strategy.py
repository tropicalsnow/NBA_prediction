def Market_Predictions_Strategy(market_bets,Fixed_bet_amount):


    Bets=[]
    Stakes=[]
    #Calculate bet stakes
    
    for i in  range(len(market_bets)):

        Bets.append(int(market_bets[i])) #bet according to market


        if market_bets[i] > 0:

            Stakes.append(Fixed_bet_amount)
            
        else:
            Stakes.append(0)
        
    return (Stakes,Bets)        

