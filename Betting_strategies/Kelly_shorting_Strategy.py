def Kelly_shorting_Strategy(our_probs,market_odds,f,cutoff,strategy_balance):
   #Kelly but we can decide which side to bet on based on the edge


    import numpy as np
    from math import log
    
    #Try to split the maximum bets equally for each game. This is a crude approximation of the multibet version
    individual_kelly_stake=np.floor(strategy_balance/len(our_probs))
    

    Stakes=[]
    Bets=[]
    
    for i in range(len(our_probs)):

        
        if all(market_odds[i]) > 0:

            #Calculate Kelly of Side A
            p1=our_probs[i,0]
            q1=1-p1
            d1=market_odds[i,0]
            b1=(d1-1)

            s1= (p1*b1-q1)/(b1)


            #Consider Kelly for Side B
            p2=our_probs[i,1]
            q2=1-p2
            d2=market_odds[i,1]
            b2=(d2-1)
            
            s2= (p2*b2-q2)/(b2)

      
            if s1<0 and s2<0:
                #No bet
                Stakes.append(0.0)
                bet=1
            elif (s1>0 and s2<0) or (s1>0 and p1> log(b1*(1+b2)/(1+b1)) / log(b1*b2)  ):
                #Bet on side A 
                Stakes.append(individual_kelly_stake*s1*f)
                bet=1
            else:
                #Bet on side B
                Stakes.append(individual_kelly_stake*   min(s2*f, cutoff)  )
                bet=2


        else:
            Stakes.append(0.0)

        
        Bets.append(bet)

    return (Stakes,Bets)
        
