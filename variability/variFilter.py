from scipy.signal import butter, lfilter, freqz
from scipy.stats import pearsonr

from spectralTools.lightCurve_data import lightCurve_data as LCD


from numpy import logspace, array, log10


class variFilter(object):


    def __init__(self,dataFile,tstart=0.,tstop=10.,dt=.1,emin=8.,emax=300.,order=3,fType="lowpass",fmin=1E-3,fmax=1.):



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


        

        lc = LCD(self.dataFile,self.dt,self.tstart,self.tstop,self.emin,self.emax)


        self._counts = lc.GetCounts()

        self._time = lc.GetTime()


    def CalcVari(self,recalc=False):


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
            y = self._butter_filter(cutoff)
            RLC.append(y)
    

        R=[]
        for i in range(len(RLC)-1):
    
            r = pearsonr(RLC[i],RLC[i+1])[0]
            R.append(r)



        self.RLC = RLC

        return [fGrid[:-1],R]


    def _butter_coeff(self,cutoff):
        nyq = 0.5 * self.fs
        normal_cutoff = cutoff / nyq
        b, a = butter(self.order, normal_cutoff, btype=self.fType, analog=False)
        return b, a

    def _butter_filter(self,cutoff):
        b, a = self._butter_coeff(cutoff)
        y = lfilter(b, a, self._counts)
        return y




    
