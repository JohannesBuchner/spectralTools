from numpy import exp


class pulseModel:



    def __init__(self):

        self.initialValues=[]
        self.fixPar = []

        self.pulseLookup=[self.f1,self.f2,self.f3]


    def FixParams(self,fixArray):

        self.fixPar = fixArray


    def SetInitialValues(self,intialArray):

        self.initialValues = intialArray

  

    








class KRLPulse(pulseModel):


   
    def KRLPulse(self,t,c,r,d,tmax,fmax):

        f = (fmax*(((((t+c)/(tmax+c)))**r)/(((d+(r*((((t+c)/(tmax+c)))**(1+r))))/(d+r))**((d+r)/(1+r)))))
        return f

    def f1(self,t,c,r,d,tmax,fmax):
        return self.KRLPulse(t,c,r,d,tmax,fmax)

    def f2(self,t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2):
        return self.KRLPulse(t,c1,r1,d1,tmax1,fmax1)+self.KRLPulse(t,c2,r2,d2,tmax2,fmax2)

    def f3(self,t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2,c3,r3,d3,tmax3,fmax3):
        return self.KRLPulse(t,c1,r1,d1,tmax1,fmax1)+self.KRLPulse(t,c2,r2,d2,tmax2,fmax2)+self.KRLPulse(t,c3,r3,d3,tmax3,fmax3)



class NorrisPulse(pulseModel):

    def NorrisPulse(self,t,A,tr,td,ts):

       f = A*exp(2*(tr/ td)**(1/2) ) * exp( -tr / (t - ts) - (t - ts) / td )
       return f

    def f1(self,t,A,tr,td,ts):
        return self.NorrisPulse(t,A,tr,td,ts)

    def f2(self,t,A1,tr1,td1,ts1,A2,tr2,td2,ts2):
        return self.NorrisPulse(t,A1,tr1,td1,ts1)+self.NorrisPulse(t,A2,tr2,td2,ts2)

    def f3(self,t,A1,tr1,td1,ts1,A2,tr2,td2,ts2,A3,tr3,td3,ts3):
        return self.NorrisPulse(t,A1,tr1,td1,ts1)+self.NorrisPulse(t,A2,tr2,td2,ts2)+self.NorrisPulse(t,A3,tr3,td3,ts3)
