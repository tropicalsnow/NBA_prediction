import sqlite3 #USING SQLITE instead of SQLALCHEMY

import os.path, sys


import numpy as np
import collections #for ordered dictionaries
import operator


from seasonDB_utils import open_database
from printProgressBar import printProgressBar

from scipy.optimize import minimize, nnls, lsq_linear
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor

import multiprocessing 
import math

import functools
import cvxpy as cvx

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


from statsmodels.tsa.arima_model import ARIMA
import pmdarima as pm

class PStatsDatabase:

    def __init__(self, filename):
        self.dbfile=filename  
        self.conn = sqlite3.connect(self.dbfile)

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()


    def create_Players_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Players (player_id TEXT NOT NULL, "
        "player_name TEXT NOT NULL, " 
        "weight FLOAT, "
        "height FLOAT, "
        "draft_year FLOAT,"
        "draft_round FLOAT,"
        "draft_pick FLOAT,"
        "position TEXT,"
        "PRIMARY KEY(player_id))")

        self.conn.commit()

    
    def create_Stats_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Stats ( player_id TEXT NOT NULL," 
        "season INTEGER, "
        "Age INTEGER, "
        "EXP INTEGER, "
        "GP INTEGER )")


    def create_Predicted_Stats_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE PredictedStats ( player_id TEXT NOT NULL," 
        "season INTEGER,"
        "PRIMARY KEY(player_id, season))")
        
        
        self.conn.commit()
        


    def create_db_tables(self):
        self.create_Players_Table()    
        self.create_Stats_Table()
        self.create_Predicted_Stats_Table()
        


def createStatDatabase(Params, db_name=None):
    #Create player stat database from  all available seasons

    if db_name==None:
        stats_database_file='.'+Params.databaseDir+"/PlayerStatDatabase.db"
    else:
        stats_database_file='.'+Params.databaseDir+"/"+db_name

    #Only create the player stat database if it does not exist yet
    if not os.path.isfile(stats_database_file):       

        stats_dbms = PStatsDatabase(stats_database_file)
        # Create Tables
        stats_dbms.create_db_tables()

        stats_cursor= stats_dbms.conn.cursor()




        #Loop through past season games databases
        for s in Params.trainingSeasons: 
            season = str(s-1)+"-"+str(s)[2:4]
            season_databaseFile = '.'+Params.databaseDir+"/NBA_season"+season+".db"

            print("Parsing season "+str(s))
            
            if  os.path.isfile(season_databaseFile):
                season_dbms = open_database(season_databaseFile)   #open the database file
                season_cursor= season_dbms.conn.cursor()

        
                #Add player info and stats from season database to stats database
                p_rows =  np.array(season_cursor.execute('SELECT * FROM Players').fetchall())
                #loop for player
                for p in range(p_rows.shape[0]):

                    player_id=p_rows[p][0]


                    #Find out how many games the player has played in the season
                    GP = len(season_cursor.execute('SELECT * FROM BoxscoresPlayer where player_id="'+player_id+'"').fetchall())
                    

                    #Add to player database  
                    stats_cursor.execute('INSERT OR REPLACE  INTO Players (player_id, player_name, weight, height) VALUES(?,?,?,?)',
                                                (player_id,  p_rows[p][1], p_rows[p][4], p_rows[p][5] ) )

                    #loop for stats
                    season_cursor.execute('select * from Players') #Make sure Season cursor points to Players Table 

                    stat_start=6
                    col_names=[]
                    col_values=[]
                    for i in range(p_rows.shape[1]-stat_start):
                        
                        #Get the stat name
                        col_name=season_cursor.description[i+stat_start][0]  
                        col_names.append(col_name)
                        col_values.append(p_rows[p][i+stat_start])

                        #first check if stat column names exist in the stats table. If not then add them
                        if stats_cursor.execute('Select * from Stats').fetchone() is None:
                            stats_cursor.execute('ALTER TABLE Stats ADD COLUMN '+col_name+' TEXT')

                    #build the sql query for all stats
                    sql = 'INSERT OR REPLACE INTO Stats ("player_id", "season", "Age", "EXP", "GP", "%s") VALUES ("%s", "%s", "%s", "%s", "%s", "%s");' % (
                        '","'.join(col_names), player_id, s, p_rows[p][2], "0", GP, '","'.join(col_values))

                    #Execute query
                    stats_cursor.execute(sql)


            season_dbms.closeConnection()
        
        
        stats_dbms.closeConnection()


