from astroML.density_estimation import histtools, bayesian_blocks
from astroML.plotting import hist 
import astropy.io.fits as fits
from numpy import linspace, arange



class tteBinning(object):


    def __init__(self, tteFile, tStart, tStop):

        

        self.tteFile = tteFile
        fitsFile = fits.open(tteFile)

        evts = fitsFile[2].data['TIME']

        header = fitsFile[0].header
        trigTime = header['TRIGTIME']
        start = header['TSTART'] - trigTime
        end = header['TSTOP'] - trigTime
        

        self.fileStart = start
        self.fileEnd = end
        self.tStop = tStop
        self.tStart = tStart


        self.evts = evts - trigTime

        self.evts = evts[evts <= tStop]
        self.evts = self.evts[self.evts > tStart]


    def MakeBlocks(self, p0):


        self.bins = bayesian_blocks(self.evts, p0 = p0)

    def MakeKnuth(self):
        
        self.bins = histtools.knuth_bin_width(self.evts,return_bins=True)[1]
        
        
    def MakeScotts(self):

        self.bins = histtools.scotts_bin_width(self.evts,return_bins=True)[1]

    def MakeFreedman(self):

        self.bins = histtools.freedman_bin_width(self.evts,return_bins=True)[1]


    

    def MakeHardnessBlocks(self,p0):

        pass




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


        f=open(self.tteFile[:-3]+'.ti','w')
        f.write(str(len(start))+'\n')

        for t in start:
            f.write(str(t)+'\n')

        f.close()
        
     


    def Preview(self):

        hist(self.evts,bins=self.bins,normed=True,histtype='stepfilled',alpha=.2)

        
        
    

        
