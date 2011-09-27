from scipy.optimize import curve_fit
from matplotlib.widgets import RadioButtons, Button
import matplotlib.pyplot as plt
from numpy import mean, zeros
from TmaxSelector import TmaxSelector




class pulseFit:



    def __init__(self):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.fig = plt.figure(1) 
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.3)
        self.numPulse = 1


        self.pulseLookup=[self.f1,self.f2,self.f3]

      




    def SetData(self, flux, errors, tBins):
        
        self.data = flux
        self.errors = errors
        self.tBins = tBins


    def ReadFLuxLC(self,fluxLC):


        self.fluxes =  fluxLC.fluxes

        self.errors =  fluxLC.errors
        self.tBins = fluxLC.tBins

        self.models = fluxLC.modelNames


        axcolor = 'lightgoldenrodyellow'


        self.radioFig = plt.figure(2)

        ax = plt.axes([.5, 0.5, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']

        self.radio = RadioButtons(ax,tuple(self.fluxes.keys()))
        self.radio.on_clicked(self.Selector)
        

###### Plotting

    def Selector(self,label):

        self.ax.cla()
        self.data = self.fluxes[label]
        self.PlotData()
        
        #self.ax.draw()
        

    def AddPulse(self,event):

        self.numPulse+=1
        self.tMaxSelector.SetNumPoints(self.numPulse)


   


    def PlotData(self):


     



        pl, = self.ax.plot(map(mean,self.tBins),self.data,"go")

        self.tMaxSelector = TmaxSelector(pl)


        ax = plt.axes([.05, 0.05, 0.2, 0.32])
        self.addButton = Button(ax,'Add Pulse ('+str(self.numPulse)+')')

        self.addButton.on_clicked(self.AddPulse)

        self.fig.canvas.draw()
      #  pl.xlabel("T")
      #  pl.ylabel("Flux")
        
        

###### Pulse Fitting


    def FitPulse(self):

       func = self.pulseLookup[self.numPulse-1]
       
       initialValues=[]

       self.tmax=self.tMaxSelector.GetData()


       for x in self.tmax:
           initialValues.extend([1,1,1,x,1])


       popt, pcov = curve_fit(func, self.tBins, self.data, sigma=self.errors,p0=initialValues)


        

    def KRLPulse(t,c,r,d,tmax,fmax):

        f = (fmax*(((((t+c)/(tmax+c)))**r)/(((d+(r*((((t+c)/(tmax+c)))**(1+r))))/(d+r))**((d+r)/(1+r)))))
	return f



    def f1(t,c,r,d,tmax,fmax):
        return self.KRLPulse(t,c,r,d,tmax,fmax)

    def f2(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2):
        return self.KRLPulse(t,c1,r1,d1,tmax1,fmax1)+self.KRLPulse(t,c2,r2,d2,tmax2,fmax2)

    def f3(t,c1,r1,d1,tmax1,fmax1,c2,r2,d2,tmax2,fmax2,c3,r3,d3,tmax3,fmax3):
        return self.KRLPulse(t,c1,r1,d1,tmax1,fmax1)+self.KRLPulse(t,c2,r2,d2,tmax2,fmax2)+self.KRLPulse(t,c3,r3,d3,tmax3,fmax3)
    
    



    





        
        