def addPredictionToDatabase(cursor, player_id, pred_season, predicted_stats_list):
    
    #build the sql query for all stats
    
    predicted_stats_list = np.array(predicted_stats_list).astype(str)

    
    #point cursor to Stats table in order to get the column names
    s_rows =  cursor.execute('SELECT * FROM Stats').fetchone()
    
    stat_start=5
    col_names=[]
    col_descriptions=cursor.description
    for i in range(len(s_rows)-stat_start):                    
        #Get the stat name
        col_name=col_descriptions[i+stat_start][0]  
        col_names.append(col_name)

        #first check if stat column names exist in the PredictedStats database. If not then add them
        if cursor.execute('Select * from PredictedStats').fetchone() is None:
            try:
                cursor.execute('ALTER TABLE PredictedStats ADD COLUMN '+col_name+' TEXT')
            except:
                pass
                        

    if len(predicted_stats_list) == len(col_names): #sanity check
        
        sql = 'INSERT OR REPLACE INTO PredictedStats ("player_id", "season",  "%s") VALUES ("%s", "%s", "%s");' % (
                '","'.join(col_names), player_id, pred_season, '","'.join(predicted_stats_list))   

        #Execute query
        try:
            cursor.execute(sql)
            return 1
        except:
            return 0
    else:
        return 0
    




def DissimilarityMeasure(player_dict, ref_dict):
    #calculate disimilarity between two player using their stat


    #Sort the two dictionaries by key (age)
    player_d = collections.OrderedDict(sorted(player_dict.items()))
    ref_d =    collections.OrderedDict(sorted(ref_dict.items()))



    #weighted SSE error between points
    MatchError=0 
    for x in player_d:

        if x in ref_d:

            weight_player=player_d[x][1]
            weight_ref=ref_d[x][1]

            weight=  min(weight_player,weight_ref)  #average, minimum or other?
            MatchError=MatchError+   np.power((player_d[x][0]-ref_d[x][0]),2)   / weight  


        else:
            MatchError = MatchError+  np.power(player_d[x][0],2)
    
    
    return MatchError 
 


def weighted_sum_objective(w, arg1, arg2):

    Target = arg1.T
    Ref = arg2.T

    w=w.reshape(len(w),1)

    l=0.0 #regularisation
 
    
    return np.sum(np.power((w*Ref- Target), 2)) + l*np.sum(np.power(w, 2))
 
    

