#from models import *
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt


from models import modelLookup
from numpy import array, zeros, logspace, log10, asarray

colorTable = ["CornflowerBlue","DeepPink","Lime"]


class spectraPlotter:

    def __init__(self, multi=True,pht=False,energy=False,vFv=False,eMin=10.,eMax=40000.,uniModel=None):

        if pht:
            self.phtFig = plt.figure(1)
            self.phtAx = self.phtFig.add_subplot(111)
            self.phtAx.set_xlabel("Energy (keV)")
            self.phtAx.set_ylabel("pht/s/cm2")

        if energy:
            self.energyFig = plt.figure(2)
            self.energyAx = self.energyFig.add_subplot(111)
        
            self.energyAx.set_xlabel("Energy (keV)")
            self.energyAx.set_ylabel("ergs/s/cm2")


        if vFv:
            self.vFvFig = plt.figure(3)
            self.vFvAx = self.vFvFig.add_subplot(111)
            self.vFvAx.set_xlabel("Energy (keV)")
            self.vFvAx.set_ylabel("E^2/s/cm2")

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
        for fit in fits:
            if self.uniModel == None:
                modelName = fit.GetModelName()
                self.SetModel(modelName)
                params = fit.GetParams()
                self.SetParams(params)
            #self.SetEnergies()
            else:
                
                
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
            
            for sp,cl  in zip(photonSpectra,colorTable):
                self.phtAx.loglog(energy,sp,linewidth=2.5,color=cl)
            self.phtAx.set_ylim(bottom = bottomLim)

        else:
            self.phtAx.loglog(energy,photonSpectra)
        

        
        self.phtAx.get_figure().canvas.draw()

    def EnergyPlot(self):

        eMin = self.eMin
        eMax = self.eMax

        energy = logspace(log10(eMin),log10(eMax),num=1000)
        energySpectra = energy*self.GetModel(energy)



        if self.multi:
            #First we want to set some nice limits
            mins=[]
            for sp in energySpectra:
                mins.append(sp.min())
            bottomLim = asarray(mins).max()
            
            for sp,cl  in zip(energySpectra,colorTable):
                self.energyAx.loglog(energy,sp,linewidth=2.5,color=cl)
            self.energyAx.set_ylim(bottom = bottomLim)

        else:
            self.energyAx.loglog(energy,energySpectra)

        self.energyAx.set_xlim(right=energy.max())

        


        
        self.energyAx.get_figure().canvas.draw()

    def vFvPlot(self):

        eMin = self.eMin
        eMax = self.eMax

        energy = logspace(log10(eMin),log10(eMax),num=1000)
        vFvSpectra = energy*energy*self.GetModel(energy)


        if self.multi:
            #First we want to set some nice limits
            mins=[]
            for sp in vFvSpectra:
                mins.append(sp.min())
            bottomLim = asarray(mins).max()
            
            for sp,cl  in zip(vFvSpectra,colorTable):
                self.vFvAx.loglog(energy,sp,linewidth=2.5,color=cl)
            self.vFvAx.set_ylim(bottom = bottomLim)

        else:
            self.vFvAx.loglog(energy,vFvSpectra)

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
