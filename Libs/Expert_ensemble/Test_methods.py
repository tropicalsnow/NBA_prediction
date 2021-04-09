import pandas as pd
from sklearn.metrics import brier_score_loss
import numpy as np


#TODO: Move methods to be called outside in the ensemble_methods.py file



def best_N_experts(X_trainval, y_trainval,  X_test, y_test, Nreplicates=10, type='Brier_weighted', average='median'):
    
    from sklearn.model_selection import train_test_split
    from scipy import stats
    
    n_experts=X_trainval.shape[1]
    y_trainval_bin=(y_trainval==1).astype(int) #convert to Away-based binary labels


    #Setup the grid search
    coeff_grid=np.arange(1,n_experts,5)
    Ntest= len(coeff_grid)
    TestScores = np.ones(Ntest)

    Nopt=np.zeros(Nreplicates).astype(int)
    for rep in range(Nreplicates):


        for tst in range(Ntest):

            N= coeff_grid[tst]

            #shuffle the data and split into training and validation sets
            X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval_bin, test_size=0.3,  shuffle=True) 
            
            n_train = X_train.shape[0]

            #determine the Brier scores of all predictors (in the given order) and also the number of predictions
            #from the training data. Any prediction at 0.5 is counted as a no-prediction
            Brier_Scores = np.ones(n_experts)
            weights = np.zeros(n_experts)
            for i in range(n_experts):
                Brier_Scores[i]=brier_score_loss(y_train, X_train[:,i], pos_label=1)
                weights[i]=sum(X_train[:,i]!=0.5)/n_train
            
            Brier_Scores_weighted = 1-(1-Brier_Scores)*weights 



            #choose the type of experts
            if type == 'Brier':
                #Get expert on pure Brier Score
                Scores = Brier_Scores
            elif type =='Brier_weighted':
                #Get expert on weighted Brier Score
                Scores = Brier_Scores_weighted

            
            #Determine the number of top experts
            sorted_expert_indices = np.argsort(Scores)
            #keep only the top N experts
            sorted_expert_indices= sorted_expert_indices[:N]

            #now test on the validation set
            predictions = X_val[:,sorted_expert_indices]

            #Average the experts
            if average=='weighted':
                y_prob = np.average(predictions, axis=1, weights= weights[sorted_expert_indices])
            elif average=='median':
                y_prob= np.median(predictions,axis=1)
            else: #simple unweighted averaging
                y_prob=np.mean(predictions, axis=1)

            #calculate the Brier score on the valdation data
            TestScores[tst]= brier_score_loss(y_val, y_prob, pos_label=1)



        #Take the parameter with the minimum Brier score
        tst_index = np.argmin(TestScores)
        Nopt[rep] = coeff_grid[tst_index]

    #Get the mode as the most optimal value
    Nopt = stats.mode(Nopt)[0][0]


    #Now evaluate on the test set. The expert indices of both train_val and test sets should be identical
    
    #Determine the number of top experts from the full train_val set. Any prediction at 0.5 is counted as a no-prediction
    Brier_Scores = np.ones(n_experts)
    weights = np.zeros(n_experts)
    n_train = X_trainval.shape[0]
    for i in range(n_experts):
        Brier_Scores[i]=brier_score_loss(y_trainval_bin, X_trainval[:,i], pos_label=1)
        weights[i]=sum(X_trainval[:,i]!=0.5)/n_train
    
    Brier_Scores_weighted = 1-(1-Brier_Scores)*weights 


    #choose the type of experts
    if type == 'Brier':
        #Get expert on pure Brier Score
        Scores = Brier_Scores
    elif type =='Brier_weighted':
        #Get expert on weighted Brier Score
        Scores = Brier_Scores_weighted

        
   
    sorted_expert_indices = np.argsort(Scores)
    #keep only the top N experts
    sorted_expert_indices= sorted_expert_indices[:Nopt]

    #now test on the test set
    predictions = X_test[:,sorted_expert_indices]


    #Average the experts
    if average=='weighted':
        y_prob = np.average(predictions, axis=1, weights= weights[sorted_expert_indices])
    elif average=='median':
        y_prob= np.median(predictions,axis=1)
    else: #simple unweighted averaging
        y_prob=np.mean(predictions, axis=1)


    return brier_score_loss(y_test, y_prob, pos_label=1), Nopt


