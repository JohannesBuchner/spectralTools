from scipy.signal import butter, lfilter, freqz
from scipy.stats import pearsonr

#from spectralTools.lightCurve_data import lightCurve_data as LCD
from spectralTools.binning.lightcurveMaker import ProcessedLightCurve

from numpy import logspace, array, log10, sqrt, r_, zeros, arange, log, log10
from numpy.random import normal

class variFilter(object):


    def __init__(self,dataFile,tstart=0.,tstop=10.,emin=8.,dt=.1,emax=300.,order=3,fType="lowpass",fmin=1E-3,fmax=1.):



        self.tstart = tstart
        self.tstop = tstop
        self.dt = dt
        self.emin = emin
        self.emax = emax

        self.order=order #Filter order
        self.fType= fType #high or low pass filter
        
        self.fmin = fmin #Freq search range
        self.fmax = fmax
    
        

        self.dataFile = dataFile

        self._CalculateLightCurve()

        


    def _CalculateLightCurve(self):


        

        plc = ProcessedLightCurve(self.dataFile)
        plc.SetTime(self.tstart,self.tstop)
        

        self._counts = plc.GetSourceSummedLC(self.emin,self.emax)

        #self._time = lc.GetTime()


    def CalcVari(self,recalc=False,ret=True):


        if recalc:
            self._CalculateLightCurve()
        
        self.fs = 1./self.dt # Sampling frequency

        if self.fs <= self.fmax:

            print "Your maximum frequency is greater than the sampling frequency"
            return
            

        #############################################
        fGrid = logspace(log10(self.fmin),log10(self.fmax),100)

        

        RLC = []
        for cutoff in fGrid:
            y = self._butter_filter(cutoff,self._counts)
            RLC.append(y)
    

        R=[]
        for i in range(len(RLC)-1):
    
            r = pearsonr(RLC[i],RLC[i+1])[0]
            R.append(r)




        
        R=array(R)

        test = r_[True, R[1:] < R[:-1]] & r_[R[:-1] < R[1:], True]    
        test[0]=False
        test[-1]=False
        
        indx = arange(len(R))[test]

        Sn = []
        for i in indx:

            sn = min( (R[i-1] - R[i]) /(log(fGrid[i]) - log(fGrid[i-1]) )   ,  (R[i+1] - R[i]) /(log(fGrid[i+1]) - log(fGrid[i]) ) )
            Sn.append(sn)
        Sn=array(Sn)/max(Sn)


        self.Sn = Sn
        self.dips = test
            
        self.RLC = array(RLC)

        self.R = array(R)
        self.fGrid = fGrid[:-1]



        

        if ret:
            return [fGrid[:-1],array(R)]


    def _butter_coeff(self,cutoff):
        nyq = 0.5 * self.fs
        normal_cutoff = cutoff / nyq
        b, a = butter(self.order, normal_cutoff, btype=self.fType, analog=False)
        return b, a

    def _butter_filter(self,cutoff,data):
        b, a = self._butter_coeff(cutoff)
        y = lfilter(b, a, data)
        return y


    def _SimLightCurve(self):

        Nsim = 1000 #number of sim lightcurves

        simLC = []

        for i in range(Nsim):
            
            simLC.append(map(self._genCount,self._counts))

        simLC = array(simLC)


        fGrid = logspace(log10(self.fmin),log10(self.fmax),100)
        fHist = zeros(len(fGrid))
        for slc in simLC:

            RLC = []
            for cutoff in fGrid:
                y = self._butter_filter(cutoff,slc)
                RLC.append(y)
    

            R=[]
            for i in range(len(RLC)-1):
    
                r = pearsonr(RLC[i],RLC[i+1])[0]
                R.append(r)

            R=array(R)
            test = r_[True, R[1:] < R[:-1]] & r_[R[:-1] < R[1:], True]
            test[0] = False
            test[-1] = False
            fHist[test]+=1.

        self.fHist=fHist/Nsim
    
        
    def _genCount(self,x):


        if x == 0.:

            return 0.


        else:

            return normal(x,sqrt(x))



    def GetSignificance(self):


        return self.fHist[self.dips]


    def GetFreq(self):


        return self.fGrid[self.dips]

    def GetR(self):

        return self.R[self.dips]

    def GetRLC(self):

        return self.RLC[self.dips]





        
     
    
