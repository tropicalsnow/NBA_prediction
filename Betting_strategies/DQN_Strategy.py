#USING MICROSOFT CNTK LIBRARY without Keras

import cntk.ops.functions
import cntk as C
from cntk import load_model
import numpy as np
import os, sys, inspect


#For importing modules from subfolders
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../reinforcement_learning")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)  




def DQN_Strategy(our_probs, market_odds, carmeloDat, coversDat, oddsharkDat, h2hDat, num_actions, maxPC, strategy_balance):


    
    Bets=[]
    Stakes=[]


    #Load learnt model
    model = C.load_model("reinforcement_learning\customDQN_BRAIN.mod")

    #Loop for every bet
    running_balance=strategy_balance
    for i in range(len(our_probs)):
        
 
        #Set up bet state
        state = [our_probs[i,0],  market_odds[i,0], market_odds[i,1], \
                carmeloDat[i], coversDat[i,0],  coversDat[i,1], coversDat[i,2], coversDat[i,3], oddsharkDat[i,0], oddsharkDat[i,1], oddsharkDat[i,2], \
                h2hDat[i,0], h2hDat[i,1], h2hDat[i,2], h2hDat[i,3], h2hDat[i,4], h2hDat[i,5]]



        #evaluate action for given state

        action = np.argmax(model.eval(np.float32(state)))
        ac_index=np.linspace(0, maxPC, num_actions)
        if action>=len(ac_index) or action<0:
            action=0
        else:
            action = ac_index[action]

        Stakes.append(abs(action)/100*running_balance)

        if our_probs[i,1]>our_probs[i,0]:
            Bets.append(2) #HOME
        else:
            Bets.append(1) #AWAY

        running_balance=running_balance-Stakes[i] #Assume that the balance is the current less the stake placed  for each bet



    return (Stakes,Bets)