from scipy.optimize import curve_fit
from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt
from numpy import mean





class pulseFit:



    def __init__(self):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.fig = plt.figure(1) 
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.3)

      




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

        ax = plt.axes([.01, 0.01, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']


       
     
        
        self.radio = RadioButtons(ax,tuple(self.fluxes.keys()))
        

        

        
        self.radio.on_clicked(self.Selector)
        
        




    def Selector(self,label):

        self.ax.cla()
        self.data = self.fluxes[label]
        self.PlotData()
        
        #self.ax.draw()
        

    def PlotData(self):


        pl, = self.ax.plot(map(mean,self.tBins),self.data,"go")
        self.fig.canvas.draw()
      #  pl.xlabel("T")
      #  pl.ylabel("Flux")
        
        

        


    def FitPulse(self):

        for n in numPulse:
            
        










    
            



    





        
        
