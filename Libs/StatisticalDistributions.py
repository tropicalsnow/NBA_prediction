import numpy as np
from scipy.optimize import minimize, minimize_scalar, newton, Bounds
from scipy.stats import gumbel_l, multivariate_normal, poisson, norm
import functools

 
import warnings

warnings.filterwarnings('ignore')




class Weibull3Distribution:

    def __init__(self, theta=[0,1,1]):


        self.NumParameters = 3
        self.ParameterNames =	 {"location": "mu",  "scale": "sigma",  "shape": "kappa"}

        self.ParameterValues=theta


    def likefunc(self, params, arg1):
        #Analytic form of the negative log likelihood function
      
        
        mu = params[0]
        sigma = params[1]
        kappa = params[2]
  
      

        x=arg1

        if isinstance(x, list):
            x=np.array(x)
 
        n = len(x)      
        xCent=x-mu
        xNorm = xCent/sigma
         
 
        
        sum1= np.sum(np.log(xCent))
        sum2= np.sum(  np.power( xNorm,kappa))

        nll =  -(n*(np.log(kappa)-kappa*np.log(sigma))+(kappa-1)*sum1-sum2)
  
      
        return nll

    def likefunc_gradient(self,params,arg1):

        mu = params[0]
        sigma = params[1]
        kappa = params[2]

        x=arg1


        n=len(x)

        xCent=x-mu
        xNorm = xCent/sigma
        #the gradient vectors of the nll
        dmu = -(kappa-1)*np.sum(1./xCent)+(kappa/sigma)*np.sum( np.power(xNorm,kappa-1)  )
        dsigma=  kappa/sigma* (-n + np.sum( np.power(xNorm,kappa) ))
        dkappa =  n/kappa - n*np.log(sigma) + np.sum(np.log(xCent)) - np.sum( np.power(xNorm, kappa) * np.log(xNorm) )

        return  -np.array([dmu,dsigma,dkappa])
         

    def likefunc_hessian(self,params,arg1):

        mu = params[0]
        sigma = params[1]
        kappa = params[2]

        x=arg1


        n=len(x)

        xCent=x-mu
        xNorm = xCent/sigma

        #the hessian matrix
        dmu2= -(kappa-1)*(    np.sum(np.power(1/xCent,2)) + kappa/(sigma*sigma) * np.sum(np.power(xNorm,kappa-2)))
            
        dmudsigma= -np.power(kappa/sigma,2) * np.sum( np.power(xNorm,kappa-1))
            
        dmudkappa = -np.sum(1./xCent) + kappa/sigma* np.sum(np.power(xNorm,kappa-1)* np.log(xNorm)) + 1/sigma*np.sum( np.power(xNorm,kappa-1) )
            
        dsigma2=  kappa/(sigma*sigma) * (n- (kappa-1)*np.sum(np.power(xNorm,kappa))  )
            
        dsigmadkappa = -1/sigma * (n- np.sum( np.power(xNorm, kappa) ) - kappa*np.sum(( np.power(xNorm,kappa))* np.log(xNorm)))
            
        dkappa2=  -n/(kappa*kappa) - np.sum(np.power(xNorm,kappa)  * np.power(np.log(xNorm),2) )
            
        return -np.array([ [dmu2, dmudsigma, dmudkappa], [dmudsigma, dsigma2, dsigmadkappa], [dmudkappa, dsigmadkappa, dkappa2]  ])



    def f_kappa(self, kappa,arg1,arg2):

        x=arg1
        n=arg2

        z=np.log(x)
        z_mn = 1/n* np.sum(z)
        w=z-z_mn

    
        #hack to take care of underflow overflow/errors in float64
        kw=kappa*w
        kw = np.delete(kw, np.where(kw < -700))
        kw = np.delete(kw, np.where(kw > 700))


        func = np.sum(  (1-kw) *   np.exp(kw) )

        return func
            
    
    def f_kappa_prime(self, kappa,arg1,arg2):

        x=arg1
        n=arg2

        z=np.log(x)
        z_mn = 1/n* np.sum(z)
        w=z-z_mn

  
        #hack to take care of underflow overflow/errors in float64
        kw=kappa*w
        index_min=np.where(kw < -700)
        w = np.delete(w, index_min)
        kw = np.delete(kw, index_min)
        index_max=np.where(kw > 700)
        w = np.delete(w, index_max)
        kw = np.delete(kw, index_max)


        

        grad= -np.sum(kappa* np.power(w,2) * np.exp(kw))

        return grad


    
    def profileLogLikelihood(self,mu,arg1,arg2,arg3=''):

        epsilon = 1e-10

        x=arg1
        n=arg2
        return_type=arg3

        y= x-mu

        #the function from which to obtain the optimal kappa
        f_k = functools.partial(self.f_kappa, arg1=y, arg2=n) 
        f_k_prime = functools.partial(self.f_kappa_prime, arg1=y, arg2=n) 

        #starting point
        if mu==0:
            k0= 1/(n* np.log(np.max(x)) - np.sum(np.log(x)) ) + epsilon
        else:
            k0 = np.mean(x)

        #find optimal kappa using Newton's method
        kappa = newton(f_k, k0, fprime=f_k_prime, maxiter=5000, tol=1e-6 )

        #obtain optimal sigma
        sigma = np.power(1/n * np.sum( np.power(y,kappa) )       ,1/kappa)


        pll= self.likefunc([mu, sigma, kappa],x)  #NEGATIVE log likelihood

        if return_type == 'func_only':
            return pll
        else:
            return pll, kappa, sigma



    def fit_nofail(self,x):
        """ Implementing the non-failing algorithm by Horst Rinne "The Weibull distribution A handbook 2009"  """
        
        epsilon = 1e-10
        n=len(x)


        f = functools.partial(self.profileLogLikelihood, arg1=x, arg2=n, arg3='func_only')   


        opt_mu=minimize_scalar(f, bounds=(0, np.min(x)-epsilon), method='bounded').x

        
        mLL, opt_kappa, opt_sigma=f(opt_mu, arg3='')

        #compare with corner point
        c_mu = np.min(x)-epsilon
        c_sigma =  1/n* np.sum(x-c_mu)
        c_kappa=1

        cLL = self.likefunc([c_mu,c_sigma,c_kappa], x)

        if cLL < mLL:
            #return the corner point
            self.ParameterValues[0] = c_mu
            self.ParameterValues[1] = c_sigma
            self.ParameterValues[2] = c_kappa

        else:
            #return the optimal solution found
            self.ParameterValues[0] =  opt_mu
            self.ParameterValues[1] =  opt_sigma
            self.ParameterValues[2] =  opt_kappa
                


    def fit(self,x):


        epsilon=1e-06
        #initial guess of parameters using the 2-param Weibull and zeroed data
        m0= np.min(x)-epsilon
        nx=x-m0
        nx = nx[np.where(nx>0)]

        #Initial estimate from 2-param weibull fit        
        parmhatEV= gumbel_l.fit(np.log(nx))
 

        k0=1./parmhatEV[1]
        s0 =   np.power(np.mean( np.power(nx, k0)  )       ,1/k0)
 
 
        #set-up numerical optimisation of the NLL

        objective_fun = functools.partial(self.likefunc, arg1=x) 
        jacobian_fun =  functools.partial(self.likefunc_gradient, arg1=x) 
        hessian_fun =  functools.partial(self.likefunc_hessian, arg1=x) 

        bnds = Bounds([-np.inf, epsilon,epsilon], [np.min(x)-epsilon, np.inf,np.inf], keep_feasible=True )
        
  
        #out= minimize(objective_fun, [m0,s0,k0], method='trust-ncg', jac=jacobian_fun, hess=hessian_fun,  options={'disp': False, 'maxiter':1000}) #fails on problematic models
        out= minimize(objective_fun, [m0,s0,k0], method='trust-constr', bounds=bnds, jac=jacobian_fun, hess=hessian_fun,  options={'disp': False, 'maxiter':200}) 
        #out= minimize(objective_fun, [m0,s0,k0], method='L-BFGS-B', bounds=bnds, jac=jacobian_fun,   options={'disp': False})    # does not fail but blows up parameters
        #out = minimize(objective_fun, [m0,s0,k0],  method='TNC', bounds=bnds, jac=jacobian_fun,  tol=1e-10 , options={'disp': False, 'maxiter':1000})
    
        


        self.ParameterValues = out.x






def negLogPosterior(theta, arg1,arg2,arg3,arg4):


    X=arg1
    M=arg2
    C=arg3
    model_type=arg4
    
    #The parameter prior
    prior = multivariate_normal.pdf(theta,mean=M,cov=C)
    

    #The data (neg) log-likelihood
    if model_type=='Weibull3':

        pd=Weibull3Distribution()
        sm=-pd.likefunc(theta, X)
 
    elif model_type=='Poisson':
        sm= np.sum(-poisson.logpmf(X,mu=theta[1],loc=theta[0]))


    elif model_type=='Gaussian':
        sm= np.sum(norm.logpdf(X, loc=theta[0], scale=theta[1]))
    else:
        return 0


    #the log posterior
    p= - (np.log(prior) + sm)
 
    return p