def Eureqa(X_test, y_test):
 
    y_prob = X_test[:,32] + 0.1446781*X_test[:,16] + 0.1019621*X_test[:,3] - 0.119421*X_test[:,37] - 0.1363072*X_test[:,12]

    return brier_score_loss(y_test, y_prob, pos_label=1)
 

def Stacker(X_trainval, y_trainval, X_test, y_test, Params=None):

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold, GridSearchCV

  
 
    #setup the classifier and perform cross validation
    model = LogisticRegression( penalty='elasticnet', solver='saga', warm_start=True, max_iter=10000)

    if Params is None:

        param_grid= { 'l1_ratio' : [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], 'fit_intercept':[True, False], 'C':[0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5,2]}


        #setup grid search on the train+val data.
        kfold = KFold(n_splits=5, shuffle=True)
        grid_search = GridSearchCV(model, param_grid, cv=kfold,  scoring='neg_brier_score', n_jobs=-1) 
        grid_search.fit(X_trainval, y_trainval) 
    
        print("The best parameters recovered: ", grid_search.best_params_)
        print("Cross-validation score: ", grid_search.best_score_)
        print("Score on test set: ", grid_search.score(X_test, y_test))

        #Now calculate the brier score of the best model on the test data
        #grid_search.best_estimator_ #do we need to acchess this? grid_search should have this model already. Unless we wish to refit without re-searching the grid
        y_prob=grid_search.predict_proba(X_test)

    else:
        #Inject parameters into the model
        for key in Params.keys():
            exec("model."+key+"="+str(Params[key]))

        #train the model
        model.fit(X_trainval, y_trainval) 

        #predict probabilities
        y_prob=model.predict_proba(X_test)
            

    return brier_score_loss(y_test, y_prob[:,0], pos_label=1)
 



def StackerTPOT(X_trainval, y_trainval, X_test, y_test):
    import tpot

    from sklearn.model_selection import RepeatedStratifiedKFold
    from tpot import TPOTClassifier

    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    model = TPOTClassifier(generations=5, population_size=50, cv=cv, scoring='neg_brier_score', verbosity=2, random_state=1, n_jobs=-1)
    model.fit(X_trainval, y_trainval)

    model.export('tpot_best_model.py')


    #Now calculate the brier score of the best model on the test data
    y_prob=model.predict_proba(X_test)


    return brier_score_loss(y_test, y_prob[:,0], pos_label=1)




