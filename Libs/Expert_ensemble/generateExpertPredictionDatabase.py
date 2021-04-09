import sqlite3
import sys
sys.path.append("..")
sys.path.append("../..")
sys.path.append("Libs")



import TeamsList

from seasonDB_utils import open_database
from featureUtilities import Spread2Prob_Convert

import openpyxl
import os, os.path
from datetime import datetime
from xlutils.copy import copy
import numpy as np
import math
from sklearn.metrics import brier_score_loss
import pandas as pd
from os import listdir

 

 

def list_files(directory, extension):
    return [f for f in listdir(directory) if f.endswith('.' + extension)]


class MyDatabase:

    def __init__(self, filename, seasons):
        self.dbfile=filename  
        self.seasons=seasons
        

        if not os.path.isfile(self.dbfile):
            #create a new database
            self.conn = sqlite3.connect(self.dbfile)
            self.create_db_tables()
        else:
            self.conn = sqlite3.connect(self.dbfile)

        self.populateGamesTable()            

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def create_Games_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Games (game_id TEXT NOT NULL, "
        "Away_Team_id TEXT NOT NULL, " 
        "Home_Team_id TEXT NOT NULL, " 
        "Away_Score INTEGER NOT NULL, " 
        "Home_Score INTEGER NOT NULL, " 
        "Result INTEGER NOT NULL, " 
        "Date TEXT NOT NULL, "
        "Season TEXT, "
        "OT INTEGER, "

        "PRIMARY KEY(game_id),"
        "FOREIGN KEY(Away_Team_id) REFERENCES Teams(team_id),"
        "FOREIGN KEY(Home_Team_id) REFERENCES Teams(team_id) )")
    
        self.conn.commit()


    def create_Teams_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Teams (team_id TEXT NOT NULL, "
        "team_name TEXT NOT NULL, " 
        "short_name TEXT NOT NULL, "

        "PRIMARY KEY(team_id))")

        teams_sz=len(TeamsList.Teams)
        for i in range(teams_sz): #loop over teams
            #Insert to Teams table
            c.execute('INSERT INTO teams (team_id, team_name, short_name) VALUES(?,?,?)',
                                  (TeamsList.Teams[i].ID, TeamsList.Teams[i].name, TeamsList.Teams[i].short) )

        self.conn.commit()


    def create_Experts_Table(self):
        
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Experts (expert_id TEXT NOT NULL, "
        "expert_name TEXT NOT NULL, " 
        "Score FLOAT, " 
        "Pred_No INTEGER, "
        "Weight FLOAT, "
        "Score_weighted FLOAT, "
        "PRIMARY KEY(expert_id))")
        self.conn.commit()

    def create_Predictions_Table(self):
        
        
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Predictions (game_id TEXT NOT NULL, "
        "expert_id TEXT NOT NULL, "
        "Prob_Away FLOAT, "
        "Prob_Home FLOAT, " 
        "Success INTEGER, " 

        "FOREIGN KEY(expert_id) REFERENCES Experts(expert_id),"
        "FOREIGN KEY(game_id) REFERENCES Games(game_id),"
        "PRIMARY KEY(game_id, expert_id))")


        self.conn.commit()


    def create_db_tables(self):
        self.create_Teams_Table()
        self.create_Games_Table()
        self.create_Experts_Table()
        self.create_Predictions_Table()


    def populateGamesTable(self):
        base_gamedb_filename='./Data/Stats_data/NBA_season'

        c = self.conn.cursor()

        #first populate games table

        for i in  range(len(self.seasons)):
        
            season_string=str(self.seasons[i])+'-'+str(self.seasons[i]+1)[-2:]
            game_db_filename = base_gamedb_filename+season_string+'.db'

            if os.path.isfile(game_db_filename):
                #Attach game DB
                c.execute("ATTACH DATABASE ? AS GamesDB",(game_db_filename,))

                #copy over games table
                c.execute('INSERT OR REPLACE INTO Games (game_id, Away_Team_id, Home_Team_id, Away_Score, Home_Score, Result, Date)  SELECT * FROM GamesDB.Games')

                #now fill in the season column
                c.execute("UPDATE Games SET Season= "+str(self.seasons[i])+" WHERE Season IS NULL")

                #first commit and then detach game DB
                c.connection.commit()
                c.execute("DETACH DATABASE GamesDB")

    def calculateAccuracies(self):
        pass
 
   
