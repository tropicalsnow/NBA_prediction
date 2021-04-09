#using the Keras DQN or CEM models


import numpy as np
from keras.models import model_from_json


def KerasRL_Strategy(our_probs, market_odds, carmeloDat, coversDat, oddsharkDat, h2hDat, num_actions, maxPC, strategy_balance):
    
    Bets=[]
    Stakes=[]


    # load json and create model
    json_file = open('reinforcement_learning\Keras_DQN_model_SIMPLE.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into new model
    loaded_model.load_weights("reinforcement_learning\Keras_DQN_weights_SIMPLE.h5f")

    
    

    #Loop for every bet
    running_balance=strategy_balance
    for i in range(len(our_probs)):

        #Set up bet state
        state = np.array([our_probs[i,0],  market_odds[i,0], market_odds[i,1], \
                carmeloDat[i], coversDat[i,0],  coversDat[i,1], coversDat[i,2], coversDat[i,3], oddsharkDat[i,0], oddsharkDat[i,1], oddsharkDat[i,2], \
                h2hDat[i,0], h2hDat[i,1], h2hDat[i,2], h2hDat[i,3], h2hDat[i,4], h2hDat[i,5]], dtype=np.float32)


        
        

        #evaluate action for given state
        action = np.argmax(loaded_model.predict( state.reshape(1, 1, len(state)) ) )
        ac_index=np.linspace(0, maxPC, num_actions)
        if action>=len(ac_index) or action<0:
            action=0
        else:
            action = ac_index[action]


        #set up stakes and bets
        Stakes.append(abs(action)/100*running_balance)

        if our_probs[i,1]>our_probs[i,0]:
            Bets.append(2) #HOME
        else:
            Bets.append(1) #AWAY

        running_balance=running_balance-Stakes[i] #Assume that the balance is the current less the stake placed  for each bet

    return (Stakes,Bets)