def GlobalBrier_optimiser(X_trainval, y_trainval, weights_trainval,  X_test, y_test, curr_year=2020):
 
    from scipy.optimize import minimize,  Bounds
    import functools
    from sklearn.model_selection import KFold, train_test_split


    #the residual cost function to minimise
    def forecast_error_func(x, arg1, arg2, arg3, arg4, arg5):
        

        Data= arg1
        Outcome =arg2
        weights = arg3

        P_est =  Data @ x  #weighted Arithmetic mean
        #P_est =  np.power(np.prod(np.power(Data , x),axis=1), 1/sum(x))   #weighted Geometric mean

        r = P_est - Outcome 

        l1=arg4 #regularisation coefficient
        l2=arg5 #regularisation coefficient


        reg1 = l1*np.sum(x*x) #L2 norm
        reg2 = l2*np.sum(abs(x)) #L1 norm

        #Elastic NET

        

        # W=np.ones(len(Outcome))  #flat
        # W = np.exp((curr_year-weights))   #exponential
        # W = (curr_year-weights)**2 #squared
        # W= 2**(curr_year-weights) # power
        W= np.log(1+ curr_year-weights) #logarihmic
        return np.sum(  (r*r)  *   W   )/len(Outcome)  +reg1 + reg2
    


    def constraint1(x):
        return np.sum(x)-1


  

    n_experts=X_trainval.shape[1]
    y_trainval_bin=(y_trainval==1).astype(int) #convert to Away-based binary labels
    
    #constraints and bounds for the optimisation
    cons = {'type': 'eq', 'fun': constraint1} 
    bnds = Bounds(0,1)

    

    #Set up the grid search
    Ntests=50
    coeff_grid=np.linspace(0,1,Ntests)
    Brier_Scores=np.ones(Ntests)

    for i in range(Ntests):

        coeff=coeff_grid[i]

        
        
        #shuffle the data and split it into train and validation sets
        X_train, X_val, y_train, y_val, w_train, w_val = train_test_split(X_trainval, y_trainval_bin, weights_trainval, test_size=0.3,  shuffle=True, random_state=1) 


        #setup the optimisation problem
        objective_fun = functools.partial(forecast_error_func, arg1=X_train, arg2=y_train, arg3=w_train, arg4=coeff, arg5=1-coeff) 


        #initial weights
        x0=np.ones(n_experts) / n_experts
    
        out= minimize(objective_fun, x0, options={'disp': False, 'maxiter':500},method='SLSQP',  constraints=cons, bounds=bnds) 
        x_opt = out.x

        #evaluate on validation data
        y_prob = np.zeros([len(X_val),2])    
        Brier_Scores[i]= brier_score_loss(y_val, X_val @ x_opt, pos_label=1)


    #get the best coefficients that minimise the brier score
    best_coeffs = coeff_grid[np.argmin(Brier_Scores)]
    


    #fit on train&val and evaluate on test data
    objective_fun = functools.partial(forecast_error_func, arg1=X_trainval, arg2=y_trainval_bin, arg3=weights_trainval,  arg4=best_coeffs, arg5=1-best_coeffs) 
    out= minimize(objective_fun, x0, options={'disp': False, 'maxiter':500},method='SLSQP',  constraints=cons, bounds=bnds) 
    x_opt = out.x


    y_test_bin=(y_test==1).astype(int) #convert to Away-based binary labels
    y_prob = np.zeros([len(X_test),2])    
    y_prob[:,0] = X_test @ x_opt
    y_prob[:,1]=1-y_prob[:,0]
    return brier_score_loss(y_test_bin, y_prob[:,0], pos_label=1)
 

def Bayesian_model_combination(X_trainval, y_trainval,  X_test, y_test, N_runs=10, ensembles_per_run=20):
    #Bayesian Model (Linear) combination. Based on paper by K. Monteith et al. 2011

    from math import log
    from numpy.random import default_rng
    rng = default_rng()
    
    y_trainval_bin=(y_trainval==1).astype(int) #convert to Away-based binary labels
    n_experts=X_trainval.shape[1] #number of experts
    n= X_trainval.shape[0] #data size

    alphas = np.ones(n_experts) # initial coefficients of Dirichlet distribution


    for i in range(N_runs):

        #sample the weights for the ensembles from a Dirichlet distribution    
        weights= rng.dirichlet(alphas, ensembles_per_run)

        
        #each ensemble is a weighted sum of the experts
        ensemble_outputs =(X_trainval@weights.T)    
        ensemble_labels = (ensemble_outputs>0.5).astype(int) #for the AWAY team

        #calculate the log-posterior distributions for each ensemble
        LogPosts= np.full(ensembles_per_run, -np.inf)
        for e in range(ensembles_per_run):
            
            r = np.sum(ensemble_labels[:,e] == y_trainval_bin)
            epsilon =(n-r)/n

            LogPosts[e] =       r*log(1-epsilon) + (n-r)*log(epsilon)  


        #take the ensemble with the maximum log-posterior
        index = np.argmax(LogPosts)
        #and use the ensemble weights to update the Dirichlect alphas
        alphas= alphas + weights[index,:]

    
    best_weights = weights[index,:]

    #Evaluate on test data
    y_test_bin=(y_test==1).astype(int) #convert to Away-based binary labels
    y_prob = X_test @ best_weights
    
    return brier_score_loss(y_test_bin, y_prob, pos_label=1)
    