def Process_Our_Data(dbms):

    OUR_ID='0004'
    COVERS_ID='0005'
    ODDSHARKS_ID='0006'

    cursor=dbms.conn.cursor()

    #write entries to Experts table
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+OUR_ID+"', 'OUR_Predictor') ")
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+COVERS_ID+"', 'COVERS') ")
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+ODDSHARKS_ID+"', 'ODDSHARK') ")

    #grab all games in Expert Predictions database
    all_game_rows= cursor.execute("SELECT * from GAMES").fetchall()
    col_names= np.array(cursor.description)
    games_DF = pd.DataFrame(all_game_rows, columns=col_names[:,0])


    Data_dir='./Data/Market_data/'
    part_file='MarketData_'

    files= list_files(Data_dir, 'xlsx')

    expert_DF=pd.DataFrame()
    #loop over history data in every file in dir and insert them into a DF
    for f in files:
        if part_file in f:
            df = pd.read_excel(Data_dir+f,  engine='openpyxl')
            expert_DF =expert_DF.append(df.iloc[1:])

        expert_DF=expert_DF.fillna(0)



    #Loop over Expert Predictions database games data
    for i in range(len(games_DF)):
        #Get game info
        game_id =  games_DF.iloc[i,0]
        away_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,1]).short
        home_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,2]).short
        date            = games_DF.iloc[i,6]
        date_obj= datetime.strptime(date, "%m/%d/%y")
        result          = int(games_DF.iloc[i,5])

        
        print("\tProcessing our, COVERS & ODDSHARK predictions. \t\tGames: %i/%i  " %(i+1, len(games_DF)) , end="\r", flush=True)


        #find any matching rows from the our prediction dataframe
        row_out = expert_DF.loc[(expert_DF['Away'] == away_team_Short) & (expert_DF['Home'] == home_team_Short) & (expert_DF['Result'] == result) & \
            (expert_DF['Date']==date_obj.strftime("%m/%d/%y"))]

        if len(row_out)>0:

            #OUR PREDICTIONS      
            #Get Probs 
            hist_pred       =  int(row_out['Our prediction'].iloc[0] or 0)
            hist_prob      =     (row_out['Our probs'].iloc[0] or 0)/100

            if hist_prob>0:

                #Write match to database
                Success = int(hist_pred==result)

                if hist_pred==1:
                    hist_AWAY_prob=hist_prob
                    hist_HOME_prob=1-hist_AWAY_prob      
                else:
                    hist_HOME_prob=hist_prob
                    hist_AWAY_prob=1-hist_HOME_prob   

                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, OUR_ID,  hist_AWAY_prob, hist_HOME_prob, Success))
               

            #COVERS
            #Get spreads and convert them to probs 
            cover_away_spreads       =  int(row_out['Covers sides'].iloc[0] or 0)
            cover_home_spreads       =  int(row_out['Unnamed: 16'].iloc[0] or 0)
                
            if  cover_away_spreads !=0 and cover_home_spreads !=0:
                cover_away_probs = Spread2Prob_Convert(cover_away_spreads, [-0.04927,  0.1403, 0.5472, -0.04684])
                cover_home_probs = Spread2Prob_Convert(cover_home_spreads, [-0.04927,  0.1403, 0.5472, -0.04684])

    
                Success = int((int(cover_away_probs<cover_home_probs)+1)==result)
                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, COVERS_ID,  cover_away_probs, cover_home_probs, Success))


            #ODDSHARK
            #Get moneylines and convert them to probs 
            ODDSHARK_away_moneyline       =  int(row_out['ODDSSHARK Moneyline'].iloc[0] or 0)
            ODDSHARK_home_moneyline     =  int(row_out['Unnamed: 20'].iloc[0] or 0)


            if  ODDSHARK_away_moneyline !=0 and ODDSHARK_home_moneyline !=0:

                
                if ODDSHARK_away_moneyline>0:
                    ODDSHARK_away_probs = 100/(ODDSHARK_away_moneyline+100)
                else:
                    ODDSHARK_away_probs =(-ODDSHARK_away_moneyline)/(-ODDSHARK_away_moneyline+100)

                   
                if ODDSHARK_home_moneyline>0:
                    ODDSHARK_home_probs = 100/(ODDSHARK_home_moneyline+100)
                else:
                    ODDSHARK_home_probs =(-ODDSHARK_home_moneyline)/(-ODDSHARK_home_moneyline+100)

                Success = int((int(ODDSHARK_away_probs<ODDSHARK_home_probs)+1)==result)
                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, ODDSHARKS_ID,  ODDSHARK_away_probs, ODDSHARK_home_probs, Success))


    cursor.connection.commit()
    print('done')
  

