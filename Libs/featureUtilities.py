from sqlalchemy import inspect
import numpy as np
import joblib
import os.path
import os, sys, inspect

import pandas as pd

from seasonDB_utils import open_database
from PredictPlayerStats import getPlayerPrediction


from ReliefF import ReliefF
from sklearn.feature_selection import VarianceThreshold

from sklearn.feature_selection import SelectKBest, SelectPercentile, SelectFpr, SelectFdr
from sklearn.feature_selection import f_classif, mutual_info_classif

from scipy.stats import skew, kurtosis
from numpy.random import normal

# For importing modules from subfolders
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"./Libs")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)  

from sklearn.linear_model import LogisticRegression


def Spread2Prob_Convert(spread, pars=[1,1,1,1]):
    #function to convert from (signed) spread to probability
 
    a=pars[0]
    b=pars[1]
    c=pars[2]
    d=pars[3]


    #prob= a / (1. + np.exp(-c * (spread - d))) + b
    prob= a*np.exp(b*spread) + c*np.exp(d*spread)
   

    #Supress any unrealisticaly high/low probs
    if prob>1:
        prob=0.98
    
    if prob<0:
        prob=0.2

    return prob



def logistic(x):
    return 1/(1+np.exp(-x))



def selectFeatures(features, labels, nfk):  


    if  not os.path.isfile('./Features/feature_selector.sav'):

        print("Starting feature selection.")

        # #Variance threshold feature selection
        # sel = VarianceThreshold(threshold=0.08 )
        # feature_selector=sel.fit(features)

        #ReliefF
        feature_selector = ReliefF(n_neighbors=100, n_features_to_keep=nfk)
        feature_selector.fit_transform(features, labels)

    
        print("Feature selection completed.")
        
        joblib.dump(feature_selector, './Features/feature_selector.sav')
    
    else:
    
        feature_selector=joblib.load('./Features/feature_selector.sav')         
        


    return feature_selector

def ismember(A, B):
    return [ np.sum(a == B) for a in A ]


def generateAttributeIndices(chosen_attributes):
    #Generate indices of specific types of stats from the sql databases. This is used if we wish to extract specific statistics

    #Generate Player Attribute indices
    pl_att_index=[]
    if sum(ismember(chosen_attributes, "Traditional")):
        pl_att_index.extend(list(range(2,21+1)))
    
    if sum(ismember(chosen_attributes, "Advanced")):
        pl_att_index.extend(list(range(22,41+1)))      
    
    if sum(ismember(chosen_attributes, "Misc")):
        pl_att_index.extend(list(range(42,51+1)))              

    if sum(ismember(chosen_attributes, "Scoring")):
        pl_att_index.extend(list(range(52,66+1))) 

    if sum(ismember(chosen_attributes, "Usage")):
        pl_att_index.extend(list(range(67,84+1))) 

    if sum(ismember(chosen_attributes, "Fourfactors")):
        pl_att_index.extend(list(range(85,92+1))) 

    if sum(ismember(chosen_attributes, "Tracking")):
        pl_att_index.extend(list(range(93,110+1))) 

    if sum(ismember(chosen_attributes, "Hustle")):
        pl_att_index.extend(list(range(111,125+1)))


    return pl_att_index

 
def extractFeaturesFromArray(data_array, Ngames_array):
    """ Extract features from a list of players (e.g. lineup) """

   #Check if all weights are 0. This only happens if players haven't played any games in current season. In that case simply take the mean
    if Ngames_array.all()==0:
        Ngames_array=np.ones(Ngames_array.size)
    
    #calculate weights for weighted mean
    wsum=sum(Ngames_array)
    weights=Ngames_array/wsum

    return np.average(data_array,axis=0, weights=weights)

    

