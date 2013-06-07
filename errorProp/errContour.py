

#numerical derivative 
def deriv(f):

    def df(x, h=0.1e-7):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df



class errContuor:
'''
Class to plot the errorContour from a fit to data.


'''
    def __init__(self, results = None):
        
        if results == None:
            print "No results structure was specified"
            print "Results will have to be entered manually"


    

    def _CalcContour(self):
        'Calculate the upper and lower contour '
        
        