def Process_538_Data(dbms):

    _538_file='./Data/Experts_data/538_nba_elo.xlsx'
    cursor=dbms.conn.cursor()

    ELO_ID='0001'
    CARMELO_ID='0002'
    RAPTOR_ID='0003'

    #write entries to Experts table
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+ELO_ID+"', '538_ELO') ")
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+CARMELO_ID+"', '538_CARMELO') ")
    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+RAPTOR_ID+"', '538_RAPTOR') ")
    
    
    #grab all 538 entries into a dataframe
    expert_DF = pd.read_excel(_538_file, engine='openpyxl')
    #Fix discrepancies in short names for  teams between NBA.com and FIVETHIRTYEIGHT 
    expert_DF=expert_DF.fillna(0)
    expert_DF = expert_DF.replace(['BRK'],'BKN')
    expert_DF = expert_DF.replace(['CHO'],'CHA')
    expert_DF = expert_DF.replace(['PHO'],'PHX')

    #grab all games in Expert Predictions database into a dataframe
    all_game_rows= cursor.execute("SELECT * from GAMES").fetchall()
    col_names= np.array(cursor.description)
    games_DF = pd.DataFrame(all_game_rows, columns=col_names[:,0])
   


    #Loop over Expert Predictions database games data
    for i in range(len(games_DF)):
        #Get game info
        game_id =  games_DF.iloc[i,0]
        away_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,1]).short
        away_score = int(games_DF.iloc[i,3])
        home_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,2]).short
        home_score = int(games_DF.iloc[i,4])
        date            = games_DF.iloc[i,6]
        date_obj= datetime.strptime(date, "%m/%d/%y")
        result          = int(games_DF.iloc[i,5])


        print("\tProcessing 538 predictions. \t\tGames: %i/%i  " %(i+1, len(games_DF)) , end="\r", flush=True)


        #find any matching rows from the our prediction dataframe
        row_out = expert_DF.loc[(expert_DF['team2'] == away_team_Short) & (expert_DF['team1'] == home_team_Short) & \
            (expert_DF['score2'] == away_score) & (expert_DF['score1'] == home_score) & (expert_DF['date']==date_obj.strftime("%d/%m/%y"))]

        if len(row_out)>0:
            
            #Get ELOs 
            ELO_HOME_prob       = row_out['elo_prob1'] .iloc[0] or 0
            ELO_AWAY_prob       = row_out['elo_prob2'] .iloc[0] or 0

            #Get CARMELOs 
            CARMELO_HOME_prob       = row_out['carm-elo_prob1'] .iloc[0] or 0
            CARMELO_AWAY_prob       = row_out['carm-elo_prob2'] .iloc[0] or 0

            #Get RAPTORs 
            RAPTOR_HOME_prob       = row_out['raptor_prob1'] .iloc[0] or 0
            RAPTOR_AWAY_prob       = row_out['raptor_prob2'] .iloc[0] or 0

            #ELO
            if ELO_AWAY_prob > 0 and ELO_HOME_prob > 0:
                Success = int((int(ELO_AWAY_prob<ELO_HOME_prob)+1)==result)
                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, ELO_ID,  ELO_AWAY_prob, ELO_HOME_prob, Success))

            #CARMELO
            if CARMELO_AWAY_prob > 0 and CARMELO_HOME_prob > 0:
                Success = int((int(CARMELO_AWAY_prob<CARMELO_HOME_prob)+1)==result)
                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, CARMELO_ID,  CARMELO_AWAY_prob, CARMELO_HOME_prob, Success))


            #RAPTOR
            if RAPTOR_AWAY_prob > 0 and RAPTOR_HOME_prob > 0:
                Success = int((int(RAPTOR_AWAY_prob<RAPTOR_HOME_prob)+1)==result)
                cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, RAPTOR_ID,  RAPTOR_AWAY_prob, RAPTOR_HOME_prob, Success))


    cursor.connection.commit()
    print('done')
    

