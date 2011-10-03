import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from numpy import log10, log, linspace
from fitexy import fitexy


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


    def SetDecatPhase(self, fitResult, pulseNum = 1   , tStop=None):

        




    def ComputeHIC(self,param='Epeak',F0,E0):


        xData = self.params['values'][param]/E0
        xErr = self.params['errors'][param]
        yData = self.flux
        yErr = self.fluxError 

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)


        results, errors, =  mpfitexy(logXdata,logYdata,logXerr,logYerr, guess = [1,F0], fixint=True)

        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)

        
        

        
        

        self.hicAx.loglog()


    def ConvertData2Log(self,data,err):

        logData = log10(data)
        logErr = err/(data*log(10))
        
        return [logData,logErr]


        
        
   

        

        


        



