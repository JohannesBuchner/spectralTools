from scipy.optimize import curve_fit
from matplotlib.widgets import RadioButtons, Button
import matplotlib.pyplot as plt
from numpy import mean, zeros, matrix, sqrt, array, linspace
from TmaxSelector import TmaxSelector
import pickle



class pulseFit:



    def __init__(self):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.fig = plt.figure(1) 
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.3)
        self.numPulse = 1
        self.flcFlag = False

        self.pulseLookup=[f1,f2,f3]

      


    def LoadFlux(self,fileName):

        flux  = pickle.load(open(fileName))
        
        self.fluxes = flux['fluxes']
        self.errors = flux['errors']
        self.tBins = flux['tBins']
        
        axcolor = 'lightgoldenrodyellow'


 #       self.radioFig = plt.figure(2)
#
        ax = plt.axes([.01, 0.7, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']

        self.radio = RadioButtons(ax,tuple(self.fluxes.keys()))
        self.radio.on_clicked(self.Selector)
        self.PlotData()


    def SetData(self, flux, errors, tBins):
        
        self.data = flux
        self.errors = errors
        self.tBins = tBins


  




    def ReadFluxLC(self,fluxLC):


        self.fluxes =  fluxLC.fluxes

        self.errors =  fluxLC.fluxErrors
        self.tBins = fluxLC.tBins

        self.models = fluxLC.modelNames


        self.flcFlag =True


        axcolor = 'lightgoldenrodyellow'


 #       self.radioFig = plt.figure(2)
#
        ax = plt.axes([.01, 0.7, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']

        self.radio = RadioButtons(ax,tuple(self.fluxes.keys()))
        self.radio.on_clicked(self.Selector)
        self.PlotData()
        

###### Plotting

    def Selector(self,label):

        self.ax.cla()
        self.data = self.fluxes[label]
        self.tMaxSelector.Kill()
        
        del self.tMaxSelector
        self.PlotData()

        

    def AddPulse(self,event=0):

        if self.numPulse>=3:
            self.numPulse=1
            self.tMaxSelector.SetNumPoints(self.numPulse)

        else:
            

            self.numPulse+=1
            self.tMaxSelector.SetNumPoints(self.numPulse)


   


    def PlotData(self):

    
       # plt.axes(self.fig.get_axes()[0])
        
        lowerT=[]
        upperT=[]

        for x,y in zip (self.tBins, map(mean,self.tBins)  ):

            lowerT.append(abs(x[0]-y))
            upperT.append(abs(x[1]-y))


        

        pl,er,bar, = self.ax.errorbar(map(mean,self.tBins),self.data,fmt='o', color='g', yerr=array(self.errors), xerr=[lowerT,upperT])
        self.pl = pl

        self.tMaxSelector = TmaxSelector(pl)
        self.tMaxSelector.SetNumPoints(self.numPulse)

        ax = plt.axes([.05, 0.05, 0.2, 0.32])
        self.addButton = Button(ax,'Add Pulse')

        self.addButton.on_clicked(self.AddPulse)

   #     ax = plt.axes([.06, 0.05, 0.2, 0.32])
   #     self.fitButton = Button(ax,'Fit')

    #    self.fitButton.on_clicked(self.FitPulse)



        self.fig.canvas.draw()
      #  pl.xlabel("T")
      #  pl.ylabel("Flux")
        
    def ResetPlot(self):

      #   self.pl.remove()
        del self.pl


    def DisplayFitPlot(self):
            
        x = linspace(0,self.tBins.flatten().max(),2)

        def f(t):
            
            tmp=[t]
            #print tmp
            tmp.extend(self.fitResults.tolist())
            print tmp

            return apply(self.pulseLookup[self.numPulse-1],tmp.extend(self.fitResults.tolist()))


        

        y=f(x)

          
        lowerT=[]
        upperT=[]

        for x,y in zip (self.tBins, map(mean,self.tBins)  ):

            lowerT.append(abs(x[0]-y))
            upperT.append(abs(x[1]-y))

        self.resultFig = figure(2)


        resultAx = self.resultFig.add_subplot(111)


        resultAx.errorbar(map(mean,self.tBins),self.data,fmt='o', color='b',yerr=array(self.errors), xerr=[lowerT,upperT])
        resultAx.plot(x,y,'r')
        self.resultFig.canvas.draw()






###### Pulse Fitting


    def FitPulse(self,event=0):

       func = self.pulseLookup[self.numPulse-1]
       
       initialValues=[]

       self.tmax=self.tMaxSelector.GetData()


       print "Initial guess(es) for Tmax"
       for x in self.tmax:
           print x
       print  "\n___________\n"



       for x in self.tmax:
           #initialValues.extend([.1,-1,-.5,x,1])
           initialValues.extend([1,1,1,x,1])

       #print initialValues

       popt, pcov = curve_fit(func, map(mean,self.tBins), self.data.tolist(), sigma=self.errors,p0=initialValues)


       self.fitResults = popt
       self.fitCov = pcov



    def DisplayFitResults(self):


        fitParams = ['c: ','r: ','d: ','tmax: ', 'fmax: ']

        for i in range(self.numPulse-1):
            fitParams.extend(fitParams)


        fitParams = tuple(fitParams)

        errors = map(sqrt, matrix(self.fitCov).diagonal().tolist()[0] )

        print '\n\n*****************************'
        print 'Fit Results:\n'

        for x,y,z in zip(fitParams,self.fitResults,errors):

            print x+str(y)+' +/- '+str(z)



        print '\n\n******************************\n'


    def SaveFit(self):
         

        errors = map(sqrt, matrix(self.fitCov).diagonal().tolist()[0] )
         
        f=open('pulsefitresults.txt','w')
        for x,y in zip(self.fitResults,errors):
            write(str(x)+'\t'+str(y))
        
        print "\nWrote \'pulsefitresults.txt\'\n\n"


   







 ####################################################       

def KRLPulse(t,c,r,d,tmax,fmax):

    f = (fmax*(((((t+c)/(tmax+c)))**r)/(((d+(r*((((t+c)/(tmax+c)))**(1+r))))/(d+r))**((d+r)/(1+r)))))
    return f



def f1(t,c,r,d,tmax,fmax):
    return KRLPulse(t,c,r,d,tmax,fmax)

def f2(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2):
    return KRLPulse(t,c1,r1,d1,tmax1,fmax1)+KRLPulse(t,c2,r2,d2,tmax2,fmax2)

def f3(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2,c3,r3,d3,tmax3,fmax3):
    return KRLPulse(t,c1,r1,d1,tmax1,fmax1)+KRLPulse(t,c2,r2,d2,tmax2,fmax2)+KRLPulse(t,c3,r3,d3,tmax3,fmax3)
    
    



    





        
        
