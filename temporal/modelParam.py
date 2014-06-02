import matplotlib.pyplot as plt
from numpy import mean, zeros, power, linspace, array
from mpCurveFit import mpCurveFit

class modelParam:


    def __init__(self, scat,model,param1name, param2name):

        
        #self.param1 = param1
        #self.param2 = param2
        self.param1name = param1name
        self.param2name = param2name
        
        
        #self.tBins = scat.tBins

        if param1name != "time":
            self.param1 = scat.models[model]['values'][param1name].flatten()
            self.p1errors = scat.models[model]['errors'][param1name].flatten()
        else:
            self.param1 = map(mean,scat.tBins) # Change this
            self.p1errors = zeros(len(scat.tBins))

        if param2name != "time":
            self.param2 = scat.models[model]['values'][param2name].flatten()
            self.p2errors = scat.models[model]['errors'][param2name].flatten()
        else:
            self.param2 = map(mean,scat.tBins)
            self.p2errors = zeros(len(scat.tBins))


    def LogPlot(self):

        self.logFig=plt.figure(2)
        ax = self.logFig.add_subplot(111)
        ax.loglog(self.param1, self.param2,'r.')
        ax.errorbar(self.param1, self.param2, xerr=self.p1errors ,yerr=self.p2errors,fmt='.',color='r')

        plt.xlabel("log("+self.param1name+")")
        plt.ylabel("log("+self.param2name+")")


    def Plot(self):

        self.fig=plt.figure(1)
        ax = self.fig.add_subplot(111)
        ax.errorbar(self.param1, self.param2, xerr=self.p1errors ,yerr=self.p2errors,fmt='.',color='r')
        plt.xlabel(self.param1name)
        plt.ylabel(self.param2name)




    def FitTimeEvolution(self):
        
        if "time" not in self.param1name:
            print "No time parameter"
            return


        def f(x,A,index):
            return A*power(x,index)
        

        fit = mpCurveFit(f,self.param1, self.param2 , p0=[1,-1], sigma = self.p2errors)
        print fit.params
        print fit.errors

        x = linspace(array(self.param1).min(),array(self.param1).max(),1000)
        y = f(x,fit.params[0],fit.params[1])

        plt.loglog(x,y,'b')
        plt.errorbar(self.param1, self.param2, xerr=self.p1errors ,yerr=self.p2errors,fmt='.',color='r')
        plt.xlabel("log("+self.param1name+")")
        plt.ylabel("log("+self.param2name+")")



def ConvertData2Log(self,data,err):

    logData = log10(data)
    logErr = err/(data*log(10))
        
    return [array(logData),array(logErr)]