def predictFutureStats(player_id, sorted_Matches, all_player_stats_rows, stat_index, topN):
    
    topN=min(len(sorted_Matches), topN)

    #Get stats of target player    
    p_indx=all_player_stats_rows[:,0]==player_id
    player_stats_rows=all_player_stats_rows[p_indx,:]


    # player_stats_rows =  np.array(stats_cursor.execute('SELECT * FROM Stats where player_id="'+player_id+'"').fetchall())
    player_stat_X=player_stats_rows[:,2].astype(int)
    player_stat_Y=player_stats_rows[:,stat_index].astype(float)


    next_season_age=int(player_stats_rows[-1,:][2])+1

    
    #ARIMA. Use arima as endogenous regression on the new season and append it to player_stat_Y array
    if np.all(player_stat_Y==0):       
        player_stat_Y=np.append(player_stat_Y,player_stat_Y[-1])
    else:

        model = pm.ARIMA(order=(0,0,0), maxiter=100, method='powell')
        fitted  = model.fit(player_stat_Y)
        APRED=fitted.predict(1)[0]
        player_stat_Y=np.append(player_stat_Y,APRED)
        
    
    player_stat_X=np.append(player_stat_X, next_season_age)

         




    Ref=np.zeros([len(player_stat_X), topN]) #matrix to hold the statistics of the topN players. we will use this to calculate the prediction weights for the target player
    Ref_weights=np.zeros(topN)
    Ref_next= np.zeros([topN])  #matrix to hold the statistics of the topN players for the next season. We will use this together with the calculated weights to generate the prediction
    #Get stats of topN matched players
    for i in range(topN):

        Ref_weights[i]=sorted_Matches[i][1]
        match_player_id=sorted_Matches[i][0]
        m_indx=all_player_stats_rows[:,0]==match_player_id

        match_player_stats_rows=all_player_stats_rows[m_indx,:]
        match_player_stat_X=match_player_stats_rows[:,2].astype(int)
        match_player_stat_Y=match_player_stats_rows[:,stat_index].astype(float)

        #populate Reference matrix only at x locations (i.e. age) given by target player
        for s in range(len(player_stat_X)):
            loc= np.where(match_player_stat_X==player_stat_X[s])
            if loc[0].size>0:
                Ref[s,i]  = match_player_stat_Y[loc]


        #append the stat from the next season (i.e. to be predicted)
        next_season_match_stat=  match_player_stat_Y[np.where(match_player_stat_X==next_season_age)][0]
        Ref_next[i] = next_season_match_stat


    #Remove any entries in the Ref array where all players have 0 values
    non_zero_indx=[]
    for t in range(Ref.shape[0]):
        if any(Ref[t,:] > 0 ):
            non_zero_indx.append(t)


    #weighted SSE
    objective_fun = functools.partial(weighted_sum_objective, arg1=player_stat_Y, arg2=Ref) 
    x0=np.ones([topN])
    out= minimize(objective_fun, x0, options={'disp': False, 'maxiter':200}) 
    predicted_stats=np.mean(Ref_next*out.x)
    
    # Various linear combination
    # [x,resid,rank,s] = np.linalg.lstsq(Ref[non_zero_indx,:],player_stat_Y[non_zero_indx]) #least-squares solution to a linear matrix equation (Numpy)
    # [x,resid]=nnls(Ref[non_zero_indx,:],player_stat_Y[non_zero_indx])  #non-negative least squares
    # out=lsq_linear(Ref[non_zero_indx,:],player_stat_Y[non_zero_indx], bounds=(0, np.inf)) # least squares with bound constraints (Scipy)   
    # predicted_stats=np.sum(out.x.T*Ref_next) #Linear combination of players
    

    # #using cvxpy
    # x = cvx.Variable(topN)
    # A=Ref[non_zero_indx,:]
    # b=player_stat_Y[non_zero_indx]
    # objective = cvx.Minimize(cvx.sum_squares(A*x - b))
    # constraints = [cvx.sum(x) == 1, x>=0] #convex
    # prob = cvx.Problem(objective, constraints)   
    # result = prob.solve()
    # predicted_stats=np.sum(x.value.T*Ref_next) 





    # #using regression type 1
    # x_train=Ref  #topN-dim features x num_seasons observations
    # y_train=player_stat_Y #num_seasons labels
    # # model = KNeighborsRegressor(n_neighbors=3)
    # model =RandomForestRegressor(max_depth=2, random_state=0)
    # model.fit(x_train, y_train)
    # predicted_stats=model.predict(Ref_next.reshape(1,-1))[0] #topN-dim prediction feature vector




    # # using regression type 2
    # x_train=Ref.T
    # y_train=Ref_next
    # # model = KNeighborsRegressor(n_neighbors=3)
    # model =RandomForestRegressor(max_depth=4, random_state=0)
    # #model.fit(x_train, y_train)
    # model.fit(x_train, y_train, sample_weight=Ref_weights)
    # predicted_stats=model.predict(player_stat_Y.reshape(1,-1))[0]
    # if math.isnan(predicted_stats):
    #     predicted_stats=0

    
  
 

    return predicted_stats