def Process_PredictionTrackerData(Seasons, dbms):
    
    cursor=dbms.conn.cursor()

    #Grab all expets & their ids from the Experts table in the Games database
    current_experts = np.array(cursor.execute("SELECT expert_id, expert_name from Experts").fetchall())
    if len(current_experts)==0:
        expert_names = []
        max_id =10
    else:
        expert_names= list(current_experts[:,1])
        max_id = np.max(current_experts[:,0].astype(int))

 
    #grab all games in Games Database and insert them to frame
    all_game_rows= cursor.execute("SELECT * from GAMES").fetchall()
    col_names= np.array(cursor.description)
    games_DF = pd.DataFrame(all_game_rows, columns=col_names[:,0])


    data_file_partial='./Data/Experts_data/PredictionTracker_'


    expert_DF=pd.DataFrame()
    #loop over history data in every file in dir and insert them into a DF

    for season in Seasons:
        #open PredictionTracker data file
        filename= data_file_partial+str(season)+"-"+str(season+1)[-2:]+".xlsx"
        df = pd.read_excel(filename,  engine='openpyxl') 
        expert_DF =expert_DF.append(df)


    
    #replace team names to standard stats.nba.com abbreviations
    for i in range(len(expert_DF)):
        
        try:
            tH=TeamsList.getTeam_by_partial_Name(expert_DF.iloc[i,1] ).short
        except:
            try:
                tH=TeamsList.getTeam_by_partial_ANY(expert_DF.iloc[i,1] ).short
            except:
                tH=None

        expert_DF.iloc[i,1] = tH

        try:
            tA=TeamsList.getTeam_by_partial_Name(expert_DF.iloc[i,3] ).short
        except:
            try:
                tA=TeamsList.getTeam_by_partial_ANY(expert_DF.iloc[i,3] ).short
            except:
                tA=None
        
        expert_DF.iloc[i,3] = tA



    #Loop over Games dataframe
    for i in range(len(games_DF)):
        #Get game info
        game_id =  games_DF.iloc[i,0]
        away_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,1]).short
        home_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,2]).short
        score_away=games_DF.iloc[i,3]
        score_home=games_DF.iloc[i,4]
        result    = int(games_DF.iloc[i,5])
        date            = games_DF.iloc[i,6]
        date_obj= datetime.strptime(date, "%m/%d/%y")

        
        print("\tProcessing PredictionTracker predictions. \t\tGames: %i/%i  " %(i+1, len(games_DF)) , end="\r", flush=True)

        #find any matching rows with the market dataframe
        row_out = expert_DF.loc[(expert_DF['road'] == away_team_Short) & (expert_DF['home'] == home_team_Short)  & (expert_DF['hscore'] == score_home) & \
            (expert_DF['rscore'] == score_away) & (expert_DF['date'] == date_obj)] 

        if len(row_out)>0:

            #get spreads for each expert
            for j in range( 5, len(row_out.columns)):
                
                #get the lines/spreads
                spread = -row_out.iloc[0,j] #rember that all lines are w.r.t. the home team. 

                if spread !=0 and not math.isnan(spread):

                    #grab the expert
                    expert = row_out.columns[j]
                    
    

                    #first add the expert names in the database
                    if expert not in expert_names:
                        #generate a unique id by incrementing the maximum id
                        max_id +=1
                        expert_id =  str(max_id).zfill(4)
                        expert_names.append(expert)
                        #Add expert to database
                        cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+expert_id+"', '"+expert+"') ")


                    else:
                        #get id associated with bookie
                        expert_id = cursor.execute("SELECT expert_id from Experts WHERE expert_name = '"+expert+"'").fetchone()[0]  

                    home_probs = Spread2Prob_Convert(spread, [-0.04927,  0.1403, 0.5472, -0.04684])
                    away_probs = 1 - home_probs

                    Success = int((int(away_probs<home_probs)+1)==result)
                        
                    cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, expert_id,  away_probs, home_probs, Success))


                    


    cursor.connection.commit()
    print('done')