def generate_Features_fromDB(Params,  database_file):

    """ Generates Features and labels from the player boxscore stats in a specific database file  """
    
    seasonFeatures=[] #holds the TEAM features for every game for the whole season  
    seasonLabels=[] #holds the LABELS for every game for the whole season


    #Generate the database indices from the chosen player & team stats
    pl_att_index = np.array(generateAttributeIndices(Params.chosen_attributes))

    dbms = open_database( database_file)   #open the current season database file
    cursor = dbms.conn.cursor()


    
    #Get all the games in the season  
    g_rws = cursor.execute('SELECT * FROM games').fetchall() 


    #loop over games
    for g_row in range(len(g_rws)):

        #Get game ID
        game_id= g_rws[g_row][0]
        print("\t\tGame: %s" % game_id , end="\r", flush=True)

        #get Home and Away team IDs
        awayTeam_id=g_rws[g_row][1]
        homeTeam_id=g_rws[g_row][2]

        #get Lineups for the two teams
        awayLineup = cursor.execute('SELECT player_id FROM Lineups WHERE game_id="'+game_id+'" and  team_id='+awayTeam_id).fetchall()
        homeLineup = cursor.execute('SELECT player_id FROM Lineups WHERE game_id="'+game_id+'" and  team_id='+homeTeam_id).fetchall()    
        
          

        #create two arays that will hold the stats for the players in the lineup of each team
        dfA_stats= np.array([])
        dfA_Ngames=[] #additional list that will hold the number of games played by each player
        dfH_stats= np.array([])
        dfH_Ngames=[] #additional list that will hold the number of games played by each player

        #loop for the players in the AWAY team lineup
        for p_Away in range(len(awayLineup)):
            player_id = awayLineup[p_Away][0]

            #get all the stats for all the games of that player
            stat_rws = np.array(cursor.execute('SELECT * FROM Players  WHERE player_id="'+player_id+'"').fetchone())
             #append the only CHOSEN stats in the array
            if stat_rws.size>1:

                #get the number of games played from the Boxscores table. Used for team-averaging.  
                dfA_Ngames.append(len(cursor.execute('SELECT game_id FROM BoxscoresPlayer  WHERE player_id="'+player_id+'"').fetchall()))
           
                if dfA_stats.size==0:
                    dfA_stats = stat_rws[pl_att_index+4].astype(float)
                else:
                    dfA_stats = np.vstack((dfA_stats, stat_rws[pl_att_index+4].astype(float)))
    
        #loop for the players in the HOME team lineup
        for p_Home in range(len(homeLineup)):
            player_id = homeLineup[p_Home][0]

            #get all the stats for all the games of that player
            stat_rws = np.array(cursor.execute('SELECT * FROM Players WHERE player_id="'+player_id+'"').fetchone())
            #append the only CHOSEN stats in the array
            if stat_rws.size>1:

                #get the number of games played from the Boxscores table. Used for team-averaging 
                dfH_Ngames.append(len(cursor.execute('SELECT game_id FROM BoxscoresPlayer  WHERE player_id="'+player_id+'"').fetchall()))
            
                if dfH_stats.size==0:
                    dfH_stats = stat_rws[pl_att_index+4].astype(float)
                else:
                    dfH_stats=np.vstack((dfH_stats, stat_rws[pl_att_index+4].astype(float)))


        #extract features from the lists 
        Feats_Away= extractFeaturesFromArray(dfA_stats, np.array(dfA_Ngames))
        Feats_Home= extractFeaturesFromArray(dfH_stats, np.array(dfH_Ngames))


        #Append combined feature vector to season array   
        if Params.add_gameno_as_feature:
            seasonFeatures.append(   np.hstack([Feats_Away, Feats_Home, g_row+1])   ) #Add also the game number as a feature
        else:
            seasonFeatures.append(   np.hstack([Feats_Away, Feats_Home])   )  # do not add the game number as a feature

        #Generate labels
        if Params.label_type=="hard": #for classification
            seasonLabels.append(g_rws[g_row][5]) 
        elif Params.label_type=="soft": #for regression
            seasonLabels.append(g_rws[g_row][3]-g_rws[g_row][4]) 


    dbms.closeConnection()  #close the current database file

    return seasonFeatures, seasonLabels



