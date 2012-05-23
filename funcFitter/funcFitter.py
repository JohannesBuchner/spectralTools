from mpfit import mpfit
from mpfitexy import mpfitexy
from mpCurveFit import mpCurveFit
from functions import functionLookup
import inspect
from numpy import array, linspace, log10, log, dtype
import matplotlib.pyplot as plt

class funcFitter:

    def __init__(self, interactive = False):

        print "Start Up"
        self.interactive = interactive
        #self.twoD_flag = False
        self.funcTable =  functionLookup
        self.xName="x"
        self.yName="y"
        self.title="fit"
        self.yErr =None
        

        if self.interactive:
            self.PrintFuncs()


    def SelectFunction(self, funcName = ""):
        
        self.fitFunc = self.funcTable[funcName]
        self.funcName = funcName
        args, varargs, varkw, defaults = inspect.getargspec(self.fitFunc)
        self.params = args[1:]
        args = args[2:]
        if self.interactive:
            
            print "\n\nSet initial values:\n"
            vals = [1.]
            fixeds = [0]
            for x in args:
                val = float(raw_input("\t"+x +": "))
                fixed = int(raw_input("\tfixed (1/0): "))
                vals.append(val)
                fixeds.append(fixed)
            self.iVals = vals
            self.fixed = fixeds

    

    def PrintFuncs(self):

        print "Functions to fit:"
        for x in self.funcTable.keys():
            print "\t\""+x+"\""
        



    def SetXData(self, xData):
        self.xData = xData

    def SetYData(self, yData):
        self.yData = yData


    def SetXErr(self, xErr):
        


    def SetYErr(self, yErr):
        
        self.yErr = yErr

    def SetXname(self,xName):
        self.xName = str(xName)

    def SetYname(self,yName):
        self.yName = str(yName)

    def SetTitle(self,title):
        self.title=str(title)
    
    def ConvertData2Log(self,data,err):

        logData = log10(data)
        logErr = err/(data*log(10))
        
        return [array(logData),array(logErr)]  


    def Fit(self,showLog=False,showGuess=False):
        
        print "Fitting with "+self.funcName 



        resultFig = plt.figure(2)
        resultAx = resultFig.add_subplot(111)
            

        xRange = linspace(self.xData.min(),self.xData.max(),100)
        yGuess = self.fitFunc(xRange,*self.iVals)
          
            
        if showLog:
                
            resultAx.loglog(self.xData,self.yData,'b.')
            if showGuess:
                    
                resultAx.loglog(xRange,yGuess,'r')
        if showGuess:
            print "here"
            resultAx.plot(xRange,yGuess,'r')
                

        resultAx.errorbar(self.xData,self.yData,fmt='o', color='b',yerr=self.yErr)
            
                

        fit = mpCurveFit(self.fitFunc, self.xData, self.yData, p0 = self.iVals, sigma = self.yErr, fixed = self.fixed,quiet=0)
        params, errors = [fit.params, fit.errors]
            

        print "\nFit results: "
        for x,y,z in zip(self.params, params, errors):
            print x+": "+str(y)+" +/- "+str(z)
        

        xRange = linspace(self.xData.min(),self.xData.max(),100)
        yResult = self.fitFunc(xRange,*params)
        self.result = array( zip(params,errors))
            
            

         

            

        if showLog:
            resultAx.loglog(xRange,yResult,"g")
                
        else:
            resultAx.plot(xRange,yResult,"g")
        resultAx.errorbar(self.xData,self.yData,fmt='o', color='b',yerr=self.yErr)
        resultAx.set_xlabel(self.xName)
        resultAx.set_ylabel(self.yName)
        resultAx.set_title(self.title)
           
            
            
            
