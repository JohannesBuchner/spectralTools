from scatSpectralPlotter import scatSpectralPlotter
from spectralTools.scatReader import scatReader
import matplotlib.pyplot as plt
from spectralTools.temporal.fluxLightCurve import fluxLightCurve



class evoStack:


    def __init__(self, lightcurve=True, param=None, spectrum=True, pht=True):
        '''
        Setup the plot for all the propoerties you want to show. 
        This includes color matching between spectrum (True/False)
        lightcurve (True/False)
        param = ['param1', 'param2']
        spectrum (True/False)
        pht = True makes photon lightcurves, False is energyflux
        '''


        self.lightcurve = lightcurve
        self.param = param 
        self.spectrum = spectrum
        self.pht = pht
        self.files = []

        stackSize = 0

        if lightcurve:
            stackSize+=1
        if param != None:
            stackSize+=1
        if spectrum:
            stackSize+=1

        self.fig = plt.figure(100)
        self.fig.add_subplot(1,stackSize,1)
        self.figGeometry = (1,stackSize,1)
        
        self.stackSize = stackSize


        
        
        
        

        

    def AddInputSCATFiles(self,files):

        self.files.append(files)
        
        
        


    def _MakeSpectrumPlot(self):
        
        scp =  scatSpectralPlotter(vFv = True)
        scp.SetFitsFile(self.files)
        scp.ReadFits()


        specAx = scp.vFvAx

        self.fig = plot_axes(specAx, fig=self.fig, geometry=self.figGeometry)


    def _MakeLightCurve(self):
        
        scats = map(scatReader, self.files)
        
        if len(scatReader) > 1:
            tmp = scats[0]
            for s in scats[1:]:
                tmp = tmp + s
            scats = tmp
            tBins = scat.tBins
            
            flc = fluxLightCurve(scats, self.eMin, self.eMax)
        else:
            flc = fluxLightCurve(scats[0], self.eMin, self.eMax)
            tBins = scat[0].tBins

        if self.pht:

            flc.CreateLightCurve()
            flc.LightCurveErrors()

        else:
            flc.CreateEnergyLightCurves()
            flc.EnergyLightCurveErrors()




            
            
       


def plot_axes(ax, fig=None, geometry=(1,1,1)):
    if fig is None:
        fig = plt.figure()
    if ax.get_geometry() != geometry :
        ax.change_geometry(*geometry)
    ax = fig.axes.append(ax)
    return fig



def Step(ax,tBins,y,col,lw,ls='-'):

    x=[]
    newY=[]
    for t,v in zip(tBins,y):
        x.append(t[0])
        newY.append(v)
        x.append(t[1])
        newY.append(v)
    ax.plot(x,newY,color=col,linewidth=lw,linestyle=ls)

        
