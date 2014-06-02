from numpy import array
import xspec as xs 
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import Grid
from spectralTools.step import Step



class xspecView(object):


    def __init__(self):

        #xs.Plot.device="/xs"
        xs.Plot.xAxis='keV'

        self.swift = []
        self.nai=[]
        self.bgo=[]

    def LoadSwiftPHAs(self,phaFiles):
        '''
        Load The Swift PHAs in time order

        '''
        for pha in phaFiles:

            s = xs.Spectrum(pha)
            s.ignore("**-15. 150.-**")

            cnts = sum(s.values)


            self.swift.append(cnts)


    def LoadNaiPHAs(self,phaFiles):
        '''
        Load The GBM NaI PHAs in time order

        '''
        for pha in phaFiles:

            s = xs.Spectrum(pha)
            s.ignore("**-8. 1999..-**")
            cnts = sum(s.values)

            self.nai.append(cnts)


    def LoadBGOPHAs(self,phaFiles):
        '''
        Load The GBM BGO  PHAs in time order

        '''
        for pha in phaFiles:

            s = xs.Spectrum(pha)
            s.ignore("**-250. 10000.-**")
            cnts = sum(s.values)

            self.bgo.append(cnts)
    


    def SetTimeBins(self,starts,stops):

        self.tBins = array(zip(starts,stops))

        

    def PlotLC(self):

        fig = plt.figure(1)

        grid = Grid(fig,111,nrows_ncols = (3,1), axes_pad=0.,direction='column')
        
        Step(grid[0],self.tBins,self.swift,'r',1.)

        Step(grid[1],self.tBins,self.nai,'b',1.)

        Step(grid[2],self.tBins,self.bgo,'g',1.)
        

        
            
