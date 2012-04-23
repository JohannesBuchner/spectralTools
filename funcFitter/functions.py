from numpy import power, exp, log, log10, sqrt, piecewise


def Linear(x,m,b):
    val = m*x+b 
    return val
    


def PowerLaw(x, norm, index, t0=0., pivot=1.):

    val = norm * power((x-t0)/pivot,index)
    return val

def BrokenPL(x, norm, indx1, breakPoint, indx2, pivot=1):

    
    cond1 = x <  breakPoint
    cond2 = x >= breakPoint

    val = piecewise(x, [cond1, cond2],\
                                    [lambda x:norm * power(x/pivot ,indx1) , \
                                             lambda x: norm * power( breakPoint / pivot ,indx1-indx2 ) * power(x/pivot, indx2)  ])
    return val


def Gaussian(x, norm, mu, sigma):

    val = norm * exp(power(x-mu,2.)/(2*sigma**2))
    return val
    
    
def Exponential(x, norm, x0=0.,a=1., b=-1.):
    
    val = norm * exp(a*power(x-x0,b))
    return val
    
    



functionLookup = {"PowerLaw": PowerLaw, "BrokenPL": BrokenPL, "Gaussian": Gaussian, "Exponential" : Exponential, "Linear": Linear}
