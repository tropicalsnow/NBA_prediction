import numpy as np
from sklearn.metrics import brier_score_loss

def GlobalBrier_optimiser_method(X, y, X_test=None, weights=None,  curr_year=2020):
 
    from scipy.optimize import minimize,  Bounds
    import functools
    from sklearn.model_selection import KFold, train_test_split


    if weights is None:
        W=np.ones(len(y))  #flat
    else:
        W = np.exp((curr_year-weights))   #exponential
        #W = (curr_year-weights)**2 #squared
        #W= 2**(curr_year-weights) # power
        #W= np.log(1+ curr_year-weights) #logarihmic
        



    #the residual cost function to minimise
    def forecast_error_func(x, arg1, arg2, arg3, arg4, arg5):
        

        Data= arg1
        Outcome =arg2
        W = arg3


        P_est =  Data @ x  #weighted Arithmetic mean
        #P_est =  np.power(np.prod(np.power(Data , x),axis=1), 1/sum(x))   #weighted Geometric mean

        r = P_est - Outcome 

        l1=arg4 #regularisation coefficient
        l2=arg5 #regularisation coefficient


        reg1 = l1*np.sum(x*x) #L2 norm
        reg2 = l2*np.sum(abs(x)) #L1 norm

        #Elastic NET
        return np.sum(  (r*r)  *   W   )/len(Outcome)  +reg1 + reg2


    def constraint1(x):
        return np.sum(x)-1


  

    n_experts=X.shape[1]
    y_bin=(y==1).astype(int) #convert to Away-based binary labels
    
    #constraints and bounds for the optimisation
    cons = {'type': 'eq', 'fun': constraint1} 
    bnds = Bounds(0,1)

    

    #Set up the grid search
    Ntests=100
    coeff_grid=np.linspace(0,1,Ntests)
    Brier_Scores=np.ones(Ntests)

    for i in range(Ntests):

        coeff=coeff_grid[i]
 
        
        #shuffle the data and split it into train and validation sets
        X_train, X_val, y_train, y_val, w_train, _ = train_test_split(X, y_bin, W, test_size=0.3,  shuffle=True) 


        #setup the optimisation problem
        objective_fun = functools.partial(forecast_error_func, arg1=X_train, arg2=y_train, arg3=w_train, arg4=coeff, arg5=1-coeff) 


        #initial weights
        x0=np.ones(n_experts) / n_experts
    
        out= minimize(objective_fun, x0, options={'disp': False, 'maxiter':500},method='SLSQP',  constraints=cons, bounds=bnds) 
        x_opt = out.x

        #evaluate on validation data   
        Brier_Scores[i]= brier_score_loss(y_val, X_val @ x_opt, pos_label=1)


    #get the best coefficients that minimise the brier score
    best_coeffs = coeff_grid[np.argmin(Brier_Scores)]
    


    #fit on the whole data
    objective_fun = functools.partial(forecast_error_func, arg1=X, arg2=y_bin, arg3=W ,arg4=best_coeffs, arg5=1-best_coeffs) 
    out= minimize(objective_fun, x0, options={'disp': False, 'maxiter':500},method='SLSQP',  constraints=cons, bounds=bnds) 
    x_opt = out.x


    if X_test is None:
        #just return the optimum weights and the best coefficients found during the training of the method
        return None,  best_coeffs, x_opt
    else:
        #apply on prediction data and return  
        return X_test @ x_opt,  best_coeffs, x_opt




def Stacker_method(X, y, X_test):
    
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import KFold, GridSearchCV

    
    #setup the classifier and perform cross validation
    model = LogisticRegression( penalty='elasticnet', solver='saga', warm_start=True, max_iter=10000); param_grid= { 'l1_ratio' : [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], 'fit_intercept':[True, False], 'C':[0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5,2]}


    #setup grid search on the data.
    kfold = KFold(n_splits=5, shuffle=True)
    grid_search = GridSearchCV(model, param_grid, cv=kfold,  scoring='neg_brier_score', n_jobs=-1) 
    grid_search.fit(X, y) 

    
    #Now retrain on the whole data using the best model found 
    model = grid_search.best_estimator_
    model.fit(X,y)
    return model.predict_proba(X_test)


 