from astroML.density_estimation import histtools, bayesian_blocks
from astroML.plotting import hist 
import astropy.io.fits as fits
from numpy import linspace, arange, array, logical_and, mean, sum, sqrt, logical_or, diff, sqrt
import os,errno
import warnings
import scipy.optimize
from LogLikelihood import *
from BayesianBlocks_python import BayesianBlocks

class tteBinning(object):


    def __init__(self, tteFile, tStart, tStop, bkgIntervals = None):



        
        self.binWidth =1.
        

        fileDir = tteFile.split('/')
        self.tteFile = fileDir[-1]
        tmp = ""
        for x in fileDir[:-1]:
            tmp+=x+"/"

        self.fileDir = tmp


        fitsFile = fits.open(tteFile)
        self.chanLU = fitsFile[1].data

        evts = fitsFile[2].data['TIME']

        header = fitsFile[0].header
        trigTime = header['TRIGTIME']
        start = header['TSTART'] - trigTime
        end = header['TSTOP'] - trigTime
        
        self.verbose = False

        self.fileStart = start
        self.fileEnd = end
        self.tStop = tStop
        self.tStart = tStart

       
        self.evtExt = fitsFile[2].data

        evts = evts - trigTime

        self.trigTime = trigTime

        self.allEvts = evts
       
        self.evts = evts[evts < tStop]
        
       
        self.evts = self.evts[self.evts > tStart]

        self.needAll=False
        self.HRbins = False
        if bkgIntervals != None:

            self.bkgIntervals = bkgIntervals





    def __add__(self, other):


        tmp = self.evts.tolist()
        tmp.extend(other.evts)
        self.evts = array(tmp)
        self.evts.sort()


    def MakeBlocks(self, p0):


        self.bins = bayesian_blocks(self.evts, p0 = p0)
        self.bType = "bb"

    def MakeKnuth(self):

        if self.needAll:
            self.bins = histtools.knuth_bin_width(self.allEvts,return_bins=True)[1]
            self.binWidth = diff(self.bins)
            return
        else:
            self.bins = histtools.knuth_bin_width(self.evts,return_bins=True)[1]
            self.bType = "kn"
        
    def MakeScotts(self):

        self.bins = histtools.scotts_bin_width(self.evts,return_bins=True)[1]
        self.bType = "sct"

    def MakeFreedman(self):

        self.bins = histtools.freedman_bin_width(self.evts,return_bins=True)[1]
        self.bType = "fm"

    

    def MakeHardnessBlocks(self,binLow,binHi,p0):

        self.S2N(3.,minNumberOfEvents=25)

        binWidth  = diff(self.bins)
        

        #Make two light curves between the energy bins

        chanLo1,chanLo2 = map(self._selectEnergy,binLow)
        chanHi1,chanHi2 = map(self._selectEnergy,binHi)

        tt = logical_and(self.evtExt["PHA"] >= chanLo1, self.evtExt["PHA"]<= chanLo2)
        curveLo =  self.allEvts[tt]

        

        ####Bin the counts using the fine bins

        cnts, _ = histtools.histogram(curveLo,self.bins)
        

        cnts = cnts / binWidth

        ### Get the bkg for this channel selection
        bkg = []
        for j in xrange(len(self.bins)-1):
            tot = 0
            for i in xrange(chanLo1,chanLo2+1):
                
                tot+=self.polynomials[i].integral(self.bins[i],self.bins[i+1])

            bkg.append(tot)
        bkg = array(bkg)
        assert len(cnts)==len(bkg), "Background wrong length"

        #bkgErr = sqrt(bkg)
        #cntErr = sqrt(cnts)

        subCntsLo = cnts-bkg
        subCntsLoErr = sqrt(cnts+bkg)


        #######NEED TO ADD ERROR CALCS HERE
        
        tt = logical_and(self.evtExt["PHA"] >= chanHi1, self.evtExt["PHA"]<= chanHi2)
        curveHi =  self.allEvts[tt]

        cnts, _ = histtools.histogram(curveHi,self.bins)
        

        cnts = cnts / binWidth

        ### Get the bkg for this channel selection
        bkg = []
        for j in xrange(len(self.bins)-1):
            tot = 0
            for i in xrange(chanHi1,chanHi2+1):
                
                tot+=self.polynomials[i].integral(self.bins[i],self.bins[i+1])

            bkg.append(tot)
        bkg = array(bkg)
        assert len(cnts)==len(bkg), "Background wrong length"

        subCntsHi = cnts-bkg
        subCntsHiErr = sqrt(cnts+bkg)

        hardRatio = subCntsHi/subCntsLo


        print len(self.bins)

        errors = hardRatio**2.*(subCntsLoErr/(subCntsLo**2.) + subCntsHiErr/(subCntsHi**2.))

        #bb = BayesianBlocks(binWidth,hardRatio,errors,self.bins[0])
        bb = BayesianBlocks(hardRatio,binWidth,self.bins[0])
        bins,_ = bb.globalOpt(ncp_prior=p0)
        
        lastBin = bins[-1]
        newBins=array(bins)[::2]
        newBins =newBins.tolist()
        newBins.append(lastBin)
        self.bins = array(newBins)

        print len(self.bins)
        self.bType = "hr"




        
        


    def S2N(self,targetSN,minNumberOfEvents=5,maxBinSize=10000.0,significance=True):

        self.needAll = True

        #First fit the background

        self._MakeBackgroundSelections()
        self._FitBackground()
       
        
        sigStop = self.tStop
        sigStart = self.tStart

        #Now loop on the events to get the bins
        tstarts                       = [sigStart]
        tstops                        = []
        signalToNoises                = []
        nEvents                       = 0

       
        if(len(self.evts)==0):
            tstops.append(self.tstop)
            signalToNoises.append(0)
            print("\nNo events selected, no binning possible!")
            return tstarts,tstops,signalToNoises
    


        for event in self.evts:      
            if(event < sigStart or event > sigStop):
                thisSN                    = 0
                continue

            nEvents                    += 1

            thisBackground              = sum(map(lambda x: x.integral(tstarts[-1],event),self.polynomials))  
            
            if(thisBackground<=0):
                if((event)-tstarts[-1] > 1E-2):
                    raise ValueError("Background less or equal to zero between %s and %s! Aborting..." %(tstarts[-1],event))
                else:
                  thisSN                  = 0
                  continue
            
            
            if(nEvents-thisBackground < minNumberOfEvents):
                #print "To few events"
                thisSN                    = 0
                continue
            
            if(significance):
                thisSN                      = max(0,nEvents-thisBackground)/sqrt(thisBackground) 
            else:
                thisSN                      = max(0,nEvents-thisBackground)/sqrt(nEvents)
            

            if(thisSN >= targetSN or (event-tstarts[-1])>maxBinSize):

                tstops.append(event+1E-6)
                tstarts.append(event+1E-6)
                signalToNoises.append(thisSN)

                if(self.verbose):
                  print("Found time interval #%i: %10.4f - %10.4f, with SN = %s" %(len(tstops),tstarts[-2],tstops[-1],thisSN))
                  print("                     events: %10i, background : %10.5f" %(nEvents,thisBackground))
            

                nEvents                   = 0
                continue    
        
        
        #Handle the last bin  
        tstops.append(sigStop)
        signalToNoises.append(thisSN)
        

        self.bins=tstarts
        self.bins.append(tstops[-1])
        self.bType = "sn"
        self.needAll=False

        if self.HRbins:
            #Computing HR BBs so return the time
            return [tstarts,tstarts]
    def MakeTI(self):
        

        ti =[]

        start = (arange(self.fileStart,self.bins[0],.1)).tolist()
        end = (arange(self.bins[-1],self.fileEnd, .1)).tolist()
        

        start.extend(self.bins)
        start.extend(end[1:])
        
        if start[-1]<self.fileEnd:
            start.append(self.fileEnd)
        else:
            start=start[:-1]
            start.append(self.fileEnd)

        

        tiFname = self.fileDir+self.bType  
        mkdir_p(tiFname)
        tiFname +='/'+ self.tteFile[:-3]+'ti'
        
        
        f=open(tiFname,'w')
        f.write(str(len(start))+'\n')

        for t in start:
            f.write(str(t)+'\n')

        f.close()
        
    

    def _MakeBackgroundSelections(self):


        #First bin the data by the Knuth rule
        self.MakeKnuth()
        

        for i in xrange(len(self.bkgIntervals)):

            diffs = abs(self.bins-self.bkgIntervals[i][0])
            self.bkgIntervals[i][0] = self.bins[diffs == min(diffs)    ][0]
            diffs = abs(self.bins-self.bkgIntervals[i][1])
            self.bkgIntervals[i][1] = self.bins[diffs == min(diffs)    ][0]
            





        evts = self.allEvts
        truthTables = []

        






        for sel in self.bkgIntervals:
                
            truthTables.append(logical_and(evts>= sel[0] , evts<= sel[1] ))
                

        tt = truthTables[0]
        if len(truthTables)>1:
                
            for y in truthTables[1:]:
                    
                tt=logical_or(tt,y)


        filteredEvts = evts[tt]


       
        


        cnts,bins=histtools.histogram(filteredEvts,bins=self.bins)
        tt=cnts>0
        meanT=[]
        for i in xrange(len(bins)-1):

            m = mean((bins[i],bins[i+1]))
            meanT.append(m)
        meanT = array(meanT)
        meanT = meanT[tt]
        cnts = cnts/self.binWidth

        self.optimalPolGrade           = self._fitGlobalAndDetermineOptimumGrade(cnts[tt],meanT)
        print "Optimal poly grade: %d"% self.optimalPolGrade


     
        





    def _FitBackground(self):


        ## Seperate everything by energy channel

        eneLcs = []
        for x in xrange(128):

            truthTable = self.evtExt["PHA"] == x

            evts = self.evtExt[truthTable]


            truthTables = []
            for sel in self.bkgIntervals:
                
                truthTables.append(logical_and(evts["TIME"]-self.trigTime>= sel[0] , evts["TIME"]-self.trigTime<= sel[1] ))
                
            
            tt = truthTables[0]
            if len(truthTables)>1:
                                
                for y in truthTables[1:]:
                    
                    tt=logical_or(tt,y)

            self.test=tt
            self.test2 = evts
            evts = evts[tt]

            eneLcs.append(evts)
        self.eneLcs = eneLcs
        self.bkgCoeff = []

        polynomials               = []
        for elc in eneLcs:

            cnts,bins=histtools.histogram(elc["TIME"]-self.trigTime,bins=self.bins)
            tt=cnts>0
            meanT=[]
            for i in xrange(len(bins)-1):

                m = mean((bins[i],bins[i+1]))
                meanT.append(m)
            meanT = array(meanT)
            cnts=cnts/self.binWidth

            thisPolynomial,cstat    = self._fitChannel(cnts[tt],bins[tt], self.optimalPolGrade)      
            #print(thisPolynomial)
            #print '{0:>20} {1:>6.2f} for {2:<5} d.o.f.'.format("logLikelihood = ",cstat,len(filteredData)-self.optimalPolGrade)
            polynomials.append(thisPolynomial)
        #pass
        self.polynomials          = polynomials
        

        #### Now that we have the polys we need to get the rates

        







    def _fitGlobalAndDetermineOptimumGrade(self,cnts,bins):
        #Fit the sum of all the channels to determine the optimal polynomial
        #grade
        Nintervals                = len(bins)

       

        #y                         = []
        #for i in range(Nintervals):
        #  y.append(numpy.sum(counts[i]))
        #pass
        #y                         = numpy.array(y)

        #exposure                  = numpy.array(data.field("EXPOSURE"))

        print("\nLooking for optimal polynomial grade:")
        #Fit all the polynomials
        minGrade                  = 0
        maxGrade                  = 4
        logLikelihoods            = []
        for grade in range(minGrade,maxGrade+1):      
          polynomial, logLike     = self._polyfit(bins,cnts,grade)
          logLikelihoods.append(logLike)         
        pass
        #Found the best one
        deltaLoglike              = array(map(lambda x:2*(x[0]-x[1]),zip(logLikelihoods[:-1],logLikelihoods[1:])))
        print("\ndelta log-likelihoods:")
        for i in range(maxGrade):
          print("%s -> %s: delta Log-likelihood = %s" %(i,i+1,deltaLoglike[i]))
        pass
        print("") 
        deltaThreshold            = 9.0
        mask                      = (deltaLoglike >= deltaThreshold)
        if(len(mask.nonzero()[0])==0):
          #best grade is zero!
          bestGrade               = 0
        else:  
          bestGrade                 = mask.nonzero()[0][-1]+1
        pass

       

        return bestGrade




    def _polyfit(self,x,y,polGrade):

        test = False

        #Check that we have enough counts to perform the fit, otherwise
        #return a "zero polynomial"
        nonzeroMask               = ( y > 0 )
        Nnonzero                  = len(nonzeroMask.nonzero()[0])
        if(Nnonzero==0):
          #No data, nothing to do!
          return Polynomial([0.0]), 0.0
        pass  

        #Compute an initial guess for the polynomial parameters,
        #with a least-square fit (with weight=1) using SVD (extremely robust):
        #(note that polyfit returns the coefficient starting from the maximum grade,
        #thus we need to reverse the order)
        if(test):
          print("  Initial estimate with SVD..."),
        with warnings.catch_warnings():
          warnings.simplefilter("ignore")
          initialGuess            = numpy.polyfit(x,y,polGrade)
        pass
        initialGuess              = initialGuess[::-1]
        if(test):
          print("  done -> %s" %(initialGuess))


        polynomial                = Polynomial(initialGuess)

        #Check that the solution found is meaningful (i.e., definite positive 
        #in the interval of interest)
        M                         = polynomial(x)
        negativeMask              = (M < 0)
        if(len(negativeMask.nonzero()[0])>0):
          #Least square fit failed to converge to a meaningful solution
          #Reset the initialGuess to reasonable value
          initialGuess[0]         = mean(y)
          meanx                   = mean(x)
          initialGuess            = map(lambda x:abs(x[1])/pow(meanx,x[0]),enumerate(initialGuess))

        #Improve the solution using a logLikelihood statistic (Cash statistic)
        logLikelihood             = LogLikelihood(x,y,polynomial)        

        #Check that we have enough non-empty bins to fit this grade of polynomial,
        #otherwise lower the grade
        dof                       = Nnonzero-(polGrade+1)      
        if(test): 
          print("Effective dof: %s" %(dof))
        if(dof <= 2):
          #Fit is poorly or ill-conditioned, have to reduce the number of parameters
          while(dof < 2 and len(initialGuess)>1):
            initialGuess          = initialGuess[:-1]
            polynomial            = Polynomial(initialGuess)
            logLikelihood         = LogLikelihood(x,y,polynomial)  
          pass        
        pass

        #Try to improve the fit with the log-likelihood    
        #try:
        if(1==1):
          finalEstimate           = scipy.optimize.fmin(logLikelihood, initialGuess, 
                                                        ftol=1E-5, xtol=1E-5,
                                                        maxiter=1e6,maxfun=1E6,
                                                        disp=False)
        #except:
        else:
          #We shouldn't get here!
          raise RuntimeError("Fit failed! Try to reduce the degree of the polynomial.")
        pass

        #Get the value for cstat at the minimum
        minlogLikelihood          = logLikelihood(finalEstimate)

        #Update the polynomial with the fitted parameters,
        #and the relative covariance matrix
        finalPolynomial           = Polynomial(finalEstimate)
        try:
          finalPolynomial.computeCovarianceMatrix(logLikelihood.getFreeDerivs)             
        except Exception:
          raise
        #if test is defined, compare the results with those obtained with ROOT
      

        return finalPolynomial, minlogLikelihood
        pass


    def _fitChannel(self,cnts,bins,polGrade):

        Nintervals                = len(bins)

        #Put data to fit in an x vector and y vector
        

        polynomial, minLogLike    = self._polyfit(bins,cnts,polGrade)

        return polynomial, minLogLike
        pass





    def _selectEnergy(self, energy):

        tt = logical_and(energy>=self.chanLU["E_MIN"], energy < self.chanLU["E_MAX"]  )
        
        chan = self.chanLU["CHANNEL"][tt][0]
        return chan 
        


    def Preview(self):

        hist(self.evts,bins=self.bins,normed=True,histtype='stepfilled',alpha=.2)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        
    

        
