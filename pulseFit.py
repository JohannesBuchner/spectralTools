from scipy.optimize import curve_fit
from matplotlib.widgets import RadioButtons, Button, CheckButtons
import matplotlib.pyplot as plt
from numpy import mean, zeros, matrix, sqrt, array, linspace, power
from TmaxSelector import TmaxSelector
import pickle
from mpCurveFit import mpCurveFit
import pyfits as pf
from pulseModel import KRLPulse, NorrisPulse
from lightCurve import lightCurve
from pulseModSelector import pulseModSelector
#import matplotlib 




#plt.switch_backend( 'TkAgg')
#plt.ion()

class pulseFit:



    def __init__(self):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.fig = plt.figure(1) 
        self.ax = self.fig.add_subplot(111,title="Pulse Display")
        self.fig.subplots_adjust(left=0.3)
        self.numPulse = 1
        self.flcFlag = False
        self.timeOffset = 0.0

        self.tMaxSelector = 0

        self.resultAx =False
        self.useSelector = False

        #check if a pulseModSelector has been passed
        self.pms = False
        self.radio = False
        
    #    self.initialValues=[0,1,1,1]
    #    self.fixPar = [1,0,0,1,1]

      #  self.pulseLookup=[f1,f2,f3]

        ax = plt.axes([.05, 0.05, 0.12, 0.08])
        self.addButton = Button(ax,'Add Pulse',color='0.95', hovercolor='0.45')
        self.addButton.on_clicked(self.AddPulse)

        ax2 = plt.axes([.05, 0.15, 0.12, 0.08])
        self.findMaxButton = Button(ax2,'Find Max',color='0.95', hovercolor='0.45')
        self.findMaxButton.on_clicked(self.FindMax)

        ax3 = plt.axes([.05, 0.25, 0.12, 0.08])
        self.fitButton = Button(ax3,'Fit',color='0.95', hovercolor='0.45')
        self.fitButton.on_clicked(self.FitPulse)



        ax4 = plt.axes([.05, 0.45, 0.12, 0.08])
        self.useSelectorCheck = CheckButtons(ax4, ["Selector"], [False] )
        self.useSelectorCheck.on_clicked(self.UseSelector)

        
    def UseSelector(self,event=0):
        if self.useSelector:
            self.useSelector = False
        else:
            self.useSelector = True

     #   print self.useSelector



    def SetPulseModSelector(self,pms):

        self.pms = pms


    def ReadTTE(self,tteFile,eMin,eMax,tMin,tMax,dt):


        self.data = 0
        self.errors = 0
        self.tBins = 0

        self.numPulse = 1

        if self.tMaxSelector != 0:
            del self.tMaxSelector


        print "\n\nReading TTE data. This will CRASH if there are no background files!!!!\n\n"
        lc = lightCurve('') # Give it a fake parfile
        lc.inFiles = [tteFile]
        lc.ImportData()
        lc.dt=dt
        lc.tMax=tMax
        lc.tMin=tMin
        lc.eBins = [[eMin,eMax]]
        lc.bkgFlag=True
        lc.EnergyBinning()
        lc.TimeBinning()

        


        self.data = lc.lcBkgSub[0]
        self.errors = array(map(sqrt,lc.bkgSum[0]+lc.lc[0]))
        self.tBins = array(lc.tBins)

        self.PlotData()



    def LoadFlux(self,fileName):

        flux  = pickle.load(open(fileName))
        
        self.fluxes = flux['fluxes']
        self.errors = array(flux['errors'])
        self.tBins = flux['tBins']
        
        axcolor = 'lightgoldenrodyellow'


 #       self.radioFig = plt.figure(2)

        if self.radio:
            #del self.radio
            self.radioAx.cla()
