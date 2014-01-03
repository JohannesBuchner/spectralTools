from astroML.density_estimation import histtools, bayesian_blocks
import astropy.io.fits as fits
from numpy import linspace



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

        
        
        



    def _MakeTI(self):
        

        ti =[]

        start = (linspace(self.fileStart,self.bins[0])).tolist()
        end = (linspace(self.bins[-1],self.fileEnd)).tolist()
        print start
        print end

        start.extend(self.bins)
        start.extend(end[1:])

        f=open(self.tteFile[:-3]+'.ti','w')
        f.write(str(len(start))+'\n')

        for t in start:
            f.write(str(t)+'\n')

        f.close()
        
     

        
    

        
