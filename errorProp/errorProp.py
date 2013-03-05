from inspect import getargspec
from collections import OrderedDict
from numpy import array, sqrt


#numerical derivative 
def deriv(f):

    def df(x, h=1.e-10):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df



class errorProp:
    '''
    This class propogates errors using the best fit parameters
    and covariance matrix from a fit into a defined function

    The best fit parameters should be in the form of an OrderedDict

    from collections import OrderedDict

    bestPars = OrderedDict([('<parName1>',<value> ),('<parName2>',<value> )])

    The covariance should be in a numpy array

    covar = array([[1.,2.],[2.,5.]])


    Define the function as you normally would define a python function

    def g(<parName1>,<parName2):

        return <parName1> + 3*<parName2>


    IMPORTANT: The order of the function params and the best fit params
               MUST be the same!

    The code can adapt if the function does not use all of the fit params.


    Example:


    ep = errorProp()

    ep.SetBestFitParams(bestPars)
    ep.SetCovarianceMatrix(covar)
    ep.SetFunction(g)

    result =  ep.Propogate()

    The result is a tuple (<value>,<error>)







    '''

    def __init__(self):


        pass

    def function(self):
        pass


    def SetFunction(self, f):

        self.function = f


    def SetCovarianceMatrix(self, covar):

        self.covar = covar


    def SetBestFitParams(self, params):

        #If the best fit params are entered as an OrderedDict
        #then we are cool
        if type(params) == OrderedDict :
            self.params = params
        else:
            
    
        #Otherwise we need to make one
       
 
            for p,n in zip(params,getargspec(self.function).args):
                d.append((n,p))
            self.params = d


    def Propogate(self):
        if self.function == None:
            print "ERROR: No function Set"
            return
        if self.params == None:
            print "ERROR: Best fit params not set"
            return
        if self.covar == None:
            print "ERROR: Covariance Matrix not set."

        error = self._CalculateErrors()

        evalParams = []
        args = getargspec(self.function).args
        for a in args:
            evalParams.append(self.params[a])

        value = self.function(*evalParams)

        return (value,error)



    def _CalculateErrors(self):

        shortFlag = False #Set only if the number of func args is less than params
        args = getargspec(self.function).args

        #Test a few things
        if self.covar.shape[0] != len(self.params.keys()): 
            print "Covariance Matrix and fit params dims do not match!"
            return

        if self.covar.shape[1] != len(self.params.keys()): 
            print "Covariance Matrix and fit params dims do not match!"
            return
        


        firstDerivatives = []

        if len(args) != len(self.params.keys()):
            shortFlag = True
            shortParams = []
            for a in args:
                shortParams.append((a,self.params[a]))

            shortParams = OrderedDict(shortParams)


        # loop through the params and take derivatives
        for p in self.params.keys():

            if p not in args:
                firstDerivatives.append(0.0)

            else:


                if shortFlag:
                    
                    def tmpFunction(currentParamValue):

                        tmpParams = shortParams.copy()
                        tmpParams[p]=currentParamValue
                        return self.function(*tmpParams.values())

                else:

                    def tmpFunction(currentParamValue):

                        tmpParams = self.params.copy()
                        tmpParams[p]=currentParamValue
                        return self.function(*tmpParams.values())

                firstDerivatives.append( deriv(tmpFunction)(self.params[p]) )



        firstDerivatives = array(firstDerivatives)
        
        tmp = firstDerivatives.dot(self.covar)
        error = sqrt(tmp.dot(firstDerivatives))


        return error
