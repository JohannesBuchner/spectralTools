import matplotlib.pyplot as plt
from numpy import array
from matplotlib.ticker import MaxNLocator, MultipleLocator



class bbLook:


    def __init__(self):

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
       
        self.lightcurve = []
        
        

    def AddLegendStrings(self,ls):
        self.ls = ls

   
    def _CalculateBackground(self):

        #Assuming that the first bin is the background
        self.bg = []
        for lc in self.lightcurve:
            bg=lc[0,1]
            self.bg.append(bg)

        self.bg = array(self.bg)
        
    

    def AddLightCurve(self, lc):

        self.lightcurve.append(lc)
        

    def PlotLightCurves(self):


        #colorTable = ["red","green","blue","black","yellow","cyan"]
        alpha = []
        for i in range(1,len(self.lightcurve)+1):
            
            alpha.append(1./float(i))


        self._CalculateBackground()
        for lc,bg,alf in zip(self.lightcurve,self.bg,alpha):

            pl = self.ax.plot(lc[:,0],lc[:,1]-bg,linewidth=2)
            
        self.ax.xaxis.set_major_locator(MaxNLocator(20))
        self.ax.xaxis.set_minor_locator(MaxNLocator(80))
        self.ax.set_xlabel("time (s)")
        self.ax.set_ylabel("counts/s")
        plt.legend(self.ls)
        plt.show()

        
