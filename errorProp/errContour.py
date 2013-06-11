from numpy import array, sqrt, zeros, vstack, linspace, log10
import inspect


#numerical derivative 
def deriv(f):

    def df(x, h=0.1e-7):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df



class errContour:
    '''
    Class to plot the errorContour from a fit to data.
    '''

    def __init__(self, fit):

        
        #if results == None:
        #    print "No results structure was specified"
        #    print "Results will have to be entered manually"
        #    
        #else:
        #    self.results = results
        
        self.result = fit.result
        self.covar = fit.covar
        self.fitFunc = fit.fitFunc
        self.xMin = fit.xData.min()
        self.xMax = fit.xData.max()
        try:
            self.dataLog = fit.dataLog
        except AttributeError:
            self.dataLog = 'False'
            
        args, varargs, varkw, defaults = inspect.getargspec(self.fitFunc)
        self.parNames = args[1:]
        self.pivot = fit.pivot

        self._GrabResults()
        self._CreateContours()
            

 #   def SetFitFunc(self, func):
 #       '''
 #       Define the function used for fitting
#
 #       '''

 #       self.fitFunc = func
        


    def _GrabResults(self):
        '''
        Get the restults from the fit

        '''

        self.params = self.result[:-1,0]
        self.errors = self.result[:-1,1]
        
        
    



    def _CalcContour(self,x):
        'Calculate the upper and lower contour '
        

        par = dict(zip(self.parNames, self.params))
        

        
        #Initialize the first derivative list
        firstDerivates = []


        for parName in self.parNames:

            def tmpFunc(currentPar):


                # Get the parameter values
                    tmpParams = par.copy()
                    
                    # Set the current parameter (the one that the derivative is being taken w.r.t.)
                    # To it's measured value
                    tmpParams[parName]=currentPar
                    
                    # Calculate vFv at this value
                    val = self._CalcModel(tmpParams, x)
                    

                    return val



            firstDerivates.append( deriv(tmpFunc)(par[parName]))


        firstDerivates = array(firstDerivates)


        tmp = firstDerivates.dot(self.covar)

        contours = sqrt(tmp.dot(firstDerivates))

        return contours

    def _CalcModel(self, params, x):

        mod = self.fitFunc(x, *params.values())
        return mod


    def _CreateContours(self):


        xspan = linspace(self.xMin, self.xMax, 500)

        contour=[]
        
        for x in xspan:
            contour.append(self._CalcContour(x))


        self.contour = contour


    def PlotContours(self, ax, specLineStyle='-', specColor='b', specLineWidth=1, conLineStyle='-', conColor='b', conLineWidth=.5, filled=False,fillAlpha=.5):
        '''
        This is the main command. The options are for controlling the plotting style.
        Must provide an axis to plot to!!!!!
        
        
        '''
        
        
        xspan = linspace(self.xMin, self.xMax, 500)
        if self.pivot != None:
            if (self.dataLog == 'x') or (self.dataLog == 'all'):
                func = self.fitFunc(xspan-log10(self.pivot),*self.params)
            else:
                self.fitFunc(xspan-(self.pivot),*self.params)
        else:
            func = self.fitFunc(xspan,*self.params)
        
        self.contour = array(self.contour)
        func  = array(func)
        upper = func + self.contour
        lower = func - self.contour

                        
        if self.dataLog == 'all':
            upper = 10**(upper)
            lower = 10**(lower)
            xspan = 10**(xspan)
            func = 10**(func)


        if self.dataLog == 'y':
            
            upper = 10**(upper)
            lower = 10**(lower)
            func = 10**(func)


        
        
        ax.loglog(xspan,func, ls=specLineStyle, color=specColor, lw=specLineWidth)
            
        if filled:
            ax.fill_between(xspan,lower,upper,alpha=fillAlpha,interpolate=True, color=conColor, lw=conLineWidth, linestyle=conLineStyle )
            ax.set_yscale('log', nonposy='clip')
        else:
            ax.loglog(xspan,upper, ls=conLineStyle, color=conColor, lw=conLineWidth)

            ax.loglog(xspan,lower, ls=conLineStyle, color=conColor, lw=conLineWidth)


        #ax.set_xlabel(xlabel)
        #ax.set_ylabel(ylabel)

        return ax 
        
