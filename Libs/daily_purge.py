
def purge():
        
    #purge all files that need to be recalculated every day
    import os
    import sys
    sys.path.append('Libs')



    from SupportFunctions import LoadSettings

    Params = LoadSettings("settings.txt")


    files_list=[]

    files_list.append("./temp/temp_y_train.csv")
    files_list.append("./temp/temp_Xtrain.csv")
    files_list.append("./temp/tempBackTesting_Database.db")    
    files_list.append("./Data/Stats_data/NBA_season"+str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:]+".db")
    files_list.append("./Data/Experts_data/Oddsportal_"+str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:]+".xlsx")
    files_list.append("./Data/Experts_data/PredictionTracker_"+str(Params.testSeason-1)+"-"+str(Params.testSeason)[2:]+".xlsx")
    files_list.append("./Libs/Expert_ensemble/Outcome_TEST.csv")
    files_list.append("./Libs/Expert_ensemble/Outcome_TRAIN.csv")
    files_list.append("./Libs/Expert_ensemble/Predictions_TEST.csv")
    files_list.append("./Libs/Expert_ensemble/Predictions_TRAIN.csv")
    files_list.append("./Libs/Expert_ensemble/ExpertPredictions_DB.db")
    files_list.append("./nbapreds.csv")
    files_list.append("./test_games.xlsx")
    files_list.append("./test_games_EXPERTS.xlsx")
    files_list.append("./test_games_injuries.xlsx")




    for file in files_list:
        if os.path.exists(file):
            os.remove(file)

