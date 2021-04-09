import joblib
import os.path, sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
from sklearn.metrics import brier_score_loss
import functools

sys.path.append('Libs')

from SupportFunctions import LoadSettings
from featureUtilities import  generate_Features_fromDB


def sigm_f(x, a, b, c, d):
    return a / (1. + np.exp(-c * (x - d))) + b

def lin_f(x,a,b):
    return a*x+b

 

def score_func(params, arg1, arg2):

    p1=params[0]
    p2=params[1]
    p3=params[2]
    p4=params[3]
 
 

    TL=arg1
    x=arg2

    #convert spreads to probs
    y_conv= sigm_f(x, p1, p2, p3, p4)
    
    #supress extreme values
    max_index = y_conv>=1
    y_conv[max_index]=0.98
    min_index = y_conv<=0
    y_conv[min_index]=0.02

    y_prob = np.array([y_conv, 1-y_conv]).T
    return brier_score_loss(TL, y_prob[:,0], pos_label=2)



Params = LoadSettings("settings.txt")
Train_Features,Train_Labels,_=joblib.load("./Features/TrainingFeatures.sav")
model = joblib.load("./temp/trained_model.dat")


use_test_features=False
MIN_BIN_CENTER=-10
MAX_BIN_CENTER=10
STEP_SIZE=1


#estimate  data spreads
if use_test_features:
    Test_Features, Test_Labels = generate_Features_fromDB(Params,'./Data/Stats_data/NBA_season2019-20.db')
    y_spreads=model.predict(Test_Features)
    TL=(np.array(Test_Labels)<0).astype(int)+1 #hard labels. 1-Away, 2-Home
else:
    y_spreads=model.predict(Train_Features)
    TL=(Train_Labels<0).astype(int)+1 #hard labels. 1-Away, 2-Home


#bin centers
bin_centers=np.arange(MIN_BIN_CENTER,MAX_BIN_CENTER+STEP_SIZE,STEP_SIZE)
bin_probs = np.zeros(len(bin_centers)-1)
bin_samples =np.zeros(len(bin_centers)-1)

#populate bin probabilities
for i in range(1, len(bin_centers)):
    #find all the spreads between the two bin centers
    index = (y_spreads > bin_centers[i-1]) & ( y_spreads<= bin_centers[i])

    #and the actual wins/losses and turn them to probs. RELATIVE to home team
    bin_samples[i-1]=len(TL[index])
    if bin_centers[i]<0: #HOME team label 2
        bin_probs[i-1]=sum(TL[index]==2)/len(TL[index])
    else:                #AWAY team label 1
        bin_probs[i-1]=1-sum(TL[index]==1)/len(TL[index])



#fit model
X=np.arange(MIN_BIN_CENTER+STEP_SIZE/2,MAX_BIN_CENTER,STEP_SIZE)
cfit = opt.curve_fit(sigm_f, X, bin_probs, sigma=1/np.sqrt(bin_samples))
y_fit = sigm_f(X, cfit[0][0], cfit[0][1],  cfit[0][2],  cfit[0][3] )






#now optimise on Brier score
objective_fun = functools.partial(score_func, arg1=TL, arg2=y_spreads) 


#xopt = opt.minimize(fun=objective_fun, method='Nelder-Mead', x0 =cfit[0], options={'fatol': 1e-12, 'xatol': 1e-12, 'maxiter': 10000})

bounds = [(-100, 100), (-100, 100), (-100, 100), (-100, 100)]
xopt= opt.differential_evolution(objective_fun, bounds, tol=1e-12 )

y_fit_opt = sigm_f(X, xopt.x[0], xopt.x[1], xopt.x[2], xopt.x[3]  )

print(cfit[0], xopt.x)
print(objective_fun(cfit[0]), objective_fun(xopt.x))


#Plot stuff
plt.figure()
plt.plot(X, bin_probs, '.')  
plt.plot(X, y_fit, 'r-')
plt.plot(X, y_fit_opt, 'k-')
plt.legend(('Fitted', 'Optimized')))
plt.grid()
plt.show()