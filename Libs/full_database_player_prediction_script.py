
import os.path, sys
sys.path.append('../')


from PredictPlayerStats import getPlayerPrediction, createStatDatabase, evaluate_prediction_for_Player
from SupportFunctions import LoadSettings
from seasonDB_utils import open_database

import numpy as np

def main():

    #Pre-calc all predictions of  full test season
    db_name='PlayerStatDatabase.db'

    #Read settings file
    Params = LoadSettings("../settings.txt")
    #Create Player stats database if it doesnt exist
    createStatDatabase(Params,db_name)

    verbose=True
    

    #Load ground truth test season database
    test_season = str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:4]
    GT_database_file = '.'+Params.databaseDir+"/NBA_season"+test_season+".db"
    
 
    GT_dbms = open_database(GT_database_file)   
    GT_cursor= GT_dbms.conn.cursor()

    GT_player_rows = GT_cursor.execute('SELECT * FROM Players ').fetchall()

    ErrorDict={}
    for p in range(len(GT_player_rows)):
        
        player_id=GT_player_rows[p][0]

        print(player_id)

        #Get ground truth info for target player
        GT_player_info_row = np.array(GT_cursor.execute('SELECT * FROM Players where player_id="'+player_id+'"').fetchone())


        #Calculate the predictions
        prediction, player_stats_rows=getPlayerPrediction(Params, str(player_id), db_name, verbose)


        #evaluation of predictions for single player    
        if len(prediction)>0: #temporarily ignore rookies
            _, wError, wbaselineError=evaluate_prediction_for_Player(Params, GT_player_info_row, player_stats_rows, prediction, True )          
            ErrorDict[player_id] = [wError, wbaselineError]


    Errors=np.array(list(ErrorDict.values()))
    print(np.nanmean(Errors,axis=0)) #print the average error and baseline error

    #Finish and close databases
    GT_dbms.closeConnection()



if __name__ == '__main__':
    main()