def evaluate_prediction_for_Player(Params, GT_player_info_row, player_stats_rows, predicted_stats_list, verbose=True ):
    #calculate average prediction error & baseline error of stats
    Error=[]
    baselineError=[]


    #BASELINE prediction. Just use the data from the last season (if exist)
    if len(player_stats_rows)==0:
        baseline_predicted_stats_list = np.empty(len(player_stats_rows[0][5:]))
        baseline_predicted_stats_list[:] = np.nan
    else:
        baseline_predicted_stats_list=np.zeros(len(player_stats_rows[0][5:]))
        for i in range(1,len(player_stats_rows)+1):
            if Params.testSeason>int(player_stats_rows[-i][1]):
                baseline_predicted_stats_list=player_stats_rows[-i][5:].astype(float)
                break



    for p_stat in range(len(predicted_stats_list)):
        
        #PREDICTION
        #compare with ground truth. Using simple indexing. This will not work well if we are predicting subindices of stats
        GT=max(abs(float(GT_player_info_row[p_stat+6])), 1e-012)
        pcnt_err= min(abs(predicted_stats_list[p_stat]-float(GT_player_info_row[p_stat+6]))  /  GT,5) #capped at 1 (i.e. 500%)
        Error.append(pcnt_err)

        #BASELINE
        #compare with ground truth. Using simple indexing. This will not work well if we are predicting subindices of stats
        b_pcnt_err=min(abs(baseline_predicted_stats_list[p_stat]-float(GT_player_info_row[p_stat+6]))  /  GT,5) #capped at 1 (i.e. 500%)
        baselineError.append(b_pcnt_err)

    Error=np.array(Error)
    baselineError=np.array(baselineError)
    
    if verbose:
        print("\nAVERAGE stat prediction error for player is: %f "%(np.mean(Error)))   
        print("BASELINE AVERAGE prediction error for player  is: %f  \n\n"%(np.mean(baselineError)))

        #Break down errors into stats types
        print("\t Traditional stats error: %f (base: %f) "%(np.mean(Error[0:20]), np.mean(baselineError[0:20])))
        print("\t Advanced stats error: %f (base: %f) "%(np.mean(Error[20:40]), np.mean(baselineError[20:40])))
        print("\t Misc stats error: %f (base: %f) "%(np.mean(Error[40:50]),np.mean(baselineError[40:50])) )
        print("\t Scoring stats error: %f (base: %f) "%(np.mean(Error[50:65]), np.mean(baselineError[50:65]))) 
        print("\t Usage stats error: %f (base: %f) "%(np.mean(Error[65:85]), np.mean(baselineError[65:85]))  )
        print("\t Fourfactors stats error: %f (base: %f) "%(np.mean(Error[85:91]), np.mean(baselineError[85:91])) )
        print("\t Tracking stats error: %f (base: %f) "%(np.mean(Error[91:109]), np.mean(baselineError[91:109])) )
        print("\t Hustle stats error: %f (base: %f) \n\n"%(np.mean(Error[109:124]), np.mean(baselineError[109:124])))


    #Print weighted error of top 50 features
    feature_index=[19, 24, 25, 13, 18,  0,  3,  1, 36, 10,  9,  4, 11, 41, 8, 20, 30, 87,
                   80, 34, 103, 38, 105, 66, 37, 90, 47, 85, 7, 60, 5, 98, 76, 49, 67, 40,
                   33, 27, 97, 51, 79, 2, 81, 70, 59, 56, 72, 73, 22,  94]

    feature_weights= np.array([0.03962618, 0.0391852 , 0.01784355, 0.01283249, 0.01219561,
                      0.00973923, 0.00890767, 0.00792196, 0.00736699, 0.00710438,
                      0.00706269, 0.00679113, 0.00668696, 0.00638061, 0.00634992,
                      0.00625606, 0.00613168, 0.00599632, 0.00597178, 0.005811  ,
                      0.00580586, 0.00571098, 0.00569257, 0.00539315, 0.00538026,
                      0.00537566, 0.00531788, 0.00515918, 0.00515737, 0.00508881,
                      0.00505557, 0.00496576, 0.00496346, 0.00490503, 0.00488405,
                      0.00486041, 0.00480642, 0.00477501, 0.00471107, 0.00470729,
                      0.00469609, 0.00468946, 0.00465937, 0.00465698, 0.00458559,
                      0.00455966, 0.00454386, 0.0045198 , 0.00449064, 0.0044736 ] )                  
    feature_weights= feature_weights/sum(feature_weights)
    wError          =   np.sum(Error[feature_index]*feature_weights)
    wbaselineError  =   np.sum(baselineError[feature_index]*feature_weights)

    if verbose:
        print("WEIGHTED Error of top 50 features: %f "%(wError)  )    
        print("BASELINE WEIGHTED Error of top 50 features: %f "%(wbaselineError)  )    


    return Error, wError, wbaselineError


