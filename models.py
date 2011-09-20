import numpy and np
from numpy import exp

def Band( x, alpha , beta , Ep , A ):

        band = np.piecewise(x, \
[x< (alpha-beta)*Ep/(2+alpha),x>= (alpha-beta)*Ep/(2+alpha)],
[lambda x: A*( pow(x/100., alpha) * exp(-x*(2+alpha)/Ep) ), \
lambda x:A* ( pow( (alpha -beta)*Ep/(100.*(2+alpha)),alpha-beta)*exp(beta-alpha)*pow(x/100,beta))])

        return band

def BlackBody(x,A,kT):

    return A*x*x*exp(-x/kT)

def PowerLaw(x,Epiv,index):

    return A*(x/Epiv)**index
