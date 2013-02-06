#from models import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt


from models import modelLookup
from numpy import array, zeros, logspace, log10, asarray, sqrt, linspace, arange



fig_width_pt =245.26653  # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
fig_width = fig_width_pt*inches_per_pt  # width in inches
fig_height = fig_width*golden_mean      # height in inches
fig_size =  [fig_width,fig_height]
params = {'backend': 'ps',
          'axes.labelsize': 10,
          'text.fontsize': 10,
          'legend.fontsize': 10,
          'xtick.labelsize': 8,
          'ytick.labelsize': 8,
          'text.usetex': True,
          'figure.figsize': fig_size,
          'font.family': 'serif'}
plt.rcParams.update(params)
keV2erg =1.60217646e-9

class spectralPlotter:

    def __init__(self, multi=True,pht=False,energy=False,vFv=False,eMin=10.,eMax=40000.,uniModel=None,manualColor=None):

        if pht:
            self.phtFig = plt.figure(1)
            self.phtAx = self.phtFig.add_subplot(111)
            self.phtAx.set_xlabel("Energy (keV)")
            self.phtAx.set_ylabel(r"Flux (photons s$^{-1}$ cm$^{-2}$ keV$^{-1}$)")

        if energy:
            self.energyFig = plt.figure(2)
            self.energyAx = self.energyFig.add_subplot(111)
        
            self.energyAx.set_xlabel("Energy (keV)")
            self.energyAx.set_ylabel("$F_E$ (ergs s$^{-1}$ cm$^{-2}$ keV$^{-1}$)")


        if vFv:
            self.vFvFig = plt.figure(3)
            self.vFvAx = self.vFvFig.add_subplot(111)
            self.vFvAx.set_xlabel("Energy (keV)")
            self.vFvAx.set_ylabel(r"$\nu F_{\nu}$ (ergs$^2$ s$^{-1}$ cm$^{-2}$ keV$^{-1}$)")


        if manualColor != None:

            self.setColor = True
            self.manualColor = manualColor
        else:
            self.setColor = False
        

        self.energyPlt = energy
        self.phtPlt = pht
        self.vFvPlt = vFv
        
        self.modelLookup = modelLookup
        self.multi = multi
        self.uniModel = uniModel

        self.eMin = float(eMin)
        self.eMax = float(eMax)
    


    def FitReader(self):
        print "In Base Class: Define in subclass"


    def SetFitsFile(self, fName):
        self.fName = fName
        
        for f in fName:
            print "reading: "+f

        self.numFiles = len(fName)

        print "finished reading "+str(self.numFiles)+ " files"
        
        #print "reading"self.fName

    def SetParams(self,args):
        self.params=args
        
    def SetModel(self,modelName):
        models=[]
        for x in modelName:
            models.append(self.modelLookup[x])
        self.model=models


    def GetModel(self,energy):
        
        
        if self.multi:
            flux = []
            for x,y in zip(self.model,self.params):

                
                
                if x == self.modelLookup["Total Test Synchrotron"]: # Have to do it bin my bin
                    tmpFlux =[]
                    for en in energy:
                        tmpFlux.append(x(en,*y[0][0]))
                    tmpFlux = array(tmpFlux)

                    flux.append(tmpFlux)

                elif x == self.modelLookup["Fast Synchrotron"]: # Have to do it bin my bin
                    tmpFlux =[]
                    for en in energy:
                        tmpFlux.append(x(en,*y[0][0]))
                    tmpFlux = array(tmpFlux)

                    flux.append(tmpFlux)

                else:
                    flux.append(x(energy,*y[0][0]))
            flux=array(flux)



        else:
            flux = zeros( len(energy))
                
            for x,y in zip(self.model,self.params):
                
                if x == self.modelLookup["Total Test Synchrotron"]: # Have to do it bin my bin
                    tmpFlux =[]
                    for en in energy:
                        tmpFlux.append(x(en,*y[0][0]))
                    tmpFlux = array(tmpFlux)
                    flux = flux +tmpFlux
                else:
                    flux = flux + x(energy,*y[0][0])
       
        #self.test = flux
        return flux

        
    def ReadFits(self):
        
        fits = self.FitReader()

        red = []
        blue = []
        for i in arange(float(self.numFiles),.9,-1):

            colorNum = i/self.numFiles

            red.append((1,colorNum,0.))
            blue.append((0.,colorNum,1.))


        if self.setColor:
            red = self.manualColor


     
        for fit,r,b in zip(fits,red,blue):
            

            if self.uniModel == None:
                modelName = fit.GetModelName()
                self.SetModel(modelName)
                params = fit.GetParams()
               
                self.SetParams(params)
                self.colorTable = [r,b]
            #self.SetEnergies()
            else:
                
                self.colorTable = [r,b]
                modelName = fit.GetModelName()
                modelIndex = modelName.index(self.uniModel)
                modelName=[self.uniModel]

                self.SetModel(modelName)
                params = [fit.GetParams()[modelIndex]]
                self.SetParams(params)
            
            if self.phtPlt:
                self.PhotonPlot()


            if self.energyPlt:
                self.EnergyPlot()

            if self.vFvPlt:
                self.vFvPlot()
           
                

    def PhotonPlot(self):


        eMin = self.eMin
        eMax = self.eMax

        energy = logspace(log10(eMin),log10(eMax),num=1000)
        photonSpectra = self.GetModel(energy)

        #for sp in photonSpectra
        if self.multi:
            #First we want to set some nice limits
            mins=[]
            for sp in photonSpectra:
                mins.append(sp.min())
            bottomLim = asarray(mins).max()
            
            for sp,cl  in zip(photonSpectra,self.colorTable):
                self.phtAx.loglog(energy,sp,linewidth=1.5,color=cl)
            self.phtAx.set_ylim(bottom = bottomLim)

        else:
            self.phtAx.loglog(energy,photonSpectra,linewidth=1.5, color = "CornflowerBlue")
        

        
        self.phtAx.get_figure().canvas.draw()

    def EnergyPlot(self):

        eMin = self.eMin
        eMax = self.eMax

        energy = logspace(log10(eMin),log10(eMax),num=1000)
        energySpectra = keV2erg*energy*self.GetModel(energy)



        if self.multi:
            #First we want to set some nice limits
            mins=[]
            for sp in energySpectra:
                mins.append(sp.min())
            bottomLim = asarray(mins).max()
            
            for sp,cl  in zip(energySpectra,self.colorTable):
                self.energyAx.loglog(energy,sp,linewidth=1.5,color=cl)
            self.energyAx.set_ylim(bottom = bottomLim)

        else:
            self.energyAx.loglog(energy,energySpectra,linewidth=1.5, color = "CornflowerBlue")

        self.energyAx.set_xlim(right=energy.max())

        


        
        self.energyAx.get_figure().canvas.draw()

    def vFvPlot(self):

        eMin = self.eMin
        eMax = self.eMax

        energy = logspace(log10(eMin),log10(eMax),num=1000)
        vFvSpectra = (keV2erg)**2*energy*energy*self.GetModel(energy)


        if self.multi:
            #First we want to set some nice limits
            mins=[]
            for sp in vFvSpectra:
                mins.append(sp.min())
            bottomLim = asarray(mins).max()
            
            for sp,cl  in zip(vFvSpectra,self.colorTable):
                self.vFvAx.loglog(energy,sp,linewidth=1.5,color=cl,fillstyle='bottom')
            self.vFvAx.set_ylim(bottom = bottomLim)

        else:
            self.vFvAx.loglog(energy,vFvSpectra,linewidth=1.5, color = "CornflowerBlue")

        self.vFvAx.set_xlim(right=energy.max())

        self.vFvAx.get_figure().canvas.draw()


     
class Fit:

    def __init__(self, modelName, params):

        self.modelName = modelName
        self.params = params

    def GetParams(self):
        return self.params
    
    def GetModelName(self):
        return self.modelName
