#from scatSpectralPlotter import scatSpectralPlotter
from spectralTools.scatReader import scatReader
import matplotlib.pyplot as plt
from spectralTools.temporal.fluxLightCurve import fluxLightCurve



class evoStack:


    def __init__(self, lightcurve=True, params=[], pht=True, components=['total'], eMin=10, eMax=300 ):
        '''
        Setup the plot for all the propoerties you want to show. 
        
        lightcurve (True/False)
        
        param = [['model','param1'], ['model','param2']]
        
        pht = True makes photon lightcurves, False is energyflux
        '''

        self.eMin = eMin
        self.eMax = eMax


        self.lightcurve = lightcurve
        self.params = params 
        
        self.pht = pht
        self.components = components


        self.files = []

        stackSize = 0

        if lightcurve:
            stackSize+=1
        for x in params:
            stackSize+=1
        
        self.fig = plt.figure(100)
        
        self.axes = []

        for a in range(stackSize):
            self.axes.append(self.fig.add_subplot(stackSize,1,a+1))
        
        
        
        self.stackSize = stackSize


        
        
        
        

        

    def AddInputSCATFiles(self,files):

        self.files.append(files)
        
        
        


   


    def _MakeLightCurve(self):
        
        scats = map(scatReader, self.files)
        
        if len(scats) > 1:
            tmp = scats[0]
            for s in scats[1:]:
                tmp = tmp + s
            scats = tmp
            tBins = scats[0].tBins
            mTBins = scats[0].meanTbins
            
            flc = fluxLightCurve(scats, self.eMin, self.eMax)
        else:
            flc = fluxLightCurve(scats[0], self.eMin, self.eMax)
            tBins = scats[0].tBins
            mTBins = scats[0].meanTbins

        flux = []
        errors = []

        if self.pht:

            flc.CreateLightCurve()
            flc.LightCurveErrors()
            
            for c in self.components:
                flux.append(flc.fluxes[c])
                errors.append(flc.fluxErrors[c])





        else:
            flc.CreateEnergyLightCurves()
            flc.EnergyLightCurveErrors()

            for c in self.components:
                flux.append(flc.energyFluxes[c])
                errors.append(flc.energyFluxErrors[c])


        
        print tBins
        for f, e in zip(flux, errors):

            
            self.axes[0].errorbar(mTBins, f, yerr=e,color='k',fmt='.')
            
            Step(self.axes[0], tBins, f,'k' ,1.)


        



        
        ax = self.axes[0]
        ax.set_xlabel("time (s)")
        if self.pht:
            ax.set_ylabel("photons s$^{-1}$ cm$^{-2}$")
        else:
            ax.set_ylabel("ergs s$^{-1}$ cm$^{-2}$")

        ax.set_xlim(left = tBins[0][0], right=tBins[-1][-1])
            
        plt.draw()


    def _PlotParameters(self):


        scats = map(scatReader, self.files)
        
        if len(scats) > 1:
            tmp = scats[0]
            for s in scats[1:]:
                tmp = tmp + s
            scats = tmp
            tBins = scats[0].tBins
            mTBins = scats[0].meanTbins


        else:
          
            tBins = scats[0].tBins
            mTBins = scats[0].meanTbins

        self.scats = scats

        for p, i  in zip(self.params, range(len(self.params))):


            model, par, = p
            print model
            print par
            val, err, _, =  scats[0].GetParamArray(model,par)

            ax = self.axes[i+1] 
            ax.errorbar(mTBins, val, yerr=err, color = 'k', fmt = '.')
            
            

        plt.draw()




def Step(ax,tBins,y,col,lw,ls='-'):

    x=[]
    newY=[]
    for t,v in zip(tBins,y):
        
        x.append(t[0])
        newY.append(v)
        x.append(t[1])
        newY.append(v)
    ax.plot(x,newY,color=col,linewidth=lw,linestyle=ls)

        
