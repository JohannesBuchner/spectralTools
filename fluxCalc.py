from spectralTools.models import modelLookup
from spectralTools.temporal.eFluxModels import modelLookup as eFluxLookup
from scipy.integrate import quad, quadrature
from numpy import array, sqrt, zeros, vstack


keV2erg =1.60217646e-9

def CalculateFlux(modelName,params,eMin=10.,eMax=40000.):

    model = modelLookup[modelName]

    if (modelName == 'Band\'s GRB, Epeak') or (modelName =='Power Law w. 2 Breaks'):



        val,err, = quadrature(model, eMin, eMax, args=params, tol=1.49e-10, rtol=1.49e-10, maxiter=200)
        return val


    val,err, = quad(model, eMin,eMax,args=params,epsabs=0., epsrel= 1.e-5 )

    return val


def CalculateEnergyFlux(modelName,params,eMin=10.,eMax=40000.):

    model = eFluxLookup[modelName]

    if (modelName == 'Band\'s GRB, Epeak') or (modelName =='Power Law w. 2 Breaks'):

        val,err, = quadrature(model, eMin,eMax,args=params,tol=1.49e-10, rtol=1.49e-10, maxiter=200)
        val = val*keV2erg
        return val


    val,err, = quad(model, eMin, eMax, args=params, epsabs=0., epsrel= 1.e-5 )


    val = val*keV2erg


    return val
