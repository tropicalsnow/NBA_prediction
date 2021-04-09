def With_Market_Strategy(our_prediction,market_bets,Fixed_bet_amount):

    #bet only if we agree with the market

    Bets=[]
    Stakes=[]

    #Calculate bet stakes
    for i in  range(len(our_prediction)):

        Bets.append(int(our_prediction[i]))

        if Bets[i]==market_bets[i]:
            Stakes.append(Fixed_bet_amount)
        else:
            Stakes.append(0)

    return (Stakes,Bets)


