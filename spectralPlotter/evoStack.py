#from scatSpectralPlotter import scatSpectralPlotter
from spectralTools.scatReader import scatReader
import matplotlib.pyplot as plt
from spectralTools.temporal.fluxLightCurve import fluxLightCurve
from numpy import  sqrt

#fig_width_pt =245.26653  # Get this from LaTeX using \showthe\columnwidth
#inches_per_pt = 1.0/72.27               # Convert pt to inch
#golden_mean = (sqrt(5)-1.0)/2.0         # Aesthetic ratio
#fig_width = fig_width_pt*inches_per_pt  # width in inches
#fig_height = fig_width*golden_mean      # height in inches
#fig_size =  [fig_width,fig_height]
#params = {'backend': 'ps',
#          'axes.labelsize': 6,
#          'text.fontsize': 6,
#          'legend.fontsize': 10,
#          'xtick.labelsize': 5,
#          'ytick.labelsize': 5,
#          'text.usetex': True,
#          'figure.figsize': fig_size,
#          'font.family': 'serif'}

params = {'backend': 'ps',
          
          'text.usetex': True,
          
          'font.family': 'serif'}

plt.rcParams.update(params)
keV2erg =1.60217646e-9



class evoStack:


    def __init__(self, lightcurve=True, params=[], pht=True, components=['total'], eMin=10, eMax=600, colorTable=['k'] ):
        '''
        Setup the plot for all the propoerties you want to show. 
        
        lightcurve (True/False)
        
        param = [['model','param1'], ['model','param2']]
        
        pht = True makes photon lightcurves, False is energyflux
        
        To change the colors of the individual plots then the colorTable input
        must be altered. By default all colors are black. To change this simply
        modify the colorTable variable e.g.

        colorTable = ['k','b','g']

        will result in the lightcurve beind black, param1 being blue, and
        param2 being green. 

        If a lightcurve is in the plots then it's color will always be * 1st *
        in the colorTable. Othersise the color ordering will be matched with
        order of the input params.


        '''

        self.eMin = eMin
        self.eMax = eMax


        self.lightcurve = lightcurve
        self.params = params 
        
        self.pht = pht
        self.components = components


        self.files = []

        stackSize = 0

        #Count up the number of plots required
        if lightcurve:
            stackSize+=1
        for x in params:
            stackSize+=1


        ## Make sure that there are enough entries in the color table
        if len(colorTable)<stackSize:
            print "Correcting colorTable size"
            for i in range(stackSize-len(colorTable)):
                colorTable.append('k')

        

        self.colorTable = colorTable
            
        #Set up the figure specs
        self.fig = plt.figure(100)
        self.fig.subplots_adjust(hspace=0.001) # Align the plots
        self.axes = [] #Table of the axes

        #Add and axes for each plot. Lightcurve is in the first row.
        #The axis will share a common x-axis
        for a in range(stackSize):
            if a==0:
                self.axes.append(self.fig.add_subplot(stackSize,1,a+1))
            else:
                self.axes.append(self.fig.add_subplot(stackSize,1,a+1, sharex=self.axes[0]) )
        
        
        self.stackSize = stackSize


        
        
        
        

        

    def AddInputSCATFiles(self,files):
        '''
        Append a file onto the file name stack 

        '''
        self.files.append(files)
        
        
        


   


    def _MakeLightCurve(self):
        '''
        Private method called by Process if lightcurve = True
        makes photon or energy flux lightcurves from the scat files 
        over the specfied energy range

        '''
        
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


        
        
        for f, e in zip(flux, errors):

            
            self.axes[0].errorbar(mTBins, f, yerr=e,color=self.colorTable[0], fmt='.')
            
            Step(self.axes[0], tBins, f, self.colorTable[0], 1.)


        



        
        ax = self.axes[0]
        #ax.set_xlabel("time (s)")
        if self.pht:
            ax.set_ylabel("photons s$^{-1}$ cm$^{-2}$")
        else:
            ax.set_ylabel("ergs s$^{-1}$ cm$^{-2}$")

        ax.set_xlim(left = tBins[0][0], right=tBins[-1][-1])
            
        #plt.draw()


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
          
            #tBins = scats[0].tBins
            mTBins = scats[0].meanTbins

        self.scats = scats

        if self.lightcurve:
            colors = self.colorTable[1:]
        else:
            colors = self.colorTable

        for p, i, cl  in zip(self.params, range(len(self.params)), colors):


            model, par, = p
            #print model
            #print par
            #print  scats[0].GetParamArray(model,par)
            val =  scats[0].GetParamArray(model,par)[:,0]
            err = scats[0].GetParamArray(model,par)[:,1]
            
            ax = self.axes[i+1] 
            ax.errorbar(mTBins, val, yerr=err, color = cl, fmt = '.')
            ax.set_ylabel(par)
            ax.set_yscale('log')
            
            
            

        


    def Process(self):
        
        if self.files == []:

            print "YOU HAVE NOT ADDED ANY FILES!!!!"
            print "use .AddInputSCATFiles(<filename>)"
            return
        if self.lightcurve:
            self._MakeLightCurve()
        if self.params != []:
            self._PlotParameters()


        lastAx = self.axes[-1]

        lastAx.set_xlabel("time (s)")
        
        plt.draw()

def Parser(parfile):
        '''
        Reads a parfile to automatically generate plots
        without having to initiate the python cmd line.

        '''


    f = open (self.parFile)
    lex = shlex(f,posix=True)
    lex.whitespace += '='
    lex.whitespace_split = True

    flag=True
    while flag:

        t=lex.get_token()
        print t
            
            
        if t=='PHOTON':
            t=lex.get_token()
            pht = True

        if t=='ENERGY':
            t=lex.get_token()
            pht = False


        if t=='EMIN':
            t=lex.get_token()
            eMin = t

        if t=='EMAX':
            t=lex.get_token()
            eMax = tmp

        if t=='COLORS':
            t=lex.get_token()
            
        
        
           

          

        if t ==lex.eof:
            flag=False

        del f 
        del lex

        


def Step(ax,tBins,y,col,lw,ls='-'):

    x=[]
    newY=[]
    for t,v in zip(tBins,y):
        
        x.append(t[0])
        newY.append(v)
        x.append(t[1])
        newY.append(v)
    ax.plot(x,newY,color=col,linewidth=lw,linestyle=ls)

        
