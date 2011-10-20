import matplotlib.pyplot as plt

class modelParam:


    def __init__(self, param, tBins):

        self.param = param
        self.errors = errors
        self.tBins = tBins




    def LogPlot(self):

        self.logFig=plt.figure(2)
        ax = self.logFig.add_subplot(111)
        ax.loglog(self.tBins,self.param,'r.')
        ax.errorbar(self.tBins, self.param,yerr=self.errors,fmt='.',color='r')


     def Plot(self):

        self.fig=plt.figure(1)
        ax = self.fig.add_subplot(111)
        ax.errorbar(self.tBins, self.param,yerr=self.errors,fmt='.',color='r')
    







def ConvertData2Log(self,data,err):

    logData = log10(data)
    logErr = err/(data*log(10))
        
    return [array(logData),array(logErr)]
