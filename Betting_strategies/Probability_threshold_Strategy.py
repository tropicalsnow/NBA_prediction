def Probability_threshold_Strategy(our_prediction,Fixed_bet_amount,our_probs,prob_threshold):



    Bets=[]
    Stakes=[]
        
    #Calculate bet stakes
    for i in  range(len(our_prediction)):
        
        bet=int(our_prediction[i])
        Bets.append(bet)
        
    
        p=our_probs[i,bet-1]
    
        
        
        
        if p >= prob_threshold:
            Stakes.append(Fixed_bet_amount)
            
        else:
            Stakes.append(0)

    return (Stakes,Bets)

