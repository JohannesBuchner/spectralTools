from funcFitter import funcFitter
from mpfitexy import mpfitexy
from functions import functionLookup
import matplotlib.pyplot as plt
from numpy import array, linspace, log10, log, dtype
import inspect


def filt_neg_err(y, yerr, set_ymin=1e-6): 
    ymin = y - yerr 
    filt = ymin < 0 
    yerr_pos = yerr.copy() 
    yerr_neg = yerr.copy() 
    yerr_neg[filt] =  y[filt] - set_ymin 
    return array([yerr_neg, yerr_pos])

class funcFitter2D(funcFitter):


    def __init__(self, dataLog=None, rDisp=False):


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
        self.errorbarThick=1.
        self.fitLineThick=2.
        self.plotNum=1000
        self.rDisp=rDisp
        self.limits=None
        self.fontsize=10
        self.pivot = 1.


    def SetXErr(self,xErr):
        
        self.twoD_flag = True
        self.xErr = xErr

    def SetPivot(self,pivot):
        self.pivot=pivot

    def _PrepareData(self):
        

        self.dataMin = self.xData.min()
        self.dataMax = self.xData.max()
        
        if self.dataLog == None:
            self.dataLog="No"
            self.xData = self.xData/self.pivot
           # self.xErr = self.xErr/self.pivot
            return
        
        elif self.dataLog == "x":
            self.xData, self.xErr = self.ConvertData2Log(self.xData,self.xErr)

        elif self.dataLog == "y":
            self.yData, self.yErr = self.ConvertData2Log(self.yData,self.yErr)

        elif self.dataLog == "all":
            self.yData, self.yErr = self.ConvertData2Log(self.yData,self.yErr)
            self.xData, self.xErr = self.ConvertData2Log(self.xData,self.xErr)
            self.xData = self.xData - log10(self.pivot)
            #self.xErr = self.xErr - log10(self.pivot)

        

    def Fit(self,showGuess=False):
        
        self._PrepareData()
        print "Fitting data with 2D Errors"
        print ">>>\t"+self.dataLog+" data has been converted to log10 space"
        
        
        resultFig = plt.figure(self.plotNum)
        resultAx = resultFig.add_subplot(111)
        self.ax = resultAx
        xRange = linspace(self.dataMin,self.dataMax,100)
        yGuess = self.fitFunc(xRange,*self.iVals)

        if showGuess:
            resultAx.plot(xRange,yGuess,color=self.guessColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)

        fixslope=False
        fixint=False
        if self.fixed[0]==1.:
            fixslope=True
        if self.fixed[1]==1.:
            fixint=True

        if self.dataLog == None:
            resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr,elinewidth=self.errorbarThick)
        
        
        
        #resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr,elinewidth=self.errorbarThick)
        
        fit = mpfitexy(self.xData,self.yData,self.xErr,self.yErr,guess=self.iVals,fixslope=fixslope,fixint=fixint,limits=self.limits,quiet=1)
        params, errors, chi2, dof, covar = fit
        #params = params.tolist().append(self.pivot)
        #errors = errors.tolist().append(0)
        
        #params=array(params)
        #errors = array(errors)
        #print params
        #print errors
        #self.xData = self.xData*self.pivot
        print "\nFit results: "
                
        try:
            for x,y,z in zip(self.params, params, errors):
                print x+": "+str(y)+" +/- "+str(z)
            if self.rDisp:
                self._ResultsDisplay(resultAx,params,errors)

        except TypeError:
            print "-----------> FIT FAILED!!!!!"
            return


        

        xRange = linspace(self.dataMin,self.dataMax,100)
        yResult = self.fitFunc(xRange,*params)

        #if self.dataLog == 'y' or 'all':
        #    print "Converting fit params into linear space"
        #    params[1] = 10**(params[1])
        #    errors[1] = params[1]*log(10)*errors[1]
        

        self.covar = covar


        self.result = zip(params,errors)
        self.result.append([chi2,dof])
        self.result=array(self.result)


        if self.dataLog == None:
            #resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr,elinewidth=self.errorbarThick)
            resultAx.plot(xRange,yResult,color=self.fitColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)

        elif self.dataLog == "x":
             resultAx.set_xscale("log")
             xDat, xErr = self.ReconvertData(self.xData,self.xErr) 
             
             tmpXerr = filt_neg_err(xDat,xErr)

             resultAx.semilogx(10**(xRange),yResult,color=self.fitColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)
             resultAx.errorbar(xDat,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=tmpXerr,elinewidth=self.errorbarThick)

        elif self.dataLog == "y":
            resultAx.set_yscale("log")
            yDat, yErr = self.ReconvertData(self.yData,self.yErr)
            tmpYerr = filt_neg_err(yDat,yErr) 
            resultAx.semilogy((xRange),10**(yResult),color=self.fitColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)
            resultAx.errorbar((self.xData),yDat,fmt=self.dataMarker, color=self.dataColor,yerr=tmpYerr,xerr=(self.xErr),elinewidth=self.errorbarThick)
            

        elif self.dataLog == "all":
            xDat, xErr = self.ReconvertData(self.xData+(log10(self.pivot)),self.xErr) 
            tmpXerr = filt_neg_err(xDat,xErr)
            yDat, yErr = self.ReconvertData(self.yData,self.yErr)
            tmpYerr = filt_neg_err(yDat,yErr) 
            
            ### New code added here 
            yResult = self.fitFunc(log10(xRange)-log10(self.pivot),*params)
            self.xData = self.xData+log10(self.pivot)
            
            ###
            
            resultAx.set_xscale("log",nonposx='clip')
            resultAx.set_yscale("log",nonposy='clip')
            resultAx.loglog((xRange),10**(yResult),color=self.fitColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)
            resultAx.errorbar(xDat,yDat,fmt=self.dataMarker, color=self.dataColor,yerr=tmpYerr,xerr=tmpXerr,elinewidth=self.errorbarThick)
            

        #resultAx.plot(xRange,yResult,color=self.fitColor,linestyle=self.fitLineStyle,linewidth=self.fitLineThick)
        #resultAx.errorbar(self.xData,self.yData,fmt=self.dataMarker, color=self.dataColor,yerr=self.yErr,xerr=self.xErr)
        resultAx.set_xlabel(self.xName,fontsize=self.fontsize)
        resultAx.set_ylabel(self.yName,fontsize=self.fontsize)
        resultAx.set_title(self.title,fontsize=self.fontsize)
        self.ax = resultAx
