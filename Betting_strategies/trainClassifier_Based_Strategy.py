#TODO: MODIFY THIS WITH PROPER TRAIN, VAL and TEST DATA

import sys
import numpy as np
import joblib
import os.path
import os, sys, inspect

sys.path.append('./')



from runBacktest_modular import LoadBackTestData, LoadAdditionalExpertsData

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn import model_selection 
from sklearn.metrics import brier_score_loss

 




def main(validate):

    # TODO: Make this into a loop


    #Load Market data & Additional ODDSHARK data
    Market_history_file0='./Data/MarketData_2015-16.xlsx'
    no_games0, results0, our_probs0, our_prediction0, market_odds0, market_prediction0, CARMELO0,  COVERS0, ODDSHARK0, H2H0, ODDSHARK_LastN_Away0, ODDSHARK_LastN_Home0 = LoadBackTestData(Market_history_file0)
    
    Market_history_file1='./Data/MarketData_2016-17.xlsx'
    no_games1, results1, our_probs1, our_prediction1, market_odds1, market_prediction1, CARMELO1,  COVERS1, ODDSHARK1, H2H1, ODDSHARK_LastN_Away1, ODDSHARK_LastN_Home1 = LoadBackTestData(Market_history_file1)

    Market_history_file2='./Data/MarketData_2017-18.xlsx'
    no_games2, results2, our_probs2, our_prediction2, market_odds2, market_prediction2, CARMELO2,  COVERS2, ODDSHARK2, H2H2, ODDSHARK_LastN_Away2, ODDSHARK_LastN_Home2 = LoadBackTestData(Market_history_file2)

    Market_history_file3='./Data/MarketData_2018-19.xlsx'
    no_games3, results3, our_probs3, our_prediction3, market_odds3, market_prediction3, CARMELO3,  COVERS3, ODDSHARK3, H2H3, ODDSHARK_LastN_Away3, ODDSHARK_LastN_Home3 = LoadBackTestData(Market_history_file3)
    
 

    #Load additional experts data
    Experts_history_file0='./Data/Experts/PredictionTracker_2015-16.xlsx'
    line0, lineavg0, linesag0, linesage0, linesagp0, lineopen0, linemoore0, linepower0, linesaggm0, linefox0, linedok0, linetalis0, linemassey0, linepugh0, linedonc0 = \
    LoadAdditionalExpertsData(Experts_history_file0,Market_history_file0)

    Experts_history_file1='./Data/Experts/PredictionTracker_2016-17.xlsx'
    line1, lineavg1, linesag1, linesage1, linesagp1, lineopen1, linemoore1, linepower1, linesaggm1, linefox1, linedok1, linetalis1, linemassey1, linepugh1, linedonc1 = \
    LoadAdditionalExpertsData(Experts_history_file1,Market_history_file1)

    Experts_history_file2='./Data/Experts/PredictionTracker_2017-18.xlsx'
    line2, lineavg2, linesag2, linesage2, linesagp2, lineopen2, linemoore2, linepower2, linesaggm2, linefox2, linedok2, linetalis2, linemassey2, linepugh2, linedonc2  = \
    LoadAdditionalExpertsData(Experts_history_file2,Market_history_file2)

    Experts_history_file3='./Data/Experts/PredictionTracker_2018-19.xlsx'
    line3, lineavg3, linesag3, linesage3, linesagp3, lineopen3, linemoore3, linepower3, linesaggm3, linefox3, linedok3, linetalis3, linemassey3, linepugh3, linedonc3  = \
    LoadAdditionalExpertsData(Experts_history_file3,Market_history_file3)
 

    #Create features and labels. 
    features_set0=np.column_stack((our_probs0,market_odds0, CARMELO0, COVERS0, ODDSHARK0, H2H0,\
    line0, lineavg0, linesag0, linesage0, linesagp0, lineopen0, linemoore0, linepower0, linesaggm0, linefox0, linedok0, linetalis0, linemassey0, linepugh0, linedonc0))
    #ODDSHARK_LastN_Away0, ODDSHARK_LastN_Home0))  
    labels0=results0
    
    
    features_set1=np.column_stack((our_probs1,market_odds1, CARMELO1, COVERS1, ODDSHARK1, H2H1,\
    line1, lineavg1, linesag1, linesage1, linesagp1, lineopen1, linemoore1, linepower1, linesaggm1, linefox1, linedok1, linetalis1, linemassey1, linepugh1, linedonc1))
    #ODDSHARK_LastN_Away1, ODDSHARK_LastN_Home1))  
    labels1=results1


    features_set2=np.column_stack((our_probs2,market_odds2, CARMELO2,  COVERS2, ODDSHARK2, H2H2,\
    line2, lineavg2, linesag2, linesage2, linesagp2, lineopen2, linemoore2, linepower2, linesaggm2, linefox2, linedok2, linetalis2, linemassey2, linepugh2, linedonc2))
    #ODDSHARK_LastN_Away2, ODDSHARK_LastN_Home2))  
    labels2=results2

    features_set3=np.column_stack((our_probs3,market_odds3, CARMELO3,  COVERS3, ODDSHARK3, H2H3,\
    line3, lineavg3, linesag3, linesage3, linesagp3, lineopen3, linemoore3, linepower3, linesaggm3, linefox3, linedok3, linetalis3, linemassey3, linepugh3, linedonc3 ))
    #ODDSHARK_LastN_Away3, ODDSHARK_LastN_Home3))
    labels3=results3

 
 

    #Combine past data (featurse and labels)
     
    past_training_features=np.append(features_set0, np.append(features_set1, features_set2, 0), 0)
    past_training_labels=np.append(labels0, np.append(labels1,labels2,0),0)
 

   


    #Build classifier model
    #model = GradientBoostingClassifier(n_estimators=20,learning_rate =0.05)        
    #model = SGDClassifier(loss="hinge", penalty="elasticnet", max_iter=10)       
    #model = neighbors.KNeighborsClassifier(n_neighbors=4)                          
    #model = GaussianNB()                                                         
    model = BaggingClassifier(KNeighborsClassifier(n_neighbors=4), n_estimators=10, max_samples=0.5, max_features=0.5,bootstrap=False, bootstrap_features=False)         
    #model = RandomForestClassifier(n_estimators=500, max_depth=2)                              
    #model = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=2)                   
    #model =  LogisticRegression(solver='lbfgs')                                                
    #model = MLPClassifier(solver='lbfgs', alpha=1e-5,  hidden_layer_sizes=(20,))              

    #Calibrate the model's probabilities
    model = CalibratedClassifierCV(model, cv=10, method='isotonic')



    if validate:
        runs = 500


        Accu=[]
        Brier=[]

        for r in range(runs):



            #Randomly split the data into  training and  test sets
            current_training_features, current_test_features, current_training_labels, current_test_labels =  model_selection.train_test_split(features_set3,labels3,test_size=0.5)    
            

            training_features=np.append(current_training_features,past_training_features,0)  #add current season data in training
            training_labels=np.append(current_training_labels,past_training_labels,0)        #add current season data in training
            
          
            #Train the classifier
            model.fit(training_features,training_labels)


            #Validate classifier on training data
            p_test = model.predict(current_test_features)
            p_probs= model.predict_proba(current_test_features)

            y_true = (p_test==current_test_labels).astype(int) 
            acc= np.mean((p_test==current_test_labels).astype(int))
            br=brier_score_loss(y_true, np.max(p_probs,1))
   

            print("Run ",str(r+1)," out of ", str(runs),":  [tr:",str(training_features.shape),", ts:",str(len(current_test_labels)),"]: ",str(acc),". Brier score: ",str(br))
    
            
            Accu.append(acc)
            Brier.append(br)


        print("Avg. testing accuracy: "+str(np.mean(Accu,0))+". Avg. Brier score: "+str(np.mean(Brier,0)))


    else:


        #Train on full dataset and return model
        #FULL_features=np.append(past_training_features,features_set3,0) #include current season data
        #FULL_labels=np.append(past_training_labels,labels3,0) #include current season data
        FULL_features=past_training_features #do not include current season data
        FULL_labels=past_training_labels #do not include current season data

        #Train the classifier
        model.fit(FULL_features,FULL_labels)
        joblib.dump(model, './Betting_strategies/classifier_Based_Strategy_model.sav')
        



if __name__ == '__main__':

    validate=False
    main(validate) 