def calculatePlayersMatch(stat_index, stat_dict, player_stats_rows, all_player_stats_rows, m_player_id):
    ''' find a match between a reference player and a target player   '''

    indx=all_player_stats_rows[:,0]==m_player_id
    match_player_stats_rows=all_player_stats_rows[indx,:]

    #Create dictionary of stat indexed by age
    match_player_stat_dict= {}
    for d in range(len(match_player_stats_rows)):
        weight= int(match_player_stats_rows[d,2])/82 #the weight of the stat is determined by the number of games the player has played in the season. Max games =82  means max weight =1
        match_player_stat_dict[match_player_stats_rows[d,1]] = [float(match_player_stats_rows[d,3]), weight]


    #Ignore any players that we cannot extrapolate from (i.e. their max age is not larger than current age of player of interest)
    next_season_age=str(int(player_stats_rows[-1,:][2])+1)
    if next_season_age in match_player_stat_dict:

        
        #Calculate matching score between player and reference player from database
        MatchError=DissimilarityMeasure(stat_dict, match_player_stat_dict)

    else:

        MatchError=None
    


    return MatchError, m_player_id
 
 
def pool_worker(player_stats_rows, all_players_info_rows, all_player_stats_rows, player_id, stat_index, topN):
    """ calculate the prediction for the parallel pool  """

    num_stats = player_stats_rows.shape[1]
    printProgressBar(stat_index -5 + 1, num_stats-5, prefix = 'Progress:', suffix = 'Complete ', length = 50)

    #Create dictionary of stat indexed by age
    stat_dict= {}

    for d in range(len(player_stats_rows)):
        weight= int(player_stats_rows[d,4])/82 #the weight of the stat is determined by the number of games the player has played in the season. Max games =82  means max weight =1
        stat_dict[player_stats_rows[d,2]] = [float(player_stats_rows[d,stat_index]), weight]
    

    #Loop through ALL other players in the database to find matches
    Matches_dict={}
    
    match_player_single_stat=all_player_stats_rows[:,[0,2,4,stat_index]]
    for id in all_players_info_rows[:,0]:
        MatchError, match_player_id=calculatePlayersMatch(stat_index, stat_dict, player_stats_rows, match_player_single_stat, id) #Only pass the single stat
        
        if MatchError != None:                            
            #Add info to Matches dictionary
            Matches_dict[match_player_id] = MatchError
 
    #Find highest matching players
    Matches_dict = sorted(Matches_dict.items(), key=operator.itemgetter(1))
 
    #Predict next season
    predicted_stats=predictFutureStats(player_id, Matches_dict, all_player_stats_rows, stat_index, topN)
    # print("\tPredicted stat for next season: %f  \t\t\t\t\t "%(predicted_stats) )

    
    return predicted_stats






