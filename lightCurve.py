import astropy.io.fits as pf
import matplotlib.pyplot as plt
from numpy import arange, logical_and, array, zeros, genfromtxt
from shlex import shlex
import sys
import operator
from mpl_toolkits.axes_grid1 import AxesGrid, ImageGrid, Grid
#from llePhaReader import llePhaReader

class lightCurve:

    def __init__(self, parFile,fignum=2):
        """
        A class

        """
        
        self.dataSets = []
        self.inFiles = []
        self.customFlag = False
        self.parFile = parFile
        self.drawGrid = False
        self.drawStack = False
        self.drawStackSub = False
        self.drawGridSub = False
        self.drawBkgGrid=False
        self.save =False
        self.bkgFlag =False
        self.lleFlag=False
        self.fignum =fignum

    def ImportData(self):

        for x in self.inFiles:
            self.dataSets.append(pf.open(x))



    def TimeBinning(self):


        
         
        self.tSeries = []

        self.lc = []
        self.bkgSum = []
        self.lcBkgSub= []

        if not self.customFlag:
       
            tBinsLo = arange(self.tMin, self.tMax-self.dt, self.dt)
            tBinsHi = arange(self.tMin+self.dt, self.tMax, self.dt)
            
            
        else:
            tBinsLo = self.inTBins[:-1]
            tBinsHi = tBinsLo[1:]
        
        self.tBins = map(lambda lo,hi: [lo,hi], tBinsLo, tBinsHi)

        if self.bkgFlag:
            self.ImportBackGrounds()


        for x in xrange(len(self.eBins)):
            
            self.lc.append(zeros(len(self.tBins)))
            self.bkgSum.append(zeros(len(self.tBins)))
            #self.lcBkgSub.append(zeros(len(self.tBins)))

        for x,chans in zip(self.dataSets,self.chans):

            # field 2 contains time 
            pha = x[2].data.field('PHA')
            data = x[2].data
                                 
            energySelections = map(lambda eBin: data[self.SelectBin(eBin[0], eBin[1], pha ,hiFlag=True)] ,chans)
            self.energySelections = energySelections
            timeSelections = map(lambda y:  array(map(lambda bins: len(y[self.SelectBin(bins[0]+self.trigTime, bins[1]+self.trigTime, y.field('TIME') )]) ,self.tBins)), energySelections)
            self.timeSelections = timeSelections
            for i,j in zip(self.lc,timeSelections):
                i+=j
        

            
        # Background subtraction
        if self.bkgFlag:

            for x in self.bkg:
            
                for y,z in zip(self.bkgSum,x):
                    y+=z
        

            #for x,y,z in zip(self.lcBkgSub,self.lc,self.bkgSum):
            #    print x
            #    x = y - z
            #    print x
            for x,y in zip(self.lc,self.bkgSum):
                self.lcBkgSub.append(x-y)
   
        if self.lleFlag:
            self.ProcessLLE()

  
    def EnergyBinning(self):

        self.chans = []
        self.dataTimes = []

        self.trigTime = self.dataSets[0][0].header['TRIGTIME']
        
        for x in self.dataSets:

            tStart = x[0].header['TSTART'] - self.trigTime
            tStop  = x[0].header['TSTOP']  - self.trigTime
            self.dataTimes.append([tStart,tStop])
            loEdges = x[1].data.field('E_MIN')
            channels = x[1].data.field('CHANNEL')
            
            #print loEdges
            
            self.chans.append(map(self.GetEdge, map(lambda bbins: channels[self.SelectBin(bbins[0],bbins[1] , loEdges)]  ,self.eBins) ))            
        
    def GetEdge(self, y):

        if y!=[]:
            return [y.min(),y.max()]
        else:
            return [1000,1001]
            

    def SelectBin(self,low,high,data, hiFlag=False):
        
 
        loMask = data >= low
        if hiFlag:
            hiMask = data <= high
        else:
            hiMask = data < high

 
        mask = logical_and(loMask, hiMask)

     
 
        
        return mask

    def ImportBackGrounds (self):

        fileEnd = '_bkg.dat'

        bkgFilesNames = map(lambda f: f[:-4]+fileEnd, self.inFiles)
        
        bkgFiles = map(genfromtxt,bkgFilesNames)

        

        self.bkg = map(lambda bk,ch: self.BuildBackground(bk,ch),  bkgFiles,self.chans)
            
        


    def BuildBackground(self, bkg, chans):


        tmp=array(bkg)

        if len(tmp.shape)==1:
            order = 0
        else:
            order = tmp.shape[1]

        del tmp
        
        

        coeff = [0,0,0,0,0]
        
        summedBkg = []
        bkgLC = []

        binCenters = map(lambda x: (x[0]+x[1])/2.0,self.tBins)
        #print binCenters

        for x in chans:
            
            #summedBkg.append( bkg[chans[0]:chans[1]].sum(0) )
            summedBkg =  bkg[x[0]:x[1]].sum(0) 
            for i in range(order):
                coeff[i]=summedBkg[i]
                
            
            polyBk = lambda x: coeff[0] + coeff[1]*x + coeff[2]*x*x + coeff[3]*pow(x,3) + coeff[4]*pow(x,4)

            bkgLC.append( map(lambda y : polyBk(y) * self.dt ,binCenters) )

        return bkgLC

       
    
   



    def StackPlot(self):

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        tmp=array(self.tBins)

        

        timeAxis = tmp[:,1]
        for x,eBins in zip(self.lc,self.eBins):
            pl,=ax.step(timeAxis,x, label= str(eBins[0])+' - '+str(eBins[1])+ ' keV',lw=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Counts')
        
        # Cute little script to sort the plots by the labela
        handles, labels = ax.get_legend_handles_labels()
        hl = sorted(zip(handles, labels),key=operator.itemgetter(1))
        #handles2, labels2 = zip(*hl)
        leg = ax.legend(handles, labels, loc=1, borderaxespad=0.)
            # Make the text small on the legend 
        for t in leg.get_texts():
            t.set_fontsize('small')

        self.f1=fig
        if self.save:
            plt.savefig(self.fname+"_stack.pdf")
        


    def GridPlot(self):

        numPlot = len(self.lc)

        tmp=array(self.tBins)

        maxCounts = max(map(max,self.lc))+5
        maxTime = tmp.max()
        minTime = tmp.min()
        Xtxt = maxTime*.6
        Ytxt = maxCounts*.7

        timeAxis = tmp[:,1]

        fig = plt.figure(self.fignum)
        
        #pltNum = numPlot*100 +11
        
        
        grid = Grid(fig,111,nrows_ncols=(numPlot,1), axes_pad=0,  direction='column' )

      
        
        for i in xrange(numPlot):
      
            txtString= str(self.eBins[i][0])+' - '+str(self.eBins[i][1])+ ' keV'
            

            pl, = grid[i].step(timeAxis,self.lc[i],color='k')
            
            ax=pl.get_axes()
            #ax.set_hatch('/')
            #plt.yticks(rotation=-25)
            ax.set_ylim(top=maxCounts)
            #ax.set_yticklables(ax.get_yticks(),rotation=-25)
            yloc = plt.MaxNLocator(10,prune='lower')
            ax.yaxis.set_major_locator(yloc)
            #ax.text(Xtxt,Ytxt,txtString)  #uncomment later
            
            ax.set_ylabel(r"counts s$^{-1}$" )
            ax.set_xlabel("Time [s]")
            ax.set_xlim(right=maxTime,left=minTime)
            
        #plt.xlabel('Time (s)')
        #plt.ylabel('Counts')
        self.vlineLims = [0,maxCounts]
        self.f2=fig
        self.grid = grid
        #fig.tight_layout()
        
        if self.save:
            plt.savefig(self.fname+"_grid.pdf")



    def StackSubPlot(self):

      fig = plt.figure(5)
      ax = fig.add_subplot(111)
      tmp=array(self.tBins)

        

      timeAxis = tmp[:,1]
      for x,eBins in zip(self.lcBkgSub,self.eBins):
          pl,=ax.step(timeAxis,x, label= str(eBins[0])+' - '+str(eBins[1])+ ' keV',lw=2)
      plt.xlabel('Time (s)')
      plt.ylabel('Counts')
      ax.set_ylim(bottom = 0)
        
        # Cute little script to sort the plots by the labela
      handles, labels = ax.get_legend_handles_labels()
      hl = sorted(zip(handles, labels),key=operator.itemgetter(1))
        #handles2, labels2 = zip(*hl)
      leg = ax.legend(handles, labels, loc=1, borderaxespad=0.)
            # Make the text small on the legend 
      for t in leg.get_texts():
          t.set_fontsize('small')
          
      self.f5=fig
      if self.save:
          plt.savefig(self.fname+"_stackSub.pdf")


    def GridSubPlot(self):

        numPlot = len(self.lc)

        tmp=array(self.tBins)

        maxCounts = max(map(max,self.lc))+5
        maxTime = tmp.max()
        minTime = tmp.min()
        Xtxt = maxTime*.6
        Ytxt = maxCounts*.7

        timeAxis = tmp[:,1]

        fig = plt.figure(4)
        
        #pltNum = numPlot*100 +11
        
        grid = AxesGrid(fig,111,nrows_ncols=(numPlot,1), axes_pad=0, aspect=False, direction='column' )

      
        for i in xrange(numPlot):
      
            txtString= str(self.eBins[i][0])+' - '+str(self.eBins[i][1])+ ' keV'
            pl, = grid[i].step(timeAxis,self.lcBkgSub[i])
            ax=pl.get_axes()
            #ax.set_hatch('/')
            ax.set_ylim(top=maxCounts,bottom = 0)
            ax.text(Xtxt,Ytxt,txtString)
        #plt.xlabel('Time (s)')
        #plt.ylabel('Counts')
    
        self.f4=fig
        if self.save:
            plt.savefig(self.fname+"_gridSub.pdf")



    def BkgGridPlot(self):

        numPlot = len(self.lc)

        tmp=array(self.tBins)

        maxCounts = max(map(max,self.lc))+5
        maxTime = tmp.max()
        minTime = tmp.min()
        Xtxt = maxTime*.6
        Ytxt = maxCounts*.7

        timeAxis = tmp[:,1]

        fig = plt.figure(3)
        
        #pltNum = numPlot*100 +11
        
        grid = AxesGrid(fig,111,nrows_ncols=(numPlot,1), axes_pad=0, aspect=False, direction='column' )

      
        for i in xrange(numPlot):
      
            txtString= str(self.eBins[i][0])+' - '+str(self.eBins[i][1])+ ' keV'
            pl, = grid[i].step(timeAxis,self.lc[i])
            grid[i].step(timeAxis,self.bkgSum[i],'r')
            ax=pl.get_axes()
            #ax.set_hatch('/')
            ax.set_ylim(top=maxCounts)
            ax.text(Xtxt,Ytxt,txtString)
            
            
        plt.xlabel('Time (s)')
        plt.ylabel('Counts')
        print "HERE"
        self.f3=fig
        if self.save:
            plt.savefig(self.fname+"_bkgGrid.pdf")
                                
            


    def ProcessLLE(self):
        
        lle=llePhaReader(self.lleFile)
        lle.bkgFlag=self.bkgFlag
        lle.ReadTBins(self.tMin,self.tMax,self.trigTime,self.tBins,self.dt)
        lle.GetEnergyBins(self.eBins)
        lle.CreateCurves()
   
        for i in range(len(self.eBins)):
            self.lc[i]+=lle.lc[i]
            if self.bkgFlag:
           #     print i
                self.lcBkgSub[i]+=lle.bkgSubLC[i]
                self.bkgSum[i]+=lle.bkgLC[i]
        
            
        

    
        
    


    def run(self):

        self.ImportData()
        self.EnergyBinning()
        self.TimeBinning()
        if self.drawStack:
            self.StackPlot()
        if self.drawGrid:
            self.GridPlot()
        if self.drawBkgGrid:
            self.BkgGridPlot()
        if self.drawStackSub:
            self.StackSubPlot()
        if self.drawGridSub:
            self.GridSubPlot()

        
        #plt.show()
    

    def Parser(self):
        
        f = open (self.parFile)
        lex = shlex(f,posix=True)
        lex.whitespace += '='
        lex.whitespace_split = True

        flag=True
        tmpEBin = []
        
        while flag:

            t=lex.get_token()
            print t
            
            
            if t=='EBIN':
                t=lex.get_token()
                tmpEBin.append(t)
           

            if t=='TMIN':
                t=lex.get_token()
                self.tMin = float(t)
            if t=='TMAX':
                t=lex.get_token()
                self.tMax = float(t)
            if t=='DT':
                t=lex.get_token()
                self.dt = float(t)
            if t=='TIMEFILE':
                self.customFlag = True
                t=lex.get_token()
                tmp = open(t)
                tmp = tmp.readlines()
                self.inTBins = map(float,tmp)
            if t=='DATA':
                t=lex.get_token()
                tmp = open(t)
                self.inFiles = map(lambda x: x.strip(),tmp.readlines())
            if t=='STACK':
                self.drawStack=True
            if t=='GRID':
                self.drawGrid=True
            if t=='BKG_GRID':
                self.drawBkgGrid=True
            if t=='GRID_SUB':
                self.drawGridSub=True
                
            if t=='STACK_SUB':
                self.drawStackSub=True

            if t=='SAVE':
                self.save = True
                t=lex.get_token()
                self.fname=t
            if t=='BKG':
                self.bkgFlag=True
            if t=="LLE":
                t=lex.get_token()
                self.lleFlag=True
                self.lleFile = t

            if t ==lex.eof:
                flag=False

        del f 
        del lex

        tmp = map(lambda x: x.split(':'), tmpEBin)
  
        tmp = map(lambda x: [float(x[0]),float(x[1])],tmp)
        tmp.sort()
        self.eBins = tmp
        del tmp 
       
        






if __name__=="__main__":

    inFile = sys.argv[1]
    lc=lightCurve(inFile)
    lc.Parser()
    lc.run()
        
        

        
