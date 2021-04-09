
def Fixed_Short_Strategy(market_bets,Fixed_bet_amount):

    #Calculate bet stakes
    Stakes=[Fixed_bet_amount for x in market_bets]
    
    Bets=[2 if x==1 else 1 for x in market_bets] #reverse bets


    return (Stakes,Bets)
    
