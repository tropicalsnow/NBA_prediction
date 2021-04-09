def Percentage_Short_Strategy(market_bets,stake_pcnt,strategy_balance):

    import numpy as np

    #Calculate bet stakes
    amount=np.floor(strategy_balance/len(market_bets))

    Stakes=[amount*stake_pcnt for x in market_bets ]
    Bets=[2 if x==1 else 1 for x in market_bets] #reverse bets

    return (Stakes,Bets)

