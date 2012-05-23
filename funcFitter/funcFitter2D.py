from funcFitter import funcFitter
from mpfitexy import mpfitexy


class funcFitter2D(funcFitter):


    def __init__(self, dataLog=None):
        self.interactive =False
        self.fitFunc = self.funcTable["Linear"]
        self.funcName = "Linear"
        self.dataLog=dataLog
        self.xName="x"
        self.yName="y"
        self.title="fit"
        


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

        

    def Fit(showGuess=False):
        
        self._PrepareData()
        print "Fitting data with 2D Errors"
        print ">>>\t"+self.dataLog+" data has been converted to log10 space"
        

        resultFig = plt.figure(2)
        resultAx = resultFig.add_subplot(111)

        xRange = linspace(self.xData.min(),self.xData.max(),100)
        yGuess = self.fitFunc(xRange,*self.iVals)

        if showGuess:
            resultAx.plot(xRange,yGuess,'r')

        if self.fixed[0]==1.:
            fixslope=True
        if self.fixed[1]==1.:
            fixint=True

        mpfitexy(self.xData,self.yData,self.xErr,self.yErr,guess=self.iVals)