def Process_OddsPortalData(Seasons, dbms):
    
    cursor=dbms.conn.cursor()

    #Grab all expets & their ids from the Experts table in the Games database
    current_experts = np.array(cursor.execute("SELECT expert_id, expert_name from Experts").fetchall())
    if len(current_experts)==0:
        expert_names = []
        max_id =10
    else:
        expert_names= list(current_experts[:,1])
        max_id = np.max(current_experts[:,0].astype(int))



    #grab all games in Games Database and insert them to frame
    all_game_rows= cursor.execute("SELECT * from GAMES").fetchall()
    col_names= np.array(cursor.description)
    games_DF = pd.DataFrame(all_game_rows, columns=col_names[:,0])


    data_file_partial='./Data/Experts_data/Oddsportal_'
    
    expert_DF=pd.DataFrame()
    #loop over history data in every file in dir and insert them into a DF
    for season in Seasons:
        #open PredictionTracker data file
        filename= data_file_partial+str(season)+"-"+str(season+1)[-2:]+".xlsx"
        df = pd.read_excel(filename,  engine='openpyxl') 
        expert_DF =expert_DF.append(df.iloc[1:])


    
    #Loop over Games dataframe
    for i in range(len(games_DF)):
        #Get game info
        game_id =  games_DF.iloc[i,0]
        away_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,1]).short
        home_team_Short = TeamsList.getTeam_by_ID(games_DF.iloc[i,2]).short
        score_away=games_DF.iloc[i,3]
        score_home=games_DF.iloc[i,4]
        result    = int(games_DF.iloc[i,5])
        date            = games_DF.iloc[i,6]
        date_obj= datetime.strptime(date, "%m/%d/%y")


        print("\tProcessing Oddsportal predictions. \t\tGames: %i/%i  " %(i+1, len(games_DF)) , end="\r", flush=True)

        #find any matching rows with the market dataframe
        row_out= expert_DF.loc[(expert_DF['Away'] == away_team_Short)  & (expert_DF['Home'] == home_team_Short)  & (expert_DF['Score Away'] ==score_away ) & \
            (expert_DF['Score Home'] ==score_home ) & (expert_DF['Date'] == date)]
        
        
        #IF WE HAVE A MATCH only write the Predictions in the database. Non matching games will have to be dropped since we do not have valid NBA.com game ids
        if len(row_out)>0:
            #get spreads for each expert
            for j in range(7, row_out.shape[1]):
                
                try:
                    #capture the expert's name and odds
                    [expert, expert_odds]= row_out.iloc[0,j].split("::")
                    expert_odds= np.array(expert_odds.split(",")).astype(float)
                except:
                    #skip that expert
                    continue

                #first add the expert names in the database
                if expert not in expert_names:
                    #generate a unique id by incrementing the maximum id
                    max_id +=1
                    expert_id =  str(max_id).zfill(4)
                    expert_names.append(expert)
                    #Add expert to database
                    cursor.execute("INSERT OR REPLACE INTO EXPERTS (expert_id, expert_name) Values ('"+expert_id+"', '"+expert+"') ")

                else:
                    #get id associated with bookie
                    expert_id = cursor.execute("SELECT expert_id from Experts WHERE expert_name = '"+expert+"'").fetchone()[0]  

                    try:
                        #covert odds to probls
                        away_probs = 1/expert_odds[0]
                        home_probs = 1/expert_odds[1]
                    except:
                        #skip that expert
                        continue
                    
                    
                    Success = int((int(away_probs<home_probs)+1)==result)

                    cursor.execute("INSERT OR REPLACE INTO Predictions  Values (?,?,?,?,?) ",(game_id, expert_id,  away_probs, home_probs, Success))

    cursor.connection.commit()
    print('done')



