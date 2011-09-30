import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def HIC(x,E0,F0,index):

    val = F0*(x/E0)**index

    return val

def HFC(x,E0,phi0):

    val = E0*exp(-x/phi0)
    return val



class correlation:


    def __init__(self,scat,model='Band'):

    

    #    self.model =  model

        self.params = scat.models[model]
        
        self.tBins = self.scat.tBins


        self.multiPlot = False


    def SetMultiPlot(self):
        self.multiPlot = True
        self.figAll = plt.figure()


    def LoadFromFluxSave(self,flux,model='total'):

        self.flux=flux['fluxes'][model]
        self.fluxError = flux['errors']
        

    def LoadFromFluxLC(self,flux,model='total'):

        self.flux = flux.fluxes[model]
        self.fluxError = flux.fluxErrors



    def ComputeFluence(self):
        

        deltaT= array(map(lambda x: x[1]-x[0]  ,self.tBins))
        self.fluence = self.flux*deltaT
        self.t90 = self.fluence.cumsum()




    def ComputeHIC(self,param='Epeak'):


        xData = self.params['values'][param]
        xErr = self.params['errors'][param]
        yData = self.flux
        yErr = self.fluxError 


        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)

        
        

        
        

        self.hicAx.loglog()


        

        

        


        