#
        self.radioAx = plt.axes([.01, 0.7, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']

        self.radio = RadioButtons(self.radioAx,tuple(self.fluxes.keys()))
        self.radio.on_clicked(self.Selector)
        
        self.PlotData()
        #self.FindMax() # Must happen after data is plotted!


    def SetData(self, flux, errors, tBins):
        
        self.data = flux
        self.errors = errors
        self.tBins = tBins


  


    def FindMax(self,event=0):

        self.fmax = self.data.max()

        for i in range(len(self.data)):
            if self.data[i]==self.fmax:
                self.tmax=[mean(self.tBins[i])]
                break

        #self.initialValues[3]=self.fmax
        self.tMaxSelector.points  = self.tmax
     
        print "\n\n###############\t###############\n"
        print "TMAX: "+str(self.tmax[0])
        print "FMAX: "+str(self.fmax)

        print "\n\n###############\t###############\n"
        
        # This will set the initial value for the KRLPulse
        # Tmax value to what is found
        if self.pms:
            if self.pms.pulseInt.get() == 0:
                self.pms.p1a.delete(0,100)
                self.pms.p1a.insert(0,str(self.tmax[0]))
                

    def ReadFluxLC(self,fluxLC):


        self.fluxes =  fluxLC.fluxes

        self.errors =  array(fluxLC.fluxErrors)
        self.tBins = fluxLC.tBins

        self.models = fluxLC.modelNames


        self.flcFlag =True


        axcolor = 'lightgoldenrodyellow'


 #       self.radioFig = plt.figure(2)
#
        ax = plt.axes([.01, 0.7, 0.2, 0.32], axisbg=axcolor)

        self.data = self.fluxes['total']

        if self.radio:
            del self.radio
            self.radioAx.cla()


        self.radio = RadioButtons(self.radioAx,tuple(self.fluxes.keys()))
        self.radio.on_clicked(self.Selector)
        
        self.PlotData()
       # self.FindMax()
        

###### Plotting

    def Selector(self,label):

        self.ax.cla()
        self.data = self.fluxes[label]
        self.tMaxSelector.Kill()
        
        del self.tMaxSelector
        self.PlotData()

        

    def AddPulse(self,event=0):

        if self.numPulse>=3:
            self.numPulse=1
            self.tMaxSelector.SetNumPoints(self.numPulse)
        else:
            self.numPulse+=1
            self.tMaxSelector.SetNumPoints(self.numPulse)



    def PlotData(self):

    
       # plt.axes(self.fig.get_axes()[0])
        self.ax.cla()
        
        lowerT=[]
        upperT=[]

        for x,y in zip (self.tBins, map(mean,self.tBins)  ):

            lowerT.append(abs(x[0]-y))
            upperT.append(abs(x[1]-y))

        pl,er,bar, = self.ax.errorbar(array(map(mean,self.tBins))+self.timeOffset,self.data,fmt='o', color='b', yerr=array(self.errors), xerr=[lowerT,upperT])
        self.pl = pl

        self.tMaxSelector = TmaxSelector(pl)
        self.tMaxSelector.SetNumPoints(self.numPulse)
        self.fig.canvas.draw()

        
    def ResetPlot(self):
        del self.pl


    def DisplayFitPlot(self):
        

        #if self.resultAx:
        #    self.resultAx.cla()
        #else:  
        self.resultFig = plt.figure(2)
        self.resultAx = self.resultFig.add_subplot(111)


        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.GetPulseMod()
            func = pulseMod.pulseLookup[self.numPulse-1]
    
        m = linspace(0,self.tBins.flatten().max(),1000)+self.timeOffset

        tmpFitResults = array(self.fitResults)
        tmpFitResults[3]+=self.timeOffset

        def f(t):
            
            tmp=[t]
            #print tmp
            tmp.extend(tmpFitResults.tolist())
         
            return apply(func,tmp)


        n = array(map(f,m))

   
        lowerT=[]
        upperT=[]

        for x,y in zip (self.tBins, map(mean,self.tBins)  ):

            lowerT.append(abs(x[0]-y))
            upperT.append(abs(x[1]-y))

        lowerT =array(lowerT)+self.timeOffset
        upperT = array(upperT)+self.timeOffset
        

        self.resultAx.errorbar(array(map(mean,self.tBins))+self.timeOffset,self.data,fmt='o', color='b',yerr=array(self.errors), xerr=[lowerT,upperT])
        self.resultAx.plot(m,n,'r')
        self.resultFig.canvas.draw()




    def DisplayTestPlot(self,c,r,d,tmax,fmax):


        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.GetPulseMod()
            func = pulseMod.pulseLookup[self.numPulse-1]

            
        m = linspace(0,self.tBins.flatten().max(),1000)+self.timeOffset

        tmpFitResults = array([c,r,d,tmax,fmax])
        tmpFitResults[3]+=self.timeOffset

        def f(t):
            
            tmp=[t]
            #print tmp
            tmp.extend(tmpFitResults.tolist())
         
            return apply(func,tmp)


        n = array(map(f,m))

   
        lowerT=[]
        upperT=[]

        for x,y in zip (self.tBins, map(mean,self.tBins)  ):

            lowerT.append(abs(x[0]-y))
            upperT.append(abs(x[1]-y))

        lowerT =array(lowerT)+self.timeOffset
        upperT = array(upperT)+self.timeOffset
        self.testFig = plt.figure(2)


        resultAx = self.testFig.add_subplot(111)

        resultAx.loglog(m,n,'r')
        resultAx.errorbar(array(map(mean,self.tBins))+self.timeOffset,self.data,fmt='o', color='b',yerr=array(self.errors), xerr=[lowerT,upperT])
        
        self.testFig.canvas.draw()





###### Pulse Fitting


    def FitPulse(self,event=0):

        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.GetPulseMod()
            func = pulseMod.pulseLookup[self.numPulse-1]


       # func = self.pulseLookup[self.numPulse-1]
       
        initialValues=pulseMod.GetInitialValues()
       

        self.tmax=self.tMaxSelector.GetData()
       
        if self.tmax == []:
            fixPar = pulseMod.GetFixedParams()
            limits = pulseMod.limits
            initialValues = pulseMod.GetInitialValues()

        else:

            print "\n_________________________________\n"
            print "Initial guess(es) for Tmax"
            for x in self.tmax:
                print x
                print "\n_________________________________\n"


            limits = []
       
            tmp1 = []
            tmp3=[]
            for x in self.tmax:
                tmp2 = initialValues
                if self.useSelector:
                    tmp2[0] = x
                tmp1.extend(tmp2)
                tmp3.extend(pulseMod.GetFixedParams())
                limits.extend(pulseMod.limits)
            
            
        
            intialValues = tmp1
            fixPar=tmp3


       
        # print limits
        # print initialValues
        # print fixPar
  

        # I've removed the limits for now I should add them in later.
        fit = mpCurveFit(func, array(map(mean,self.tBins))+self.timeOffset, self.data.tolist(), sigma=self.errors,p0=initialValues,fixed=fixPar,maxiter=400, limits=limits) 

       
        self.fitResults = fit.params 
        self.fitCov = fit.errors
        self.fitResults[3]-=self.timeOffset
        self.GoodnessOfFit()
        self.DisplayFitResults()
        self.DisplayFitPlot()






    def GoodnessOfFit(self):

        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.GetPulseMod()
            func = pulseMod.pulseLookup[self.numPulse-1]


        def f(t):
            
            tmp=[t]
            #print tmp
            tmp.extend(self.fitResults.tolist())
         
            return apply(func,tmp)
        

        n = array(map(f, map(mean,self.tBins)  ))


        tmp = (power((self.data - n),2))/power(self.errors,2)

        chi2 =  tmp.sum()

        dof = len(self.data) - 5*self.numPulse - 1

        print "\nReduced Chi2: "+str(chi2/dof)






    def DisplayFitResults(self):

        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.pulseInt.get()
            



        fitParams = [['tmax: ','c: ','r: ','d: ', 'fmax: '],['ts: ','A: ','tr: ','td: ']][pulseMod]

        for i in range(self.numPulse-1):
            fitParams.extend(fitParams)


        fitParams = tuple(fitParams)
        errors = self.fitCov
       # errors = map(sqrt, matrix(self.fitCov).diagonal().tolist()[0] )

        print '\n\n********************************'
        print 'Fit Results:\n'

        for x,y,z in zip(fitParams,self.fitResults,errors):

            print x+str(y)+' +/- '+str(z)



        print '\n\n******************************\n'


    def SaveFit(self,fileName='fitSave.p'):
        '''
        Save the fit results to a dictionary in the form of dic['<param>'][pulseNumber][val,err]

        '''
        if self.pms:
            #If there is pms then we need to set the right models
            pulseMod = self.pms.pulseInt.get()

        fitParams = (['tmax','c','r','d', 'fmax'],['ts','A','tr','td'])[pulseMod]

#        errors = map(sqrt, matrix(self.fitCov).diagonal().tolist()[0] )
        errors=self.fitCov
        saveList = []

        for i in range( len(fitParams) ):
            
            tmpRow=[]

            for j in range(self.numPulse):
                
                tmp = [self.fitResults[i+j*len(fitParams)],errors[i+j*len(fitParams)]]
                tmpRow.append(tmp)
            saveList.append(tmpRow)


        saveDic = dict (zip(fitParams ,saveList) )
        
        pickle.dump(saveDic,open(fileName,'w'))




    
    



    





        
        
