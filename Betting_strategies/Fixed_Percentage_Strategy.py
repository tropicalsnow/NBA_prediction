def Fixed_Percentage_Strategy(our_prediction,stake_pcnt,strategy_balance):

    import numpy as np

    #Calculate bet stakes
    Stakes=[]
    Bets=[]
    
    amount=np.floor(strategy_balance/len(our_prediction))


    for i in range(len(our_prediction)):
        
        Stakes.append(amount*stake_pcnt)
        Bets.append(int(our_prediction[i]))

    return (Stakes,Bets)