def CalculateScores(dbms):
    cursor=dbms.conn.cursor()
    
    #Get the number of games
    n_games= cursor.execute("select (select count() from Games) as count, * from Games").fetchone()[0]

    #Grab all expets & their ids from the Experts table in the Games database
    current_experts = np.array(cursor.execute("SELECT expert_id, expert_name from Experts").fetchall())
    for expert in current_experts:
        predictions = np.array(cursor.execute("SELECT * from Predictions WHERE expert_id = '"+expert[0]+"'").fetchall())
        pred_no = len(predictions) #the number of predictions
        weight = min(pred_no/n_games,1) #this shouldn't really be higher than 1


        if pred_no>0:

            y_prob = predictions[:,2:4].astype(float)
            y_pred = np.argmax(y_prob, axis=1)+1
            gtLabels = np.copy(y_pred)
            for j in range(pred_no):
                if int(predictions[j,4])==0:
                    #flip label
                    if gtLabels[j]==2:
                        gtLabels[j]=1
                    else:
                        gtLabels[j]=2
                

            BS=brier_score_loss(gtLabels, y_prob[:,0], pos_label=1)


            wBS = 1-(1-BS)*weight #Until we find a better way to weigh this

            #add entry to database
            print("\tProcessing Expert : %s \t\t  " %(expert[1]) , end="\r", flush=True)
            cursor.execute("UPDATE Experts set Score = '"+str(BS)+"', Pred_No = '"+str(pred_no)+"', Weight = '"+str(weight)+"' , Score_weighted = '"+str(wBS)+"'   where expert_id = '"+expert[0]+"'")
            

    cursor.connection.commit()            



def create_Database(db_filename, Seasons):

    #generate or load the database
    dbms = MyDatabase(db_filename, Seasons)


    # #Now populate different experts

    #1. 538's ELO/CARMELO/RAPTOR
    Process_538_Data(dbms)

    #2. Get our, covers and oddshark predictions
    Process_Our_Data(dbms)

    #3. Get PredictionTracker data. 
    Process_PredictionTrackerData(Seasons, dbms)

    #4. Get Oddsportal data
    Process_OddsPortalData(Seasons, dbms)

    


    #calculate accuracies for each expert
    CalculateScores(dbms)

    #close the database
    dbms.closeConnection()





def main():
    
    db_filename='.\Libs\Expert_ensemble\ExpertPredictions_DB.db'


    Seasons=[2015, 2016, 2017, 2018, 2019, 2020]
  
    create_Database(db_filename, Seasons)




    

if __name__ == '__main__':
    main()