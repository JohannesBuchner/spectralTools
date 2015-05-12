from tteBinning import tteBinning
from glob import glob
from numpy import logical_and, array, mean, histogram, arange, savez, load
from spectralTools.step import Step


import matplotlib.pyplot as plt

import astropy.io.fits as fits


class lightcurveMaker(object):

    def __init__(self,dataFile,bkgIntervals=[[-20,-.1],[50.,250.]]):
        
        self.dataFile = dataFile
        self.data = fits.open(dataFile)
        #self.binDict = dict()
        self.bkgIntervals = bkgIntervals



    

    
    def ReadData(self,binningMethod=1.,start=0.,stop=50.):
        '''
        Momentarily GBM specific 
        
        '''


        self.thisStart = start
        self.thisStop  = stop
        self.binMeth = binningMethod

        # Grab the trigger time and other bullshit
        
        self.trigTime=self.data[0].header["TRIGTIME"]
        self.tstart = self.data[0].header["TSTART"]-self.trigTime
        self.tstop = self.data[0].header["TSTOP"]-self.trigTime
        self.det = self.data[0].header["DETNAM"]
        self.grb = self.data[0].header["OBJECT"]
        self.emin = self.data[1].data["E_MIN"]
        self.emax = self.data[1].data["E_MAX"]


        # Make a energy chan selection
        chans = array(zip(self.emin,self.emax))
        meanChan = array(map(mean,chans))
        self.meanChan = meanChan
        self.chanWidth = self.emax-self.emin
        
        # Extract the TTE events
        self.evts = self.data[2].data["TIME"] - self.trigTime #Filter chans
        
        # Create a binning instance 
        tb = tteBinning(self.dataFile,self.tstart,self.tstop,self.bkgIntervals)
        self.dataBinner = tb

        self._BinDataAndSubtract()



    def _BinDataAndSubtract(self):




        if type(self.binMeth) == float:
            print
            print "Making constant time bins of dt: %.2f"%self.binMeth
            print
            self.dataBinner.MakeConstantBins(self.binMeth)

        elif type(self.binMeth) == list:
            print "NOT WORKING YET"
            self.dataBinner.MakeCustomBins()

        elif self.binMeth == "bb":

            self.dataBinner.MakeBlocks(.05)
            
        

        self.dataBinner.MakeBackgroundSelectionsForDataBinner()
        self.dataBinner._FitBackground()
        print 
        print "Backgound Fit!"
        print 
        self.bkgMods = self.dataBinner.polynomials

        #self.thisStart = start
        #self.thisStop  = stop 

        #GO BY TIME BIN


        start = self.thisStart
        stop  = self.thisStop

        start = self.tstart
        stop  = self.tstop


        tc = []
        bc = []
        sc = []
        be = []
        
        print start, stop        
        bins = self.dataBinner.bins
        j=0
        for i in range(len(bins)-1):
            
            lob=bins[i]
            hib=bins[i+1]
            
            if lob>=start and hib<=stop:
                
                bkgCounts = []
                bkgError = []
            
                totalCounts = []
            
                for ch in range(128):
                
                    tt = self.data[2].data["PHA"] == ch
                
                
                    ## get evts between times:
                    tt2 = self.evts >= lob
                    tt2 = logical_and(tt2,self.evts <hib)
                
                    tt= logical_and(tt,tt2)
                
                    #Num total counts
                
                    totalCounts.append(len(self.evts[tt]))
                    bkgCounts.append(self.bkgMods[ch].integral(lob,hib))
                    bkgError.append(self.bkgMods[ch].integralError(lob,hib))
                totalCounts =array(totalCounts)/(hib-lob)
                bkgCounts=array(bkgCounts)/(hib-lob)
                bkgError = array(bkgError)/(hib-lob)
                sourceCounts  = totalCounts  - bkgCounts

                tc.append(totalCounts)
                bc.append(bkgCounts)
                be.append(bkgError)
                sc.append(sourceCounts)


                
       # Collect the curves into matrices
        self._tc = array(tc)
        self._bc = array(bc)
        self._sc = array(sc)
        self._be = array(be)


        # Transpose the matricies into the right form
        self._tc = self._tc.T
        self._bc = self._bc.T
        self._sc = self._sc.T
        self._be = self._be.T





    def GetTotalSummedLC(self,emin,emax):


        lc = self._sumCnts(self._tc,emin,emax)

        return lc

    def GetSourceSummedLC(self,emin,emax):


        lc = self._sumCnts(self._sc,emin,emax)

        return lc

    def GetBkgSummedLC(self,emin,emax):


        lc = self._sumCnts(self._bc,emin,emax)

        return lc




    def SaveLC(self):
        '''
        Save the bkg subtracted lightcuve into
        a .npz format. The file nameing is handled
        automagically.
        '''

        outFileName = "%s_%s_dt_%.2f"%(self.grb,self.det,self.binMeth)


        savez(outFileName,total=self._tc,source=self._sc,bkg=self._bc,tbins=self.dataBinner.bins,be=self._be,emin=self.emin,emax=self.emax)
        


    def PlotData(self):

        tBins = []
        for i in range(len(self.dataBinner.bins)-1):

            tBins.append([self.dataBinner.bins[i],self.dataBinner.bins[i+1]])
        tBins=array(tBins)


        cnts,_ = histogram(self.dataBinner.evts,bins=self.dataBinner.bins)

        maxCnts = max(cnts/self.dataBinner.binWidth)
        minCnts = min(cnts/self.dataBinner.binWidth) 

        fig=plt.figure(666)
        ax=fig.add_subplot(111)

        Step(ax,tBins,cnts/self.dataBinner.binWidth,"k",.5)


        #Plot the background region

        cnts,_ = histogram(self.dataBinner.filteredEvts,bins=self.dataBinner.bins)


        Step(ax,tBins,cnts/self.dataBinner.binWidth,"b",.7)


        #Plot the selection region


        ax.vlines(self.thisStart,minCnts-50,maxCnts+50,colors='limegreen',linewidth=1.5)
        ax.vlines(self.thisStop,minCnts-50,maxCnts+50,colors='limegreen', linewidth=1.5)


        bkg = []
        oneSecBins =arange(self.dataBinner.bins[0],self.dataBinner.bins[-1],1.) 
        for i in range(len(oneSecBins)-1):

            b=0
            for j in range(len(self.bkgMods)):

                b+= self.bkgMods[j].integral(oneSecBins[i],oneSecBins[i+1])/(oneSecBins[i+1]-oneSecBins[i])
            bkg.append(b)
        meanT = map(mean,zip(oneSecBins[:-1],oneSecBins[1:]))
        ax.plot(meanT,array(bkg),linewidth=2,color="r")

        minX = min(map(lambda x: x[0],self.bkgIntervals))
        maxX = max(map(lambda x: x[1],self.bkgIntervals))


        ax.set_ylim(bottom=minCnts-50.,top=maxCnts+50.)
        ax.set_xlim(left=minX,right=maxX)



        
        

    def _sumCnts(self, curve, lo, hi):

        loChan = self._GetChannel(lo)
        hiChan = self._GetChannel(hi)


        return curve[loChan:hiChan+1].sum(axis=0)




        

    def _GetChannel(self,energy):
        '''
        Private function that finds the channel for a given energy

        ____________________________________________________________
        arguments:
        energy: selection energy in keV

        '''

        if energy < self.emin[0]:
            return 0
        elif energy > self.emax[-1]:
            return len(self.emax)-1
    

        
        ch = 0
        for lo, hi in zip(self.emin,self.emax):

            if energy >= lo and energy <= hi:
                return ch
            else:
                ch+=1





