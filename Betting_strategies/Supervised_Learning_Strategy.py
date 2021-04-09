import os
import joblib

from sklearn.ensemble import RandomForestRegressor

from sklearn.ensemble import AdaBoostClassifier



import xlrd
import numpy as np
import math


def TrainSupervisedModel():
    #load data
    
    TrainingFiles=[
    './Betting_strategies/manual_training/manual_betting_features_2019_1.xlsx',
    './Betting_strategies/manual_training/manual_betting_features_2019_2.xlsx',
    './Betting_strategies/manual_training/manual_betting_features_2019_3.xlsx'
    ]


    Features=[]
    Labels=[]

    for i in range(len(TrainingFiles)):
        workbook = xlrd.open_workbook(TrainingFiles[i], on_demand=True)
        worksheet = workbook.sheet_by_index(0)

        num_cols = worksheet.ncols   # Number of columns

        for row_idx in range(1, worksheet.nrows): #Iterate through rows. Skip header
            Feature_vector=[]
            Feature_flag=True
            for col_idx in range(0, num_cols):  # Iterate through columns
                cell_val = worksheet.cell(row_idx, col_idx).value  # Get cell 
                if cell_val =='':
                    Feature_flag=False

                if Feature_flag:
                    Feature_vector.append(cell_val)
                else:
                    side=worksheet.cell(row_idx, col_idx+1).value
                    stake=worksheet.cell(row_idx, col_idx+2).value
                    if side==1:
                        stake=-stake                    
                
                    break
            
            if Features==[]:
                Features=np.array(Feature_vector)
                Labels=np.array(stake)
            else:
                Features= np.vstack([Features, Feature_vector])
                Labels=   np.hstack([Labels, stake])
                
                    


        workbook.release_resources()

    #Train model
    model = RandomForestRegressor(max_depth=2, max_features =0.7, criterion='mae')
    #model =AdaBoostClassifier(n_estimators=100)

    model.fit(Features, Labels)


    return model


def Supervised_Learning_Strategy(Probs,Market_Odds,  Balance, Accuracy, game_no, Profit ):
    

    
    Stakes=[]
    Bets=[]
    Unsettled_Balance=Balance
    if math.isnan(Accuracy):
        Accuracy=1 

    #Load trained model if exists. If it doesnt exist then train it and save it
    model_filename="./Betting_strategies/manual_training/supervised_learning_model.dat"
    if  os.path.isfile(model_filename):
        # load model from file
        model = joblib.load(model_filename)
    else:
        model = TrainSupervisedModel()
        # save model to file
        joblib.dump(model, model_filename)


    #Generate observation and apply model
    for i in range(len(Probs)):
        
        observation = np.array([Balance, Probs[i,0], Probs[i,1], Market_Odds[i,0], Market_Odds[i,1], Balance-Unsettled_Balance, i+1, len(Probs), game_no+i+1, Accuracy, Profit ])

        out=model.predict(observation.reshape(1,-1))[0]

        if out<0:
            Bet_Side=1
            Bet_Amt=-out
        else:
            Bet_Side=2
            Bet_Amt=out



        if Bet_Amt <= Unsettled_Balance:
            Unsettled_Balance = Unsettled_Balance - Bet_Amt


        Stakes.append(Bet_Amt)
        Bets.append(Bet_Side)

    
    return Stakes, Bets