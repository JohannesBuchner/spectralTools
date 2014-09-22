from astroML.density_estimation import histtools, bayesian_blocks
from astroML.plotting import hist 
import astropy.io.fits as fits
from numpy import linspace, arange, array, logical_and, mean, sum, sqrt, logical_or, diff, sqrt, insert, loadtxt, histogram, concatenate, histogram
import os,errno
import warnings
import scipy.optimize
from LogLikelihood import *
from BayesianBlocks_python import BayesianBlocks
from glob import glob
import matplotlib.pyplot as plt
from step import Step


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

        self.bkgExists = False
        self.evtExt = fitsFile[2].data

        evts = evts - trigTime

        self.trigTime = trigTime

        self.allEvts = evts
       
        self.evts = evts[evts < tStop]
        

        print "The Trigger Time for this event::\n%f"%self.trigTime
        
       
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



    def ReadTIFile(self,tiFile):

        self.bins = loadtxt(tiFile)[1:]
        self.binWidth = self.bins[1:]-self.bins[:-1]



    def MakeCustomBins(self,starts,stops):


        starts=array(starts)
        starts.sort()

        stops=array(stops)

        stops.sort()

        self.bins =starts

        self.bins = insert(self.bins,len(self.bins),stops[-1])

        self.binWidth = diff(self.bins)

        self.bType = "cb"

        

    def MakeConstantBins(self,dt):


        if self.needAll:

            self.bins=arange(self.fileStart,self.fileEnd,dt)
            self.binWidth = diff(self.bins)
            return
        else:
            self.bins = arange(self.tStart,self.tStop,dt)
            self.bType='dt'
            self.binWidth = diff(self.bins)

        

        
    def MakeBlocks(self, p0):


        self.bins = bayesian_blocks(self.evts, p0 = p0)
        self.bType = "bb"
        self.binWidth = diff(self.bins)
        
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
        self.binWidth = diff(self.bins)

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




        
        


    def S2N(self,targetSN,minNumberOfEvents=5,maxBinSize=10000.0,significance=True,forceBkg=False):

        self.needAll = True

        #First fit the background

        
        if (not self.bkgExists) or forceBkg:
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

        start = (arange(self.fileStart,self.bins[0],1.)).tolist()
        end = (arange(self.bins[-1],self.fileEnd, 1.)).tolist()
        

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
        


    def MakeSwiftPHA(self,swiftTime,bn):

        
        dT = self.trigTime - swiftTime
        

        tmp = fits.open('sw%sbevshsp_uf.evt'%bn)
        swiftTrig = tmp[0].header["TRIGTIME"]
        tmp.close()
        del tmp

        print "Time diff between Fermi and Swift: %f"%dT

        gti = []
        phaBins = []
        for i in xrange(len(self.bins)-1):

            b= [self.bins[i]+dT, self.bins[i+1]+dT]
            print b

            gti.append(b)

            
            ##Shifted to Swift MET
            b= [self.trigTime+self.bins[i]+dT,self.trigTime+ self.bins[i+1]+dT]

            phaBins.append(b)


        
    
        ####Here we build the PHA making string for the SWIFT evts
        ####There is an assumption that all the swift preprocessing 
        ####has been completed first. Currently, I have no fucking
        ####idea how to do that
        i=0
        processStrings=[]
        for x in phaBins:
            t1,t2 = x

            processString = '''
            batbinevt infile='sw%sbevshsp_uf.evt' outfile='bin%d.pha' outtype=PHA timedel=0 timebinalg=u energybins='CALDB:80' detmask='total.qmap' ecol=ENERGY weighted=YES outunits=RATE tstart= %f tstop=%f clobber=yes'''%(bn,i,t1,t2)
            
            processStrings.append(processString)
            i+=1


        

        #Make the GTI File

        gtiFile = open("gti.txt","w")
        gtiFile.write("# START\tSTOP\n")
        
        for g in gti:
            
            gtiFile.write("%f\t%f\n"%(g[0],g[1]))
        
        gtiFile.close()


        gtiFile = open("gti.col","w")

        gtiFile.write("START\t1D s\nSTOP\t1D s")
        gtiFile.close()


        gtiFile=open("gti.head",'w')

        gtiFile.write("MJDREFI = 51910\n")
        gtiFile.write("MJDREFF = 0.00074287037\n")
        gtiFile.write("TIMEZERO = 0.0\n")
        gtiFile.write("TRIGTIME = %f"%swiftTrig)
        gtiFile.close()
        
        

        #Load the headas environment
        os.environ["HEADAS"]="/usr/local/heasoft-6.15/i386-apple-darwin13.0.2"
        headas=os.environ["HEADAS"]
        source(headas+"/headas-init.sh")
        os.environ["CALDB"]='/usr/local/caldb'
        source(os.environ["CALDB"]+'/software/tools/caldbinit.sh')
        

        #create the pha files
        for ps in processStrings:
            os.system(ps)
        #for x in phaBins:
        #    print x
        #Get all the pha files to make the RSPs
        phaFiles=glob('bin*.pha')

        for pha in phaFiles:
            updateKeywords='batupdatephakw %s sw%sbevtr.fits.gz'%(pha,bn)
            os.system(updateKeywords)

        for pha in phaFiles:
             phas = 'batphasyserr %s CALDB'%(pha)
             os.system(phas)

        for pha in phaFiles:
            rsp = 'batdrmgen %s %s.rsp NONE'%(pha,pha[:-4])
            os.system(rsp)



        #make a swift lightcurve
        os.system('ftcreate gti.col gti.txt offset.gti headfile=gti.head extname=GTI')

        os.system("ftcopy offset.gti'[1][col START=START+TRIGTIME;STOP=STOP+TRIGTIME]' absolute.gti")


        os.system("batbinevt infile=sw%sbevshsp_uf.evt outfile=mybins.lc outtype=LC timedel=1.0 timebinalg=g energybins=15-150 gtifile=absolute.gti detmask=total.qmap clobber=YES"%bn)

    def MakeGTGRBbins(self):


        tstart=[]
        tstop=[]
        for i in xrange( len(self.bins)-1  ):
            
            tstart.append(self.bins[i])
            tstop.append(self.bins[i+1])

        start=open('tstart.txt','w')
        stop=open('tstop.txt','w')
        startString='['
        stopString='['
        
        for x,y in zip(tstart,tstop):

            startString+='%.3f,'%x
            stopString+='%.3f,'%y

        startString=startString[:-1]+']'
        stopString=stopString[:-1]+']'

        start.write(startString)
        stop.write(stopString)

        start.close()
        stop.close()

    def _MakeBackgroundSelections(self):


        #First bin the data by the Knuth rule or something else
        self.MakeConstantBins (1.)
        #self.MakeKnuth()

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


    def MakeBackgroundSelectionsForDataBinner(self):


      
        

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

        self.filteredEvts = filteredEvts
       
        


        cnts,bins=histogram(filteredEvts,bins=self.bins)
        tt=cnts>0
        meanT=[]
        for i in xrange(len(bins)-1):

            m = mean((bins[i],bins[i+1]))
            meanT.append(m)
        meanT = array(meanT)
        meanT = meanT
        cnts = cnts/self.binWidth

        
        self.optimalPolGrade           = self._fitGlobalAndDetermineOptimumGrade(cnts[tt],meanT[tt])
        print "Optimal poly grade: %d"% self.optimalPolGrade


     
        





    def _FitBackground(self):

        self.bkgExists = True
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

            self.bkgRegion=tt
            
            evts = evts[tt]

            eneLcs.append(evts)
        self.eneLcs = eneLcs
        self.bkgCoeff = []

        polynomials               = []

        self.shit1 =[]
        self.shit2 = []
        for elc in eneLcs:

            cnts,bins=histogram(elc["TIME"]-self.trigTime,bins=self.bins)

 
