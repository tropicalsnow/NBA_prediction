
def Reinforcement_Learning_Strategy(Probs, true_market_odds, initial_balance, balance):

    
    import tensorflow
    import sys
    

    Bets=[]
    Stakes=[]
    
    #Load learnt model
    model = tensorflow.keras.models.load_model('./reinforcement_learning/Keras_DQN_model_SIMPLE')

    #Set up bet state            
    growth=balance/initial_balance
    season_round=0

    for i in range(length(Probs)):

        state = [growth, Probs[i,0], true_market_odds[i,0], true_market_odds[i,1], season_round]


        #evaluate action for given state

    

    
    model.predict()


    #  #first Convert action range from [0:num_actions] to [-maxPC,maxPC]        
    #     ac_index=np.linspace(-maxPC, maxPC, num_actions)
    #     if action>=len(ac_index):
    #         action=0        
    #     else:
    #         action = ac_index[action] 
    
    #     bet_size=abs(action)/100* balance 


    pass

