#from models import *
import matplotlib.pyplot as plt
from models import modelLookup
from numpy import array, zeros

class spectraPlotter:
'''
This class can plot several spectral models together
it can be read from an SCAT or the fitfile made by fitReader




'''
    def __init__(self, multi=True,pht=False,energy=False,vFv=False):

        self.phtFig = plt.Figure(1)
        self.energyFig = plt.Figure(2)
        self.vFvFig = plt.Figure(3)

        self.phtAx = phtFig.add_subplot(111)
        self.energyAx = energyFig.add_subplot(111)
        self.vFvAx = vFvFig.add_subplot(111)

        self.phtAx.xlabel("Energy (keV)")
        self.phtAx.ylabel("pht/s/cm2")

        self.energyAx.xlabel("Energy (keV)")
        self.energyAx.ylabel("ergs/s/cm2")

        self.vFvAx.xlabel("Energy (keV)")
        self.vFvAx.ylabel("pht/s/cm2")

        self.energyPlt = energy
        self.phtPlt = pht
        self.vFvPlt = vFv
        
        self.modelLookup = modelLookup


    def FitReader(self):
        print "In Base Class: Define in subclass"


    def SetFitsFile(self, fName):
        self.fname = fName

    def SetParams(self,args):
        self.params=args
        
    def SetModel(self,modelName):
        models = []
        for x in modelName:
             models.append(self.modelLookup[modelName])
        self.model=models

    def GetModel(self,energy):
        
        flux = zeros(len(energy))
        for x,y in zip(self.model,self.params):
            flux = flux+ x(energy,*y)
       
        return flux

        
    def ReadFits(self):
        
        fits = self.FitReader()
        for fit in fits:
            modelName = fit.GetModelName()
            self.SetModel(model)
            params = fit.GetParams()
            self.SetParams(params)
            self.SetEnergies()
            
            if phtPlt:
                self.PhotonPlot()

            if energyPlt:
                self.EnergyPlot()

            if vFvPlt:
                self.vFvPlot()
           
                
            

            




    def PhotonPlot(self):


        eMin = self.GetEMin()
        eMax = self.GetEMax()

        energy = arange(eMin,eMax,1000)
        photonSpectra = self.GetModel(energy)

        self.phtAx.loglog(energy,photonSpectra)

    def EnergyPlot(self):

        eMin = self.GetEMin()
        eMax = self.GetEMax()

        energy = arange(eMin,eMax,1000)
        energySpectra = energy*self.GetModel(energy)

        self.energyAx.loglog(energy,energySpectra)

     def vFvPlot(self):

        eMin = self.GetEMin()
        eMax = self.GetEMax()

        energy = arange(eMin,eMax,1000)
        vFvSpectra = energy*energy*self.GetModel(energy)

        self.vFvAx.loglog(energy,vFvSpectra)


     
class Fit:

    def __inti__(self, modelName, params):

        self.modelName
        self.params = params

    def GetParams(self):
        return self.params
    
    def GetModelName(self):
        return self.modelName
