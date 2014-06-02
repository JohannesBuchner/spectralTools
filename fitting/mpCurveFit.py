from mpfit import mpfit
from numpy import asarray
import inspect

#def _general_function(params, fjac=None, xdata=None, ydata=None, function=None):
    
    #print function(xdata, *params) - ydata
#    return 0, function(xdata, *params) - ydata

#def _weighted_general_function(params,fjac=None, xdata=None, ydata=None, function=None, weights=None):
#    return 0, weights * (function(xdata, *params) - ydata)
from pylab import *

class mpCurveFit:

  
    def __init__(self,f, xdata, ydata, p0=None, sigma=None, fixed=None,limits=None, maxiter=200,quiet=1):
        args, varargs, varkw, defaults = inspect.getargspec(f)
       
        self.quiet = quiet
        if len(args) < 2:
            msg = "Unable to determine number of fit parameters."
            raise ValueError(msg)
       
        def general_function(params, fjac=None, xdata=None, ydata=None):
            return [0, f(xdata, *params) - ydata]

        def weighted_general_function(params,fjac=None, xdata=None, ydata=None, weights=None):
            return [0, weights * (f(xdata, *params) - ydata)]


        parinfo = [{'value':1., 'fixed':0, 'limited':[0,0], 'limits':[0.,0.]}  for i in range(len(args)-1)] 
        

        if p0 != None:
            for x,y in zip(parinfo,p0):
                x['value']=y
        if fixed != None:
            for x,y in zip(parinfo,fixed):
                x['fixed']=y


        if limits != None:
            for x,y in zip(parinfo,limits):
                x['limited']=y[0]
                x['limits']=y[1]
            



    #args = (xdata, ydata, f)
        if sigma is None:
            func = general_function
           # print 'here'
          #  my_functkw = {'xdata':xdata,'ydata':ydata,'function':f}
            my_functkw = {'xdata':xdata,'ydata':ydata}
        else:
            func = weighted_general_function
            weights= 1.0/asarray(sigma)
           # my_functkw = {'xdata':xdata,'ydata':ydata,'function':f,'weights':weights}
            my_functkw = {'xdata':xdata,'ydata':ydata,'weights':weights}


        
       
        result = mpfit(func, functkw=my_functkw, parinfo = parinfo,quiet=self.quiet,maxiter=maxiter)
      
        self.params = result.params
        self.errors = result.perror
        self.dof = result.dof
        self.chi2 = result.fnorm
        self.covar = result.covar
 
    
