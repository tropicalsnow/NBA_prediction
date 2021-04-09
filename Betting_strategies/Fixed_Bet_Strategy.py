
def Fixed_Bet_Strategy(our_prediction,Fixed_bet_amount):

    #Calculate bet stakes
    Stakes=[]
    Bets=[]
    for i in range(len(our_prediction)):
        Stakes.append(float(Fixed_bet_amount))
        Bets.append(int(our_prediction[i]))

    return (Stakes,Bets)
    
