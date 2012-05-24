from funcFitter import funcFitter
from mpfitexy import mpfitexy
from functions import functionLookup
import matplotlib.pyplot as plt
from numpy import array, linspace, log10, log, dtype
import inspect


class funcFitter2D(funcFitter):


    def __init__(self, dataLog=None):


        self.funcTable =  functionLookup
        self.interactive =False
        self.fitFunc = self.funcTable["Linear"]
        self.funcName = "Linear"
        args, varargs, varkw, defaults = inspect.getargspec(self.fitFunc)
        self.params = args[1:]
        args = args[2:]
        self.dataLog=dataLog
        self.xName="x"
        self.yName="y"
        self.title="fit"
        self.dataColor="b"
        self.fitColor="g"
        self.guessColor="r"
        self.dataMarker="o"
        self.fitLineStyle="-"
        


    def SetXErr(self,xErr):
        
        self.twoD_flag = True
        self.xErr = xErr


    def _PrepareData(self):
        
        if self.dataLog == None:
            self.dataLog="No"
            return
        
        elif self.dataLog == "x":
            self.xData, self.xErr = self.ConvertData2Log(self.xData,self.xErr)

        elif self.dataLog == "y":
            self.yData, self.yErr = self.ConvertData2Log(self.yData,self.yErr)

        elif self.dataLog == "all":
            self.yData, self.yErr = self.ConvertData2Log(self.yData,self.yErr)
            self.xData, self.xErr = self.ConvertData2Log(self.xData,self.xErr)

        

    def Fit(self,showGuess=False):
        
        self._PrepareData()
        print "Fitting data with 2D Errors"
        print ">>>\t"+self.dataLog+" data has been converted to log10 space"
        

        resultFig = plt.figure(self.plotNum)
        resultAx = resultFig.add_subplot(111)

        xRange = linspace(self.xData.min(),self.xData.max(),100)
        yGuess = self.fitFunc(xRange,*self.iVals)

        if showGuess:
            resultAx.plot(xRange,yGuess,self.guessColor+self.fitLineStyle)

        fixslope=False
        fixint=False
        if self.fixed[0]==1.:
            fixslope=True
        if self.fixed[1]==1.:
            fixint=True


        resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr)
        fit = mpfitexy(self.xData,self.yData,self.xErr,self.yErr,guess=self.iVals,fixslope=fixslope,fixint=fixint)
        params, errors = fit

        print "\nFit results: "
        for x,y,z in zip(self.params, params, errors):
            print x+": "+str(y)+" +/- "+str(z)
        

        xRange = linspace(self.xData.min(),self.xData.max(),100)
        yResult = self.fitFunc(xRange,*params)
        self.result = array( zip(params,errors))

        resultAx.plot(xRange,yResult,self.fitColor+self.fitLineStyle)
        #resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr)
        resultAx.set_xlabel(self.xName)
        resultAx.set_ylabel(self.yName)
        resultAx.set_title(self.title)
