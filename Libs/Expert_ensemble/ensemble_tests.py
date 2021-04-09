import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
from featureUtilities import Spread2Prob_Convert
from ensemble_metaPredict import extract_data

import Test_methods as tst

 



#load data from database
db_filename='ExpertPredictions_DB.db'

conn=sqlite3.connect(db_filename)
cursor = conn.cursor()


#Get all the Predictions, Experts & Games data and save them to Pandas df
all_game_rows=cursor.execute("SELECT game_id, Away_Score, Home_Score, Result, Season from GAMES").fetchall()
col_names= np.array(cursor.description)
games_DF = pd.DataFrame(all_game_rows, columns=col_names[:,0])

all_pred_rows=cursor.execute("SELECT * from Predictions").fetchall()
col_names= np.array(cursor.description)
predictions_DF = pd.DataFrame(all_pred_rows, columns=col_names[:,0])

all_expert_rows=cursor.execute("SELECT * from Experts").fetchall()
col_names= np.array(cursor.description)
experts_DF = pd.DataFrame(all_expert_rows, columns=col_names[:,0])


#Close database
conn.close()



expert_ids = experts_DF['expert_id'].values #these are already unique by definition of the database



#Split the games dataframe into  train & test sets
Games_trainval, Games_test = train_test_split(games_DF, test_size=0.3,  random_state=115) #make sure random_state is fixed otherwise delete all CSV files



preds_trainval_file='./Predictions_TRAIN.csv'
outc_trainval_file = './Outcome_TRAIN.csv'
preds_test_file='./Predictions_TEST.csv'
outc_test_file = './Outcome_TEST.csv'
if  os.path.isfile(preds_trainval_file) and os.path.isfile(outc_trainval_file)  and os.path.isfile(preds_test_file) and os.path.isfile(outc_test_file):
    #load the data from file
    Preds_trainval= np.loadtxt(preds_trainval_file, delimiter=',')
    Outc_trainval,Spreads_trainval,weights_trainval = np.loadtxt(outc_trainval_file, delimiter=',' , usecols=(0, 1, 2), unpack=True)
    Preds_test= np.loadtxt(preds_test_file, delimiter=',')
    Outc_test,Spreads_test = np.loadtxt(outc_test_file, delimiter=',' , usecols=(0, 1), unpack=True)
else:
    #extract the data
    Preds_trainval, Outc_trainval, Spreads_trainval, weights_trainval = extract_data(Games_trainval, expert_ids, predictions_DF)
    Preds_test, Outc_test, Spreads_test, _ = extract_data(Games_test, expert_ids, predictions_DF)
    #save to CSV
    np.savetxt(preds_trainval_file, Preds_trainval, delimiter=',', fmt='%s')
    np.savetxt(outc_trainval_file,np.column_stack((Outc_trainval,Spreads_trainval,weights_trainval)),delimiter=',', fmt='%s')
    np.savetxt(preds_test_file, Preds_test, delimiter=',', fmt='%s')
    np.savetxt(outc_test_file,np.column_stack((Outc_test,Spreads_test)),delimiter=',', fmt='%s')


 


#Evaluation

# #Method 1. best_N_experts 
# score, N = tst.best_N_experts(Preds_trainval, Outc_trainval,  Preds_test, Outc_test,  Nreplicates=25, type='Brier_weighted', average='weighted')
# print("best_%i_experts Brier score: \t%.6f"%(N, score))

# #Method 2. Stacking classifier/regressor. Do cross validation internally
# score =  tst.Stacker(Preds_trainval, Outc_trainval, Preds_test, Outc_test)
# print("Stacking Brier score: \t\t%.6f"%(score))

# score= tst.StackerTPOT(Preds_trainval, Outc_trainval, Preds_test, Outc_test)
# print("Stacking(TPOT) Brier score: \t\t%.6f"%(score))


#Method 3. Global weight optimisation
score = tst.GlobalBrier_optimiser(Preds_trainval, Outc_trainval, weights_trainval,  Preds_test, Outc_test)
print("Global optimiser Brier score: \t%.6f"%(score))

# #Method 4. Bayesian Model (Linear) Combination
# score =tst.Bayesian_model_combination(Preds_trainval, Outc_trainval,  Preds_test, Outc_test, 100, 50)
# print("BMC Brier score: \t\t%.6f"%(score))

# #Method 5. Eureqa genetic programming
# score= tst.Eureqa( Preds_test, Outc_test)
# print("Eureqa score: \t\t\t%.6f"%(score))