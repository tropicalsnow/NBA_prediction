#Predict the outcome (win/loss & prob) of individual NBA games.

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import time
import numpy as np
import os.path, sys

sys.path.append('Libs')





from SupportFunctions import backTestSeason, LoadSettings, scrape_all_databases, generateTrainingData, PredictLineup, trainClassifier
from featureUtilities import generate_Features_fromDB, engineerFeatures, selectFeatures, Predict_Features_forLineup, Spread2Prob_Convert
from scrape_NBA_Data import scrape_NBA_scheduled_games
from LoadSaveXLSData import LoadGameData, writePredictionsToFile
from seasonDB_utils import open_database
from TeamsList import Teams
from ensemble_metaPredict import ensemble_metaPredict
from daily_purge import purge


from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier 
from lightgbm import LGBMClassifier

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, AdaBoostClassifier

def create_CLASSIFIER_model(Params):
    
    if Params.label_type=='hard':

        model = XGBClassifier(
                            scale_pos_weight=1,
                            learning_rate=0.01,  
                            colsample_bytree = 1,
                            subsample = 1,
                            objective='binary:logistic', 
                            n_estimators=2000, 
                            reg_alpha = 0.3,
                            max_depth=3, 
                            gamma=0,
                            use_label_encoder=False,
                            eval_metric='logloss',
                            tree_method='gpu_hist')

        # model = RandomForestClassifier(n_jobs=1)



        # model = CatBoostClassifier(n_estimators=2000,
        #                    max_depth=3,
        #                    learning_rate=0.01,
        #                    objective='CrossEntropy',
        #                    verbose=False)    
    
        # model = LGBMClassifier(objective ='binary',
        #                        boosting_type  ='gbdt',
        #                         n_jobs = -1,
        #                        learning_rate=0.01,
        #                        max_depth=8,
        #                        n_estimators=2500, 
        #                        subsample= 0.1,
        #                        num_leaves = 15
        #                        )
        
       
    else:

        model = XGBRegressor(
                            scale_pos_weight=1,
                            learning_rate=0.01,  
                            colsample_bytree = 1,
                            subsample = 1,
                            objective='reg:squarederror', 
                            n_estimators=2000, 
                            reg_alpha = 0.3,
                            max_depth=3, 
                            gamma=0,
                            use_label_encoder=False,
                            eval_metric='rmse',
                            tree_method='gpu_hist')
                        

 

    return model


