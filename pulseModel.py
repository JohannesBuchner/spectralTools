from numpy import exp


class pulseModel:



    def __init__(self):

        self.initialValues=[]
        self.fixPar = []

        #self.pulseLookup=[self.f1,self.f2,self.f3]


    def FixParams(self,fixArray):

        self.fixPar = fixArray


    def SetInitialValues(self,intialArray):

        self.initialValues = intialArray

    def GetInitialValues(self):
        
        return self.initialValues

    def GetFixedParams(self):
        
        return self.fixPar



class KRLPulse(pulseModel):

    def __init__(self):
        
        self.pulseLookup = [krl1,krl2,krl3]
    



class NorrisPulse(pulseModel):


    def __init__(self):
        self.pulseLookup = [n1,n2,n3]





# The pulse shapes have to be help at local scope because 
# mpfit adds extra arguments in at some point and doesn't
# handle the class aspect of member functions when fitting




# Definitons for the KRL pulse shape

def KRL(t,tmax,c,r,d,fmax):

        f = (fmax*(((((t+c)/(tmax+c)))**r)/(((d+(r*((((t+c)/(tmax+c)))**(1+r))))/(d+r))**((d+r)/(1+r)))))
        return f


def krl1(t,tmax,c,r,d,fmax):
        return KRL(t,c,r,d,tmax,fmax)

def krl2(t,tmax1,c1,r1,d1,fmax1,tmax2,c2,r2,d2,fmax2):
        return KRL(t,tmax1,c1,r1,d1,fmax1)+KRL(t,tmax2,c2,r2,d2,fmax2)

def krl3(t,tmax1,c1,r1,d1,fmax1,tmax2,c2,r2,d2,fmax2,tmax3,c3,r3,d3,fmax3):
        return KRL(t,tmax1,c1,r1,d1,fmax1)+KRL(t,tmax2,c2,r2,d2,fmax2)+KRL(t,tmax3,c3,r3,d3,fmax3)



# Definitons for the Norris pulse shape


def Norris(t,ts,A,tr,td):

       f = A*exp(2*(tr/ td)**(1/2) ) * exp( -tr / (t - ts) - (t - ts) / td )
       return f

def n1(t,ts,A,tr,td):
        return Norris(t,ts,A,tr,td)

def n2(t,ts1,A1,tr1,td1,ts2,A2,tr2,td2):
        return Norris(t,ts1,A1,tr1,td1)+Norris(t,ts2,A2,tr2,td2)

def n3(t,ts1,A1,tr1,td1,ts2,A2,tr2,td2,ts3,A3,tr3,td3):
        return Norris(t,ts1,A1,tr1,td1)+Norris(t,ts2,A2,tr2,td2)+Norris(t,ts3,A3,tr3,td3)
