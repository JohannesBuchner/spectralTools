import pyfits as pf
from numpy import logical_and, transpose, array, genfromtxt, zeros


class llePhaReader:


    def __init__(self,fileName):
        
        self.fileName = fileName
        self.inFile = pf.open(fileName)
        

    def ReadTBins(self,tMin,tMax,trigTime,tBins,dt):

        self.dt=dt
        tmp1 = self.inFile[1].data['TIME']    > trigTime + tMin
        tmp2 = self.inFile[1].data['ENDTIME'] < trigTime + tMax
        truthTable = logical_and(tmp1,tmp2)
        self.tBins = self.inFile[1].data[truthTable]

        if len(tBins)!=len(self.tBins):
            print "Time bins of LLE are not like those of the GBM data"

    def GetEnergyBins(self,eBins):

         self.chans = []
         loEdges = self.inFile[2].data.field('E_MIN')
         channels = self.inFile[2].data.field('CHANNEL')

         self.chans=map(self.GetEdge, map(lambda bbins: channels[self.SelectBin(bbins[0],bbins[1] , loEdges)]  ,eBins) ) 



    def CreateCurves(self):
        
        self.lc =transpose(array( map (self.CreatBin,self.tBins)))
        if self.bkgFlag:
            #print 'here'
            self.ImportBackGrounds()
            self.bkgSubLC = []
            for x,y in zip(self.lc,self.bkgLC):
                self.bkgSubLC.append(x-y)
            print len(self.bkgLC)
            print len(self.bkgSubLC)
                
            
                
            
        
        
    def CreatBin(self,tBin):
    
        return map(lambda x:    tBin[3][x[0]-1:x[1]-1].sum(),  self.chans )
        

 


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

        bkgFilesNames = self.fileName[:-4]+fileEnd
        
        bkg = genfromtxt(bkgFilesNames)
     #   print bkg

        

        #self.bkg =  self.BuildBackground(bk,ch),  bkgFiles, self.chans)
     

    
        try:
            order = len(bkg[0])
        except TypeError:
            order = 1
            

        coeff = [0,0,0,0,0]
        
        summedBkg = []
        bkgLC = []

        binCenters = map(lambda x: (x[0]+x[1])/2.0,self.tBins)
        #print binCenters
        #print binCenters

        for x in self.chans:
            
            #summedBkg.append( bkg[chans[0]:chans[1]].sum(0) )
            summedBkg =  bkg[x[0]:x[1]].sum(0) 
     #       print summedBkg
            if order > 1:
                for i in range(order):
                    coeff[i]=summedBkg[i]
            else:
                coeff[0]=summedBkg
            
            polyBk = lambda x: coeff[0] + coeff[1]*x + coeff[2]*x*x + coeff[3]*pow(x,3) + coeff[4]*pow(x,4)

            bkgLC.append( map(lambda y : polyBk(y) * self.dt ,binCenters) )

        self.bkgLC = array(bkgLC)

       