def main():

    #daily purge
    purge_warn = input("PURGE DAILY DATA? (Type 'yes' or any key for no) ")
    if purge_warn.capitalize() == "Yes":
        purge()


    #Read settings file
    Params = LoadSettings("settings.txt")
    
    
    #Scrape all databases if they do not exist. Includes all training and test databases
    scrape_all_databases(Params)

    if Params.testSeason in Params.trainingSeasons:
        print("WARNING: Test season ",Params.testSeason," is ALSO in training season list")


    #GENERATE TRAINING DATA FOR CLASSIFIER
    Features_FILENAME = ("TrainingFeatures.")
    TrainFeatures,TrainLabels, TrainWeights = generateTrainingData(Params, Features_FILENAME)
 
    if Params.use_feature_selector:
        FS = selectFeatures(TrainFeatures, TrainLabels, Params.num_of_features)
        TrainFeatures = FS.transform(TrainFeatures)
    else:
        FS=None


    if Params.feature_engineer:
        TrainFeatures = engineerFeatures(TrainFeatures)


    #Create the classifier model
    CM=create_CLASSIFIER_model(Params)
    


    answer=input("Season (B)ackTest or (F)uture game prediction  \t\t")    


    if answer.capitalize() == "B":
         
        #SEASON BACKTEST
        output_file= './Data/Market_data/MarketData_'+str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:4]+'.xlsx'    

        warn = input("WARNING THIS WILL OVERWRITE THE FILE " + output_file + ". ARE YOU SURE Y/N? ")

        if warn.capitalize() == "Y":
            backTestSeason(Params, TrainFeatures, TrainLabels, TrainWeights, CM, output_file, FS, Params.plot_graphs)
        

    elif answer.capitalize() == "F":
        
        #FUTURE GAME PREDICTION

        test_season = str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:4]
        databaseFile = Params.databaseDir+"/NBA_season"+test_season+".db"
        if  os.path.isfile(databaseFile):
            dbms = open_database(databaseFile)   #open the database file
            cursor= dbms.conn.cursor()
        else:
            print("Testing database was not found. Aborting")
            sys.exit()

        no_games_sofar= len(cursor.execute('SELECT game_id FROM Games ').fetchall())

        #Load Prediction database as well
        player_dbms= open_database(Params.databaseDir+"/PlayerStatDatabase.db") #TODO: Pass this from Params file


        #Fit the classifier
        CM=trainClassifier(Params, CM, TrainFeatures, TrainLabels, TrainWeights )


        #load/scrape test data
        scheduled_games_FILENAME="test_games.xlsx"
        injury_list_FILENAME="test_games_injuries.xlsx"
        experts_FILENAME = "test_games_EXPERTS.xlsx"



        answer=input("Enter schedule games date (dd/mm/YYYY). Press (Enter) for current date: ") 
        if answer:
            dd=  answer[0:2]
            mm=  answer[3:5]
            YY=  answer[6:10]
        else:            
            dd= time.strftime("%d")
            mm= time.strftime("%m")
            YY= time.strftime("%Y")

        scrape_NBA_scheduled_games(scheduled_games_FILENAME,injury_list_FILENAME, experts_FILENAME, Teams, dd,mm,YY)
        scheduledGames=LoadGameData(scheduled_games_FILENAME,True)


        #generate features for upcoming games
        ALL_p_probs=np.zeros([len(scheduledGames),2])
        ALL_p_test=np.zeros(len(scheduledGames))

        for g in range(len(scheduledGames)):
            awayTeam_ID = cursor.execute('SELECT team_id FROM Teams WHERE short_name="'+scheduledGames[g].Away+'"').fetchone()[0]
            homeTeam_ID = cursor.execute('SELECT team_id FROM Teams WHERE short_name="'+scheduledGames[g].Home+'"').fetchone()[0]
                        
            #Predict features for the next (upcoming test) game
            awayTeam_lineup = PredictLineup(Params, awayTeam_ID, injury_list_FILENAME, dbms, player_dbms )
        
            homeTeam_lineup = PredictLineup(Params, homeTeam_ID, injury_list_FILENAME, dbms, player_dbms )
 
            #Predict features for the  game
            Feats_Away=Predict_Features_forLineup(Params, awayTeam_lineup,  cursor)
            Feats_Home=Predict_Features_forLineup(Params, homeTeam_lineup,  cursor)

            TestFeatures=np.hstack([Feats_Away, Feats_Home]) 
            if Params.reverse_home_advantage:
                ReverseTestFeatures=np.hstack([Feats_Home, Feats_Away]) 


            
            if Params.add_gameno_as_feature:   
                TestFeatures=np.hstack([TestFeatures,  (g+1+no_games_sofar)*np.ones((Params.MCruns,1)) ])  #Add the game number as a feature
                if Params.reverse_home_advantage:
                    ReverseTestFeatures=np.hstack([ReverseTestFeatures, (g+1+no_games_sofar)*np.ones((Params.MCruns,1))  ])  #Add the game number as a feature

        
            if TestFeatures.shape[0]==1:
                TestFeatures=TestFeatures.reshape(1,-1)
                if Params.reverse_home_advantage:
                    ReverseTestFeatures=ReverseTestFeatures.reshape(1,-1)
         

            if Params.use_feature_selector:
                TestFeatures = FS.transform(TestFeatures)
                if Params.reverse_home_advantage:
                    ReverseTestFeatures = FS.transform(ReverseTestFeatures)
            if Params.feature_engineer:
                TestFeatures = engineerFeatures(TestFeatures)
                if Params.reverse_home_advantage:
                    ReverseTestFeatures = engineerFeatures(ReverseTestFeatures)


            #Predict outcome of upcoming game
            if Params.label_type=='hard':
                p_probs = CM.predict_proba(TestFeatures)             
                p_probs= np.mean(p_probs, axis=0) #take the mean of the MC probs 

                if Params.reverse_home_advantage:
                    reverse_out_probs = CM.predict_proba(ReverseTestFeatures) 
                    reverse_out_probs= np.mean(reverse_out_probs, axis=0) #take the mean of the MC probs 
                    p_probs = np.array([(p_probs[0]+reverse_out_probs[1])/2, (p_probs[1]+reverse_out_probs[0])/2])


                p_probs[0] = 1- p_probs[1] #make sure they sum to 1
                     
            
                p_test =   np.argmax(p_probs)+1 #Remember here that labels are 1-Away, 2-Home
 

            else:  #SOFT LABELS  TODO: MonteCarlo

                out_regr= CM.predict(TestFeatures)[0]
                p_probs = Spread2Prob_Convert(out_regr, [9.96240982e-01,  1.34591168e-12, -1.34107120e+00, -6.40128871e-01])

                if p_probs > 0.5: #HOME
                    p_test= 2 #home
                else: #AWAY
                    p_test=1 #away
 

            ALL_p_probs[g]=p_probs
            ALL_p_test[g] = p_test


        #Write predictions to test file
        writePredictionsToFile(scheduled_games_FILENAME,ALL_p_test, ALL_p_probs)
    

        dbms.closeConnection()
        player_dbms.closeConnection()
   


        #META-predictions using ensemble of experts. Pass out predictions
        if Params.useMetaEnsemble:
            ensemble_metaPredict(experts_FILENAME, scheduled_games_FILENAME, ALL_p_probs[:,0])

if __name__ == '__main__':
    main()
    
    