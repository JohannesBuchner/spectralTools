from mpfit import mpfit
from numpy import asarray, array
import inspect
from scipy.integrate import quad
from numpy import logical_and

#def _general_function(params, fjac=None, xdata=None, ydata=None, function=None):
    
    #print function(xdata, *params) - ydata
#    return 0, function(xdata, *params) - ydata

#def _weighted_general_function(params,fjac=None, xdata=None, ydata=None, function=None, weights=None):
#    return 0, weights * (function(xdata, *params) - ydata)
from pylab import *

class mpPulseFitEngine:

  
    def __init__(self,f, xdata, ydata, p0=None, sigma=None, fixed=None,limits=None, maxiter=200,quiet=1,tBins=None):
        args, varargs, varkw, defaults = inspect.getargspec(f)
        if len(args) < 2:
            msg = "Unable to determine number of fit parameters."
            raise ValueError(msg)

        #We have to integrate the function
        masks = []
        for t in xdata:
            lowMask = tBins[:,0] <= t
            hiMask  = tBins[:,1] >= t
            mask = logical_and(lowMask,hiMask)
            masks.append(mask)



        usedTbins = []
        for m in masks:
            usedTbins.append( tBins[m][0] )


        def intPulse(thesetBins, *args):
            print args
            val=[]
            for tBin in thesetBins:
                
                val.append( quad(f, tBin[0],tBin[1], args=args, epsabs=0., epsrel= 1.e-5)[0])
            return array(val)
            
        


       
        def general_function(params, fjac=None, xdata=None, ydata=None):
            return [0, intPulse(usedTbins, *params) - ydata]

        def weighted_general_function(params,fjac=None, xdata=None, ydata=None, weights=None):
            return [0, weights * (intPulse(usedTbins, *params) - ydata)]


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


        
       
        result = mpfit(func, functkw=my_functkw, parinfo = parinfo,quiet=quiet,maxiter=maxiter)
      
        self.params = result.params
        self.errors = result.perror