#            tt=cnts>=0
            meanT=[]
            for i in xrange(len(bins)-1):

                m = mean((bins[i],bins[i+1]))
                meanT.append(m)
            meanT = array(meanT)

            truthTables = []
            for sel in self.bkgIntervals:
                
                truthTables.append(logical_and(meanT>= sel[0] , meanT<= sel[1] ))
                
            
            tt = truthTables[0]
            if len(truthTables)>1:
                                
                for y in truthTables[1:]:
                    
                    tt=logical_or(tt,y)


            
            cnts=cnts/self.binWidth
            
            self.shit1.append(meanT[tt])
            self.shit2.append(cnts[tt])
            thisPolynomial,cstat    = self._fitChannel(cnts[tt],meanT[tt], self.optimalPolGrade)      


            

            
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

        plt.hist(self.evts,bins=self.bins,normed=True,histtype='stepfilled',alpha=.2)



    def PlotData(self):


        if  not self.bkgExists:
            print "No bkg!"
            return


        #newBinsStart = arange(self.fileStart,self.bins[0],.5)
        #newBinsMid = concatenate((newBinsStart,self.bins))
        #newBinsEnd = arange(self.bins[-1],self.fileEnd,.5)
        #newBins = concatenate((newBinsMid,newBinsEnd))
        newBins = self.bins
        tBins = []
        for i in range(len(newBins)-1):
    
            tBins.append([newBins[i],newBins[i+1]])
        tBins=array(tBins)


        cnts,_ = histogram(self.allEvts,bins=newBins)

        binWidth = diff(newBins)
        fig=plt.figure(200)
        ax=fig.add_subplot(111)

        Step(ax,tBins,cnts/binWidth,"k",.5)

        
        bkg = []
        for i in range(len(newBins)-1):
    
            b=0
            for j in range(128):
        
                b+= self.polynomials[j].integral(newBins[i],newBins[i+1])/(newBins[i+1]-newBins[i])
            bkg.append(b)
        meanT = array(map(mean,tBins))
        ax.plot(meanT,bkg,linewidth=2,color="r")

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        
    

        

