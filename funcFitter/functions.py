from numpy import power, exp, log, log10, sqrt, piecewise, cosh, pi, logical_and


def Poly2 (x,c0,c1,c2):
    val = c0+x*c1+x**(2.)*c2

    return val

def Linear(x,m,b):
    val = m*(x)+b 
    return val
    


def ElectronChange(x,a,b,alpha):


    val = a*x**alpha
    val/=(x**alpha + b*x)

    return val

def ElectronChange2(x,a,b,alpha):


    val = (b/x**alpha) + a
    

    return val




def PowerLaw(x, norm, index, t0=0., pivot=1.):

    val = norm * power((x-t0)/pivot,index)
    return val

def BrokenPL(x, norm, indx1, breakPoint, indx2, t0=0., pivot=1):

    
    cond1 = x <  breakPoint
    cond2 = x >= breakPoint

    val = piecewise(x, [cond1, cond2],\
                                    [lambda x:norm * power((x-t0)/pivot ,indx1) , \
                                             lambda x: norm * power( (breakPoint-t0) / pivot ,indx1-indx2 ) * power((x-t0)/pivot, indx2)  ])
    return val


def Gaussian(x, norm, mu, sigma):

    val = norm * exp(-power(x-mu,2.)/(2*sigma**2))
    return val
    
    
def Exponential(x, norm, x0=0.,a=1., b=-1.):
    
    val = norm * exp(a*power(x-x0,b))
    return val
    
    
def RydeBPL(x, norm, indx1, indx2, breakTime ,delta, tn=1.,t0=0):

    eps=(indx2-indx1)/2
    phi=(indx2+indx1)/2
    
    val = norm*power((x-t0)/tn,phi)*power( cosh(log10((x-t0)/breakTime)/delta)/cosh(log10(tn/breakTime)/delta),eps*delta*log(10.)  )
    return val
 
def Band( x, A, Ep, alpha, beta):

	cond1 = x < (alpha-beta)*Ep/(2+alpha)
	cond2 = x >= (alpha-beta)*Ep/(2+alpha)



        band = piecewise(x, [cond1, cond2],\
				    [lambda x: A*( power(x/100., alpha) * exp(-x*(2+alpha)/Ep) ), \
					     lambda x:A* ( power( (alpha -beta)*Ep/(100.*(2+alpha)),alpha-beta)*exp(beta-alpha)*power(x/100.,beta))])

        return band  

def BlackBody(x,A,kT):

	val = A*power(x,2)*power(exp(x/float64(kT))-1,-1)

	return val
 

def EpEvo(t,A,eta,g,E0,Gamma0,n0,q):

        #c = 2.99E10 #cm/s
    c=1.
    mp = 1.67E-26   # keV ??

    z=1.
    #q=1.E-3
    #Gamma0 = 300.

    #g = (3.-eta)/2.
    #n0 = 1.E2

    #xd = ((3.-eta)*E0 / ( 4.*pi*n0*Gamma0**2. * mp  ) )**(1./3.)
    xd = 2.6E16*((1.-eta/3.)*(E0/1.E54)/((n0/100.)*(Gamma0/300.)))**(1./3.)
    #td = (1.+z)*xd / (Gamma0**2. * c)
    td = 9.7*(1.+z)*((1.-eta/3.)*(E0/1.E54)/((n0/100.)*(Gamma0/300.)**8.))**(1./3.)
        
    ### Calculate X(t)  ###
    test = (td/(2. * g + 1.) * Gamma0**(2.+1./g) + 2.*g)
    #frac = t/td

    condition1 = t<td
    condition2 = logical_and(td<=t, t<=test)

        
    X = piecewise(t, [condition1, condition2],\
    [lambda t: t/td, \
    lambda t: ((2.*g+1.)*(t/td) - 2.*g)**(1./(2.*g+1.)) ])

    ### Calculate X(t)  ###



    ### Calculate Gamma(X)  ###



    condition3 = X<1.
    condition4 = logical_and(1.<=X, X<=Gamma0**(1./g))

    Gamma = piecewise(X, [condition3, condition4],\
    [lambda X: Gamma0, \
    lambda X: Gamma0*X**(-g) ])

    ### Calculate Gamma(X)  ###

        
    eE0 = 3.E-8 * n0**(.5)*q*Gamma0**4. /(1.+z)

    return A*eE0*(Gamma/Gamma0)**4. * (X/xd)**(-eta/2.)





functionLookup = {"PowerLaw": PowerLaw, "BrokenPL": BrokenPL, "Gaussian": Gaussian, "Exponential" : Exponential, "Linear": Linear, "RydeBPL": RydeBPL, "Band" : Band, "BlackBody" : BlackBody ,"Poly2": Poly2, "EpEvo":EpEvo,"ElectronChange":ElectronChange, "ElectronChange2":ElectronChange2}