def Predict_Features_forLineup(Params, lineup,  cursor  ):
    ''' Predict future stats using Bayesian inference 
        Assuming all priors are Gaussian and all likelihoods are Gaussian with known standard deviation
        This is why the Posterior is also Gaussian and we can write the updates in closed form
    '''
    #Grab all Boxscore data into a Pandas dataframe, in order to avoid continuous database access
    column_names=[]
    bx_rows = cursor.execute('SELECT * FROM BoxscoresPlayer ').fetchall()
    for i in range(len(cursor.description)):
        column_names.append(cursor.description[i][0])
    bx_df = pd.DataFrame(bx_rows, columns =column_names)


  
    
    #Generate the database indices from the chosen player stats
    pl_att_index = np.array(generateAttributeIndices(Params.chosen_attributes))-2  #remove the +2 padding inbuild into the index


    #Pre-fetch all player priors in the lineup for speed
    priors_df=pd.DataFrame(columns =column_names[1:]) #ignore the game id column name)
    for p in range(len(lineup)):
        player_id = lineup[p]
        priors, _=getPlayerPrediction(Params, str(player_id), 'PlayerStatDatabase.db', False)
        if len(priors)==0:
            continue
        priors= priors.astype(object)
        priors = np.insert(priors, 0, str(player_id))
        priors_df.loc[p] = priors



    #Monte carlo runs
    so_var=np.linspace(0.3, 1, 82)   #widening prior variances
    s_var=np.linspace(1, 0.3, 82)   #narrowing likelihood variances
    
    

    Feats=[]
    for mc in range(Params.MCruns):

        print("\t\tMC runs: %s/%s \t" %(mc+1, Params.MCruns) , end="\r", flush=True)

        #create the numpy array that will hold the stats for ALL the players in the lineup
        df_stats=np.array([])
        dfA_Ngames=[] #additional list that will hold the number of games played by each player
        #loop for each player in the lineup
        for p in range(len(lineup)):
            player_id = lineup[p]


            #obtain PRIOR prediction for that player,season pair from the PlayerStatDatabase
            priors = np.array(priors_df.loc[priors_df['player_id'] == str(player_id)]) 
            if len(priors)==0:
                priors=np.zeros(len(pl_att_index))
            else:
                priors = priors[0,pl_att_index+1].astype(float)  #select only the required features and trim the player_id
            
 
            #obtain LIKELIHOOD for the player in current, test season, directly from the boxscores table 
            prows = np.array(bx_df.loc[bx_df['player_id'] == str(player_id)])
            N= len(prows) #the number of games this player has played this season

            #time-varying sigma and sigma0
            sigma_o=    so_var[N]*np.ones(len(pl_att_index))  #This is the variance for the prior
            sigma=       s_var[N]*np.ones(len(pl_att_index))     #This is the variance for the likelihood
    
            if N==0:
                likelihoods=np.zeros(len(pl_att_index)) #player hasnt played any games yet so set all sample means to zero
                
            else:    
                prows = prows[:,pl_att_index+2].astype(float) #convert to float and only select CHOSEN attributes
                likelihoods =    np.mean(prows, axis=0)  #assuming a Gaussian distribution then the likelihoods are the sample means 
            

            #now calculate the POSTERIOR for all stats
            posteriors = ((N* sigma_o**2 / (N* sigma_o**2 +sigma**2)) * likelihoods  ) +  \
                            (priors * ( sigma**2/(N* sigma_o**2 +sigma**2)  ) )


            post_sigma_squared =  1/(1/ sigma_o**2 + N/sigma**2)


            #Estimate the stats at the next time frame
            if np.count_nonzero(posteriors)>0:
  
                # draw a sample x from the posterior predictive distribution with N(mu=the posterior estimate, and sqrt(sigma_post+sigma) )
                #estimated_observations= normal(posteriors, np.sqrt(post_sigma_squared + sigma**2))   

                estimated_observations = posteriors #simply use the posterior (mu) from the current timeframe


                #update the likelihood as iterative update of sample mean
                estimated_likelihoods = (estimated_observations - likelihoods)/(N+1) + likelihoods
            
                #now get new estimate of posterior (mu) 
                estimated_posteriors = (( (N+1)* sigma_o**2 / ((N+1)* sigma_o**2 +sigma**2)) * estimated_likelihoods) +  \
                            (priors * ( sigma**2/((N+1)* sigma_o**2 +sigma**2)  ) )


                #append player only if he  has nonzero posterior stats 
                dfA_Ngames.append(N)    # Used for team-averaging.  
                if len(df_stats)==0:
                    df_stats=estimated_posteriors
                else:
                    df_stats=np.vstack((df_stats,estimated_posteriors))



        #extract features from the dataframes.
        Feats.append(extractFeaturesFromArray(df_stats, np.array(dfA_Ngames)) )


    return Feats
 