def getPlayerPrediction(Params, player_id, db_name=None, verbose=False):


    
    #Open database for access
    if db_name==None:
        stats_database_file=Params.databaseDir+"/PlayerStatDatabase.db"
    else:
        stats_database_file=Params.databaseDir+"/"+db_name
    
    stats_dbms = open_database(stats_database_file)   
    stats_cursor= stats_dbms.conn.cursor()


    #Get info of target player
    player_info_row = np.array(stats_cursor.execute('SELECT * FROM Players where player_id="'+player_id+'"').fetchone())
    player_stats_rows =  np.array(stats_cursor.execute('SELECT * FROM Stats where player_id="'+player_id+'"').fetchall())

    
    #check if the player+season combination already exists in the Prediction table
    srow=np.array(stats_cursor.execute('SELECT * FROM PredictedStats where player_id="'+player_id+'" and season="'+str(Params.testSeason)+'"').fetchone()).astype(float)
    if srow.size == 1:
        if player_info_row.size==1:
            if verbose:    
                print("Rookie. ID= %s."%player_id)
            prediction=np.array([]) #return empty array
        else:
            print("Predicting player  (",player_id,") ",player_info_row[1]) 
            
            #check how many past seasons we have in the database
            if player_stats_rows.shape[0]<=1:
                #Too few past seasons to calculate a prediction. So our prediction is simply the average of the past two seasons
                print("\t\tLess than 2 seasons. Using previous season stats as the prediction")
                
                if player_stats_rows.shape[0]>1:
                    w1=int(player_stats_rows[-1,4])
                    w2=int(player_stats_rows[-2,4])
                    sw=w1+w2; w1=w1/sw;  w2=w2/sw
                    predicted_stats_list=(w1*player_stats_rows[-1,5:].astype(float)+w2*player_stats_rows[-2,5:].astype(float))
                else:
                    predicted_stats_list=player_stats_rows[-1,5:].astype(float)

            else:
                #Calculate the prediction and add it to the database
                print("\t\tRecord does not exist. Matching.")
                col_names= stats_cursor.description

                #Get BASIC info on all other players in database
                all_players_info_rows= np.array(stats_cursor.execute('SELECT * FROM Players where player_id !="'+player_id+'"').fetchall())
                #Get STATS infor on all other players in the database BUT only within the years in the training season
                all_player_stats_rows = np.array(stats_cursor.execute('SELECT * FROM Stats where season in ({seq})'.format(seq=','.join(['?']*len(Params.trainingSeasons))), Params.trainingSeasons ).fetchall())

                #loop for stats using a parallel pool
                predicted_stats_list=[]
                num_stats=len(player_stats_rows[0])                
                

                #MULTI-CPU VERSION
                pool = multiprocessing.Pool(12)
                results = [ pool.apply_async(pool_worker, args = (player_stats_rows, all_players_info_rows, all_player_stats_rows, player_id, stat_index, Params.topN)  ) for stat_index in range(5,num_stats)]   
                pool.close()
                pool.join()
                #Grab the results. These should be in order otherwise the stat predictions will be wrong
                for p in results:    
                    predicted_stats_list.append(p.get())

                # # SINGLE CPU VERSION
                # for stat_index in range(5,num_stats):
                #     result = pool_worker(player_stats_rows, all_players_info_rows, all_player_stats_rows, player_id, stat_index, Params.topN)
                #     predicted_stats_list.append(result)


     

            prediction = np.array(predicted_stats_list).astype(float) 

        #Add to Predicted Stats database
        addPredictionToDatabase(stats_cursor, player_id, Params.testSeason, prediction)


    else:
        if verbose:
            print("\t\tPredictions already exist in the database")
        prediction=srow[2:] #skip the first two columns
    

    
    #Finish and close database
    stats_dbms.closeConnection()

    return prediction, player_stats_rows

