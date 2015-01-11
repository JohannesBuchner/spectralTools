import numpy as np
from numpy import exp, power, float64, array, inf, logical_and
from pygsl.sf import synchrotron_1 
import pygsl.errors
from scipy.integrate import quad, quadrature

#### Defs for calculating energy flux

def Band( x, A, Ep, alpha, beta):

	cond1 = x < (alpha-beta)*Ep/(2+alpha)
	cond2 = x >= (alpha-beta)*Ep/(2+alpha)



        band = np.piecewise(x, [cond1, cond2],\
				    [lambda x: A*( power(x/100., alpha) * exp(-x*(2+alpha)/Ep) ), \
					     lambda x:A* ( power( (alpha -beta)*Ep/(100.*(2+alpha)),alpha-beta)*exp(beta-alpha)*power(x/100.,beta))])

        return x*band

def BlackBody(x,A,kT):

	val = A*power(x,2)*power(exp(x/float64(kT))-1,-1)

	return x*val

def PowerLaw(x, A, Epiv, index):

    return x*A*(x/Epiv)**index

def Compt(x,A,Ep,index,Epiv):

	return x*A*exp(-x*(2+index)/Ep )*power(x/Epiv,index)


#### Synchrotron with pygsl

def TotalSynchrotron(x, A, eCrit, eta, index, gammaTh):

	A=float(A)
	eCrit = float(eCrit)
	eta = float(eta)
	index = float(index)
	gammaTh = float(gammaTh)


	val,err, = quad(Integrand, 1,inf, args=(x,A,eCrit,eta,index,gammaTh),epsabs=0., epsrel= 1.e-5 )
	val= val/(x)

	return x*val


def Integrand( gamma, x ,A, eCrit, eta, index, gammaTh):

	try:
		val = EDist(A,gamma,eta,gammaTh,index) * synchrotron_1(x/(eCrit*gamma*gamma))[0]
	except pygsl.errors.gsl_Error, err:
#		print err
		val = 0.
	return val


def EDist(A,gamma,eta, gammaTh, index):


	
	epsilon = (eta/gammaTh)**(2+index)*exp(-(eta/gammaTh))
	cond1 = gamma <= eta
	cond2 = gamma > eta

	gamma=float(gamma)

	if gamma<=eta:

		val = A * (gamma/gammaTh)**2 * exp(-(gamma/gammaTh))

	else:
		val = A * epsilon * (gamma/gammaTh)**(-index)

#	val = np.piecewise(x,[cond1,cond2],\
#				   [lambda x: A * (gamma/gammaTh)**2 * exp(-(gamma/gammaTh)),\
#					    lambda x:  A * epsilon * (gamma/gammaTh)**(-index))



	return val

def PowerLaw2Breaks(x, A, pivot, index1, breakE1, index1to2, breakE2, index2):
	
	cond1 = x <= breakE1
	cond2 = logical_and(x > breakE1, x <= breakE2)
	cond3 = x > breakE2
	
	pl2b = np.piecewise(x, [cond1,cond2,cond3],\
				    [lambda x: power(x/pivot,index1),lambda x:power(breakE1/pivot,index1)*power(x/breakE1,index1to2),lambda x: power(breakE1/pivot,index1)*power(breakE2/breakE1,index1to2)*power(x/breakE2,index2)])

	return x*A*pl2b

def BrokenPL(x, A, pivot, index1, breakE, index2):
        cond1 = x <= breakE
        cond2 = x > breakE
	
        bpl = np.piecewise(x, [cond1,cond2],\
				    [lambda x: power(x/pivot,index1),lambda x: power(breakE/pivot,index1)*power(x/breakE,index2)])

        return x*A*bpl



modelLookup = {"Power Law w. 2 Breaks":PowerLaw2Breaks, "Band's GRB, Epeak": Band, "Total Test Synchrotron": TotalSynchrotron, "Black Body": BlackBody,\
		"Comptonized, Epeak": Compt, "Power Law": PowerLaw,"Black Body B": BlackBody, "Broken Power Law": BrokenPL, "BlackBody2":BlackBody }