def engineerFeatures(f):

    #"Mean&Var" interleaved stats. Optimising AUC

    # F1 = f[:,177]+ 3/f[:,22] + (10.0735 + 3.65644*f[:,286] - 1.77677*f[:,36] - 3.304204*f[:,38])/(f[:,22]*f[:,250])
    # F2 = (f[:,35] + f[:,296] + 36.5292*f[:,300] + 0.45551*f[:,251] - f[:,48])/f[:,2]
    # F3 = (6.1997 + f[:,298] + 0.050978*f[:,285] - f[:,50] - 0.041351*f[:,37])/f[:,26]
    # F4 = f[:,44] + f[:,288] + f[:,181]*f[:,287] + f[:,253]*f[:,310] - f[:,4] - f[:,40] - f[:,292]
    # F5 = 0.1503*f[:,46] + 0.14606*f[:,290] + f[:,335]*f[:,415] - 0.15031 - 0.14221*f[:,294] - 0.148329*f[:,9] - 0.150312*f[:,42]
    # F6 = f[:,330] + 29.6873*f[:,174]*f[:,414] + f[:,88]*f[:,174]*f[:,414] - f[:,82] - 0.178057*f[:,312] - 1.799617*f[:,28] - 46.013238*f[:,166]*f[:,422]
    # F7 = 0.826733*f[:,316] + 0.041136*f[:,274] + 0.006124*f[:,263] + 0.00283*f[:,89] - f[:,68] - 0.007407*f[:,3] - 0.024460*f[:,336]



    # #"Mean&Var" interleaved stats. Optimising log-loss
    # F1 = (15.0396 + 3.43466*f[:,286])/f[:,36] - 0.282381*f[:,38] - 0.314134*f[:,22]
    # F2 = 1.62432 + 0.054277*f[:,251] + 1.265625*f[:,296]*f[:,353] - f[:,48]*f[:,375] - 0.4187031*f[:,2]
    # F3 = 1.01661 + 0.156339*f[:,298] + f[:,285]*f[:,419] - 0.02928*f[:,3] - 0.1290998*f[:,48] - 0.2610835*f[:,26]
    # F4 = 0.14027 + 0.14027*f[:,288] + f[:,274]*f[:,420] - 0.14262*f[:,292] - 0.15043*f[:,50]
    # F5 = f[:,177] + 0.1563831*f[:,290] + 0.1365159*f[:,44] + 0.0134001*f[:,253] + 46/f[:,0] - 0.151269*f[:,40] - 0.159477*f[:,294]
    # F6 = 24*f[:,414] + 0.148025*f[:,46] + f[:,329]*f[:,420] - 0.1526025*f[:,42] - 0.239049*f[:,336] - 20.77463*f[:,422]
    # F7= 18.0077*f[:,174] + 16.36446*f[:,316] + f[:,287]*f[:,321] - np.log(f[:,337]) - 28.9816*f[:,166]



    # f_out = np.column_stack((F1,F2,F3,F4,F5,F6,F7))    
    
    # #raw features identified from the optimisation
    # f_out = np.column_stack((  f[:,22],  f[:,36],  f[:,38],  f[:,286],  
    #                            f[:,2],   f[:,48],  f[:,251], f[:,296], f[:,353], f[:,375],
    #                            f[:,3],   f[:,26],  f[:,298], f[:,419],
    #                            f[:,50],  f[:,274], f[:,288], f[:,292], f[:,420],
    #                            f[:,0],   f[:,40],  f[:,44],  f[:,177], f[:,253], f[:,290], f[:,294],
    #                            f[:,42],  f[:,46],  f[:,329], f[:,336], f[:,420], f[:,422], f[:,414],
    #                            f[:,166], f[:,174], f[:,287], f[:,316], f[:,321], f[:,337]
    #                              )) 



    MIN=f[:,0]
    f_out=f[:,1:]


    f_out[:,1]=f_out[:,1]/MIN
    f_out[:,2]=f_out[:,2]/MIN
    f_out[:,4]=f_out[:,4]/MIN
    f_out[:,5]=f_out[:,5]/MIN
    f_out[:,7]=f_out[:,7]/MIN
    f_out[:,8]=f_out[:,8]/MIN

    f_out[:,10]=f_out[:,10]/MIN
    f_out[:,11]=f_out[:,11]/MIN
    f_out[:,12]=f_out[:,12]/MIN
    f_out[:,13]=f_out[:,13]/MIN
    f_out[:,14]=f_out[:,14]/MIN

    f_out[:,15]=f_out[:,15]/MIN
    f_out[:,16]=f_out[:,16]/MIN

    f_out[:,17]=f_out[:,17]/MIN
    f_out[:,18]=f_out[:,18]/MIN


    f_out[:,28]=f_out[:,28]/MIN
    f_out[:,41]=f_out[:,41]/MIN
    f_out[:,42]=f_out[:,42]/MIN


    f_out[:,43]=f_out[:,43]/MIN
    f_out[:,44]=f_out[:,44]/MIN
    f_out[:,45]=f_out[:,45]/MIN 

    f_out[:,46]=f_out[:,46]/MIN
    f_out[:,47]=f_out[:,47]/MIN
    f_out[:,48]=f_out[:,48]/MIN
    f_out[:,49]=f_out[:,49]/MIN
    f_out[:,50]=f_out[:,50]/MIN   


    f_out[:,92]=f_out[:,92]/MIN 
    f_out[:,93]=f_out[:,93]/MIN 
    f_out[:,94]=f_out[:,94]/MIN 
    f_out[:,95]=f_out[:,95]/MIN
    f_out[:,96]=f_out[:,96]/MIN 

    f_out[:,97]=f_out[:,97]/MIN 
    f_out[:,98]=f_out[:,98]/MIN 
    f_out[:,99]=f_out[:,99]/MIN 

    f_out[:,100]=f_out[:,100]/MIN 
    f_out[:,101]=f_out[:,101]/MIN 
    f_out[:,102]=f_out[:,102]/MIN 

    f_out[:,104]=f_out[:,104]/MIN 
    f_out[:,105]=f_out[:,105]/MIN 

    f_out[:,107]=f_out[:,107]/MIN 
    f_out[:,108]=f_out[:,108]/MIN 
    
    f_out[:,110]=f_out[:,110]/MIN 
    f_out[:,111]=f_out[:,111]/MIN 
    f_out[:,112]=f_out[:,112]/MIN 
    f_out[:,113]=f_out[:,113]/MIN 
    f_out[:,114]=f_out[:,114]/MIN 
    f_out[:,115]=f_out[:,115]/MIN 
    f_out[:,116]=f_out[:,116]/MIN 
    f_out[:,117]=f_out[:,117]/MIN 
    f_out[:,118]=f_out[:,118]/MIN 
    f_out[:,119]=f_out[:,119]/MIN 


    f_out[:,120]=f_out[:,120]/MIN 
    f_out[:,121]=f_out[:,121]/MIN 
    f_out[:,122]=f_out[:,122]/MIN 
    f_out[:,123]=f_out[:,123]/MIN 
    f_out[:,124]=f_out[:,124]/MIN 


    return f_out







 
