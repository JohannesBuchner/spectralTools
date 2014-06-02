import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from numpy import log10, log, linspace, array, e, exp, power, logical_and
from mpfitexy import mpfitexy
import pickle
from regionSelector import regionSelector
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
        self.regionSelector = False


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


    def HICfromPulseFit(self,param='Epeak',indexGuess=2,fixint=True):

        #print self.F0
        #print self.E0


        self.ComputeHIC(self.F0,self.E0,param=param,indexGuess=indexGuess,fixint=fixint)
        



    def ShowHIC(self,E0,param='Epeak'):

        xData = self.params['values'][param][self.timeIndex:self.tStop].flatten()/E0
        xErr = self.params['errors'][param][self.timeIndex:self.tStop].flatten()/E0
        yData = self.flux[self.timeIndex:self.tStop]
        yErr = self.fluxError[self.timeIndex:self.tStop]

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

        self.thicFig = plt.figure(3)

        self.thicAx = self.thicFig.add_subplot(111)

        plt.xlabel("log("+param+")")
        plt.ylabel('log(Flux)')

        pl, junk, junk2 = self.thicAx.errorbar(logXdata,logYdata,xerr=logXerr,yerr=logYerr,fmt='-',color='b')
        return pl


    def ComputeHIC(self,F0,E0,param='Epeak',indexGuess=2,fixint=True):


        xData = self.params['values'][param][self.timeIndex:self.tStop].flatten()/E0
        xErr = self.params['errors'][param][self.timeIndex:self.tStop].flatten()/E0

        yData = self.flux[self.timeIndex:self.tStop]
        yErr = self.fluxError[self.timeIndex:self.tStop]

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)
    

      #  print logYdata
      #  print logYerr
      #  print logXerr
      #  print logXdata

        

        results, errors, =  mpfitexy(logXdata,logYdata,logXerr,logYerr, guess = [indexGuess,log10(F0)], fixint=fixint, quiet=0)

        index = results[0]
        F0 = 10**results[1]
        

        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)


        plt.xlabel("log("+param+")")
        plt.ylabel('log(Flux)')
        x = linspace(xData.min()*E0,xData.max()*E0,1000)
        y = HIC(x,E0,F0,index)
        #print yData
        #print log10(yData)
    
        logXdata, logXerr, = self.ConvertData2Log(xData*E0,xErr*E0)

        self.hicAx.loglog(x,y,'r')

        self.hicAx.errorbar(xData*E0,yData,xerr=xErr*E0,yerr=yErr,fmt='o',color='b')
        #self.hicAx.errorbar(logXdata,logYdata,xerr=logXerr,yerr=logYerr,fmt='o',color='b')

       

    def HFCfromPulseFit(self):

        self.ComputeHFC(self.E0)
 


    def ShowHFC(self, E0,param='Epeak'):

        yData = self.params['values'][param][self.timeIndex:self.tStop].flatten()
        yErr = self.params['errors'][param][self.timeIndex:self.tStop].flatten()

        self.ComputeFluence()

        xData = self.t90
        xErr = self.fluxError[self.timeIndex:self.tStop]

        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

        self.thfcFig = plt.figure(4)
        self.thfcAx = self.thfcFig.add_subplot(111)


        self.thfcAx.errorbar(xData,logYdata,xerr=xErr,yerr=logYerr,fmt='o',color='b')

        plt.xlabel("Time Running Fluence")
        plt.ylabel("log("+param+")")
        

    def ComputeHFC(self,E0,param='Epeak', fixint=True):
        
        

        yData = self.params['values'][param][self.timeIndex:self.tStop].flatten()
        yErr = self.params['errors'][param][self.timeIndex:self.tStop].flatten()

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
        plt.xlabel("Time Running Fluence")
        plt.ylabel("log("+param+")")
      
        results, errors, =  mpfitexy(xData,logYdata,xErr,logYerr, guess = [-2,log10(E0)], fixint=fixint)


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


        
        
        


    def RangedHIC(self,param):
       
        self.timeIndex = 0
        self.tStop = None
        
        pl = self.ShowHIC(1,param=param)
        self.rs = regionSelector(pl)
      
        print "Select a region  and then call HICfromPulseFit("+param+")"
    

    def ComputeRangedHIC(self, param):

        
        data = self.rs.GetData()

        data.sort()

        data = map(lambda x: power(10,x), data )
        
        tmp1 = self.params['values'][param].flatten() > data[0]
        tmp2 = self.params['values'][param].flatten() < data[1]

        truthTable = logical_and(tmp1,tmp2)

        E0 = self.params['values'][param][truthTable].flatten().max()

        xData = self.params['values'][param][truthTable].flatten()/E0
        xErr = self.params['errors'][param][truthTable].flatten()/E0
        yData = self.flux[truthTable]
        yErr = array(self.fluxError)[truthTable]

        logXdata, logXerr, = self.ConvertData2Log(xData,xErr)
        logYdata, logYerr, = self.ConvertData2Log(yData,yErr)

        F0 = yData.max()
    

      #  print logYdata
      #  print logYerr
      #  print logXerr
      #  print logXdata

     

        results, errors, =  mpfitexy(logXdata,logYdata,logXerr,logYerr, guess = [2,log10(F0)], fixint=False, quiet=0)

        index = results[0]
        F0 = 10**results[1]
        

        self.hicFig = plt.figure(1)

        self.hicAx = self.hicFig.add_subplot(111)


        plt.xlabel("log("+param+")")
        plt.ylabel('log(Flux)')
        x = linspace(xData.min()*E0,xData.max()*E0,1000)
        y = HIC(x,E0,F0,index)
        #print yData
        #print log10(yData)
    
        logXdata, logXerr, = self.ConvertData2Log(xData*E0,xErr*E0)

        self.hicAx.loglog(x,y,'r')
        self.hicAx.errorbar(xData*E0,yData,xerr=xErr*E0,yerr=yErr,fmt='o',color='b')
