import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from numpy import log10, log, linspace, array, e, exp
from mpfitexy import mpfitexy
import pickle

def HIC(x,E0,F0,index):

    val = F0*(x/E0)**index

    return val

def HFC(x,E0,phi0):

    val = E0*exp(-x/phi0)
    return val



class correlation:


    def __init__(self,scat,model='Band\'s GRB, Epeak'):

    

    #    self.model =  model

        self.params = scat.models[model]
        
        self.tBins = scat.tBins

        self.timeIndex = 0
        self.tStop = None
        self.multiPlot = False


    def SetMultiPlot(self):
        self.multiPlot = True
        self.figAll = plt.figure()


    def LoadFromFluxSave(self,flux,model='Band\'s GRB, Epeak'):

        flux=pickle.load(open(flux))
        

        self.flux=flux['fluxes'][model]
        self.fluxError = flux['errors']
        

    def LoadFromFluxLC(self,flux,model='total'):

        self.flux = flux.fluxes[model]
        self.fluxError = flux.fluxErrors



    def ComputeFluence(self):
        

        deltaT= array(map(lambda x: x[1]-x[0]  ,self.tBins))
        self.fluence = self.flux*deltaT
        self.t90 = self.fluence[self.timeIndex:self.tStop].cumsum()


    def SetDecayPhase(self, fitResult, pulseNum = 1, tStop=-1,param='Epeak'):


        fit =  pickle.load(open(fitResult))


        # Select the max time of the flux from the fit
        # This allows one to use onlt the decay phase of hte pulse in the correlations
        tmax = fit['tmax'][pulseNum-1][0]
        print tmax

        self.tStop = tStop
        
        for i in range(len(self.tBins)):
            
            if (self.tBins[i,0]<tmax) and (self.tBins[i,1]>tmax):

                self.timeIndex = i


        self.F0 = fit['fmax'][pulseNum-1][0]
        self.E0 = self.params['values'][param][self.timeIndex][0]


    def HICfromPulseFit(self):

        self.ComputeHIC(self.F0,self.E0)
        



    def ShowHIC(self,E0,param='Epeak'):

        xData = self.params['values'][param][self.timeIndex:self.tStop]/E0
        xErr = self.params['errors'][param][self.timeIndex:self.tStop]/E0
        yData = self.flux[self.timeIndex:self.tStop]
        yErr = self.fluxError[self.timeIndex:self.tStop]

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)

        self.hicAx.errorbar(logXdata,logYdata,xerr=logXerr,yerr=logYerr,fmt='-',color='b')
      


    def ComputeHIC(self,F0,E0,param='Epeak'):




        xData = self.params['values'][param][self.timeIndex:self.tStop]/E0
        xErr = self.params['errors'][param][self.timeIndex:self.tStop]/E0
        yData = self.flux[self.timeIndex:self.tStop]
        yErr = self.fluxError[self.timeIndex:self.tStop]

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)
    


     

        results, errors, =  mpfitexy(logXdata,logYdata,logXerr,logYerr, guess = [-1,log10(F0)], fixint=True)

        index = results[0]
        

        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)

        x = linspace(xData.min(),xData.max(),1000)
        y = HIC(x,E0,F0,index)




        self.hicAx.loglog(x,y,'r')
      #  self.hicAx.errorbar(xData,yData,xerr=xErr,yerr=yErr,fmt='o',color='b')
        self.hicAx.errorbar(logXdata,logYdata,xerr=logXerr,yerr=logYerr,fmt='o',color='b')
       

    def HFCfromPulseFit(self):

        self.ComputeHFC(self.E0)
 


    def ShowHFC(self, E0):

        yData = self.params['values']['Epeak'][self.timeIndex:self.tStop].flatten()
        yErr = self.params['errors']['Epeak'][self.timeIndex:self.tStop].flatten()

        self.ComputeFluence()

        xData = self.t90
        xErr = self.fluxError[self.timeIndex:self.tStop]

        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

        self.hfcFig = plt.figure(2)
        self.hfcAx = self.hfcFig.add_subplot(111)


        self.hfcAx.errorbar(xData,logYdata,xerr=xErr,yerr=logYerr,fmt='o',color='b')

        

    def ComputeHFC(self,E0):
        
        

        yData = self.params['values']['Epeak'][self.timeIndex:self.tStop].flatten()
        yErr = self.params['errors']['Epeak'][self.timeIndex:self.tStop].flatten()

        self.ComputeFluence()

        xData = self.t90
        xErr = self.fluxError[self.timeIndex:self.tStop]

   #     print yData
   #     print yErr
   #     print xData
   #     print xErr
           

     
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

     
        self.hfcFig = plt.figure(2)
        self.hfcAx = self.hfcFig.add_subplot(111)

      
        results, errors, =  mpfitexy(xData,logYdata,xErr,logYerr, guess = [-2,log10(E0)], fixint=True)


        phi0 = -log10(e)/results[0]
        phi0err = log10(e)/errors[0] ## This is not right


        x = linspace(0,xData.max(),1000)
        y = HFC(x,E0,phi0)


        print phi0
        print phi0err
     


        self.hfcAx.semilogy(x,y,'r')

        self.hfcAx.errorbar(xData,yData,xerr=xErr,yerr=yErr,fmt='o',color='b')
        





    def ConvertData2Log(self,data,err):

        logData = log10(data)
        logErr = err/(data*log(10))
        
        return [array(logData),array(logErr)]


        
        
   

        

        


        



