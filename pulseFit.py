from scipy.optimize import curve_fit
from matplotlib.widgets import RadioButtons
import matplotlib.pyplot as plt







class pulseFit:



    def __init__(self):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.fig = plt.figure() 




    def SetData(self, flux, errors, tBins):
        
        self.data = flux
        self.errors = errors
        self.tBins = tBins


    def ReadFLuxLC(self,fluxLC):


        self.fluxes =  fluxLC.fluxes

        self.errors =  fluxLC.errors
        self.tBins = flux.tBins

        self.models = fluxLC.modelNames

        ax = plt.axes([0.05, 0.4, 0.15, 0.15], axisbg=axcolor)

        self.data = self.fluxes['All']

        
        radio = RadioButtons(ax,tuple(self.models))






    def Selector(label):

        self.ax.cla()
        self.data = self.fluxes['All']
        self.ax.draw()
        

    








    
            



    





        
        
