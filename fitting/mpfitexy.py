from numpy import array, sqrt, power
from mpfit import mpfit

def lineresid (p, fjac=None,x=None, y=None, e_x=None, e_y=None  ):
    '''
    PURPOSE
    Utility function called by mpfitexy. Given a set of data, returns the
    residuals weighted by both error bars and optional intrinsic scatter
    when fitted with a straight line

    '''
    slope = p[0]
    intercept = p[1]
    #pivot = p[3]
    f = slope * x + intercept
      
    resid = (y - f)/sqrt(power(e_y,2) + power(slope,2)*power(e_x,2 ))

    status = 0
    return [status, resid]



def mpfitexy( x, y, e_x, e_y , guess = [1,1] , \
    fixslope = False, fixint = False, \
    reduce = False,  quiet = 1, limits=None,silent = False):


    parinfo = [{'value':0., 'fixed':0, 'parname': '','limited':[0,0], 'limits':[0.,0.]} for i in range(2)]

    if fixslope: parinfo[0]['fixed']=1
    if fixint: parinfo[1]['fixed']=1

    if limits != None:
            for x,y in zip(parinfo,limits):
                x['limited']=y[0]
                x['limits']=y[1]

    
    parinfo[0]['parname'] = 'Slope'
    parinfo[1]['parname'] = 'Intercept'

    for gs,pr in zip(guess,parinfo):
        pr['value']=gs
    
    result = mpfit(lineresid, parinfo=parinfo, functkw = {'x':x, 'y':y, 'e_x':e_x, 'e_y':e_y},quiet=quiet)
    return [result.params,result.perror,result.fnorm,result.dof,result.covar]
        