class ProcessedLightCurve(object):


    def __init__(self, lcFile):



        tmp = load(lcFile)

        self.tmin = 0.
        self.tmax = 100.
        
        
        self._tc = tmp["total"]
        self._sc = tmp["source"]
        self._bc = tmp["bkg"]
        self._be = tmp["be"]
        self._bins = tmp["tbins"]
        self.emin = tmp['emin']
        self.emax = tmp['emax']
        
        self._starts = self._bins[:-1]
        self._stops  = self._bins[1:]

        
        print
        print "Loaded %s"%lcFile
        print

        self._MakeTimeSelections()



    def SetTime(self,tmin,tmax):


        self.tmin = tmin
        self.tmax = tmax
        self._MakeTimeSelections()



    def PlotData(self, tmin=0., tmax=100., emin=8., emax=300., total=True, src=False, bkg=False):


        tBins = array(zip(self._starts,self._stops))
        #binWidth = self._stops - self._starts

        fig=plt.figure(666)
        ax=fig.add_subplot(111)

        self.SetTime(tmin,tmax)

        if total:

            Step(ax,tBins[self.tiStart:self.tiStop+1],self.GetTotalSummedLC(emin,emax),"k",.5)

        if bkg:

            Step(ax,tBins[self.tiStart:self.tiStop+1],self.GetBkgSummedLC(emin,emax),"r",.5)

        if  src:

            Step(ax,tBins[self.tiStart:self.tiStop+1],self.GetSourceSummedLC(emin,emax),"b",.5)









        
    def _MakeTimeSelections(self):


        self.tiStart = self._GetTimeIndex(self.tmin)
        self.tiStop  = self._GetTimeIndex(self.tmax)
        self._PrintTime()

    def _GetTimeIndex(self,time):


        if time < self._starts[0]:
            return 0
        elif time > self._stops[-1]:
            return len(self._stops)-1
    

        
        ch = 0
        for lo, hi in zip(self._starts,self._stops):

            if time >= lo and time <= hi:
                return ch
            else:
                ch+=1
               

        
        


    def _PrintTime(self):

        print
        print "Current Time Selections: "
        print "\tTmin: %.2f"%self.tmin
        print "\tTmax: %.2f"%self.tmax
        print

        

    def GetTotalSummedLC(self,emin,emax):


        lc = self._sumCnts(self._tc,emin,emax)

        return lc[self.tiStart:self.tiStop+1]

    def GetSourceSummedLC(self,emin,emax):


        lc = self._sumCnts(self._sc,emin,emax)

        return lc[self.tiStart:self.tiStop+1]

    def GetBkgSummedLC(self,emin,emax):


        lc = self._sumCnts(self._bc,emin,emax)

        return lc[self.tiStart:self.tiStop+1]


    def _sumCnts(self, curve, lo, hi):

            loChan = self._GetChannel(lo)
            hiChan = self._GetChannel(hi)


            return curve[loChan:hiChan+1].sum(axis=0)




        

    def _GetChannel(self,energy):
        '''
        Private function that finds the channel for a given energy

        ____________________________________________________________
        arguments:
        energy: selection energy in keV

        '''

        if energy < self.emin[0]:
            return 0
        elif energy > self.emax[-1]:
            return len(self.emax)-1
    

        
        ch = 0
        for lo, hi in zip(self.emin,self.emax):

            if energy >= lo and energy <= hi:
                return ch
            else:
                ch+=1


