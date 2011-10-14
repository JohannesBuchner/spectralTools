import numpy as np
from numpy import exp, power, float64, array

def Band( x, A, Ep, alpha, beta):


	cond1 = x < (alpha-beta)*Ep/(2+alpha)
	cond2 = x >= (alpha-beta)*Ep/(2+alpha)



        band = np.piecewise(x, [cond1, cond2],\
				    [lambda x: A*( power(x/100., alpha) * exp(-x*(2+alpha)/Ep) ), \
					     lambda x:A* ( power( (alpha -beta)*Ep/(100.*(2+alpha)),alpha-beta)*exp(beta-alpha)*power(x/100,beta))])

        return band

def BlackBody(x,A,kT):

	
#	print A
#	print kT
#	print x
	val = A*power(x,2)*power(exp(x/float64(kT))-1,-1)
#	print val
	#print val
	return val

def PowerLaw(x, A, Epiv, index):

    return A*(x/Epiv)**index

def Compt(x,A,Ep,index,Epiv):

	return A*exp(-x*(2+index)/Ep )*power(x/Epiv,index)
