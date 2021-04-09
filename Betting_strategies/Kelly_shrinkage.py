'''
TODO: NOT FINISHED/TESTED PROPERLY
'''
from scipy.stats import beta
import scipy.integrate as integrate
from scipy.optimize import fminbound

def l_3_1(x, n, a,b, f,p, theta, k, c1,c2):

    if p> (1/theta):
        kelly=(p*theta-1)/(theta-1)
    else:
        kelly=0
    
    if p< (f*(theta-1)+1)/theta:
        loss_func= (c1+c2) * pow(abs(f-kelly),k) 
    else:
        loss_func=0


    return loss_func*beta.pdf(p,a+x,n-x+b)

def l_3_2(x, n, a,b, f,p, theta, k, c2):

    if p> (1/theta):
        kelly=(p*theta-1)/(theta-1)
    else:
        kelly=0


    if p>= (f*(theta-1)+1)/theta:
        loss_func=c2* pow(abs(f-kelly),k)
    else:
        loss_func=0
    
    return(loss_func*beta.pdf(p,a+x,n-x+b))

def G(f,x,n,theta,a,b,c1,c2,k):

    lower_lim=0
    upper_lim=(f*(theta-1)+1)/theta

    part1=integrate.quad(lambda p: l_3_1(x, n, a,b, f,p, theta, k, c1,c2),lower_lim, upper_lim)[0]
    

    lower_lim=(f*(theta-1)+1)/theta
    upper_lim=1 
 
    part2 = integrate.quad(lambda p: l_3_2(x, n, a,b, f,p, theta, k, c2),lower_lim, upper_lim)[0]
    
    return part1+part2

def  f3(x,n,theta,a,b,c1,c2,k):

    out=fminbound(lambda f: G(f,x,n,theta,a,b,c1,c2,k), 0,1, xtol=1e-02)
    return out



def Kelly_shrinkage(x,n,v,theta,c1,c2,k):
#input: 
#       x= number of correct historical wagers
#       n= total historical wagers
#       v= Beta variance
#       theta= market decimal odds
#       c1,c2,k= loss function parameters 

    #Beta distribution parameters.
    p=x/n
    a=p*(p*(1-p)/v-1)
    b=(1-p)*(p*(1-p)/v-1)


    if p>1/theta:
        Kelly_orig=(p*theta-1)/(theta-1)
        Kelly_shrink=f3(x,n,theta,a,b,c1,c2,k)
        shrink_factor=Kelly_shrink/Kelly_orig
    else:
        Kelly_orig=0
        Kelly_shrink=0
        shrink_factor=0

    return(Kelly_orig, Kelly_shrink, shrink_factor)
