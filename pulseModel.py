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

def KRL(t,c,r,d,tmax,fmax):

        f = (fmax*(((((t+c)/(tmax+c)))**r)/(((d+(r*((((t+c)/(tmax+c)))**(1+r))))/(d+r))**((d+r)/(1+r)))))
        return f


def krl1(t,c,r,d,tmax,fmax):
        return KRL(t,c,r,d,tmax,fmax)

def krl2(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2):
        return KRL(t,c1,r1,d1,tmax1,fmax1)+KRL(t,c2,r2,d2,tmax2,fmax2)

def krl3(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2,c3,r3,d3,tmax3,fmax3):
        return KRL(t,c1,r1,d1,tmax1,fmax1)+KRL(t,c2,r2,d2,tmax2,fmax2)+KRL(t,c3,r3,d3,tmax3,fmax3)



# Definitons for the Norris pulse shape


def Norris(t,A,tr,td,ts):

       f = A*exp(2*(tr/ td)**(1/2) ) * exp( -tr / (t - ts) - (t - ts) / td )
       return f

def n1(t,A,tr,td,ts):
        return Norris(t,A,tr,td,ts)

def n2(t,A1,tr1,td1,ts1,A2,tr2,td2,ts2):
        return Norris(t,A1,tr1,td1,ts1)+Norris(t,A2,tr2,td2,ts2)

def n3(t,A1,tr1,td1,ts1,A2,tr2,td2,ts2,A3,tr3,td3,ts3):
        return Norris(t,A1,tr1,td1,ts1)+Norris(t,A2,tr2,td2,ts2)+Norris(t,A3,tr3,td3,ts3)
