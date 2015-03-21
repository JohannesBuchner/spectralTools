#from models import *
import sys
import os

from spectralTools.vFvPlotModelLookup import modelLookup
from numpy import array, sqrt, zeros, vstack, logspace, log10
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



#numerical derivative 
def deriv(f):

    def df(x, h=0.1e-7):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df

keV2erg =1.60217646e-9

class vFvContour:
    '''
    vFvPlot creates vFv plots with the 1-sigma contours
    The inputs 


    '''


    def __init__(self, scat, eMin=10., eMax=40000., numEneBins = 50):

        self.eMin = eMin
        self.eMax = eMax
        self.numEneBins = numEneBins

        self.scat = scat
        self.covars = scat.covars

        self.tBins= scat.tBins

        self.modelNames = scat.modelNames
        
        
        self.modelDict = modelLookup

        self._CreateVFV()
        self._CreateContours()


    def _CalcVFV(self, modelName, params, ene):
        '''
        Calculate the vFv of the given model and the given energy
        '''

        model = self.modelDict[modelName]
        vFv = (keV2erg**2) * (ene**2) *model(ene,*params[0])

        return vFv

    def _CalcContour(self, params, covar, currentModel, ene):
        '''
        Calculate the upper and lower contours at a given energy
        '''

       
        #Initialize the first derivative list
        firstDerivates = []

        
        for modName,par, z  in zip(self.scat.modelNames, params, self.scat.paramNames):

            # Grab the model definition 
            model = self.modelDict[modName] 

            # For each parameter create a temporary function that freezes the parameter
            # at it's measured value. This mimics a partial derivative evalutated at the measured
            # value.
            for parName in z:

                # The temporary function
                def tmpVFV(currentPar):

                    # Get the parameter values
                    tmpParams = par.copy()
                    
                    # Set the current parameter (the one that the derivative is being taken w.r.t.)
                    # To it's measured value
                    tmpParams[parName]=currentPar
                    
                    # Calculate vFv at this value
                    val = self._CalcVFV(modName,tmpParams, ene)

                    return val

                # Check if this is the currently evaluating model component and take it's derivative
                if modName == currentModel:
                    firstDerivates.append( deriv(tmpVFV)(par[parName]))
                # If it is the combined model then also calculate the derivative    
                elif currentModel == "total":
                    firstDerivates.append( deriv(tmpVFV)(par[parName]))
                # If the model is not the current model then all the derivatives will be zero
                else:
                    
                    firstDerivates.append(0.0)

                # We now calculat sigma^2  = fd.C.fd
                    
        # Convert to a numpy array for matrix math
        firstDerivates = array(firstDerivates)
                
        # Do the first half of the matrix equation
        tmp = firstDerivates.dot(covar)
        # Finish it up
        contours = sqrt( tmp.dot(firstDerivates) )
        
        return contours


    def _CreateContours(self):

        # Create log energy bins
        energy = logspace(log10(self.eMin), log10(self.eMax), self.numEneBins)

        tmpParamArray = map(lambda x: [] ,self.tBins)
        individualContours = []

        for mod in self.modelNames:



            for x,row in zip(self.scat.models[mod]['values'],tmpParamArray):
                row.append(x)
        
        for mod in self.modelNames:
            contour = []
            for ene in energy:
                contour.append(map(lambda par,cov: self._CalcContour(par,cov,mod,ene), tmpParamArray, self.covars))
            contour = array(contour).transpose()
            #for c in contour:
            individualContours.append(contour)


        contour = []
        for ene in energy:
            contour.append(map(lambda par,cov: self._CalcContour(par,cov,'total',ene), tmpParamArray, self.covars))
            
        contour = array(contour).transpose()
        #for c in contour:
        individualContours.append(contour)
        #individualContours.append(contour)
        
        self.contours=dict(zip(self.modelNames+['total'],individualContours))


    def _CreateVFV(self):

        val = []
        energy = logspace(log10(self.eMin), log10(self.eMax), self.numEneBins)

        for x in self.modelNames:

            tmp = []

            for pars in self.scat.models[x]['values']:

                vFv = []
                for ene in energy:
                    vFv.append(self._CalcVFV(x,pars,ene))
                    
                tmp.append(vFv)


            val.append(tmp)


        val = map(array,val)

        totVFV = zeros((len(val[0]),self.numEneBins))

        for x in val:
                        
            for y in x:
                
                y=array(y)
                totVFV = totVFV+y

        val.append(totVFV)

        tmp = list(self.modelNames)
        tmp.append('total')

        self.vFv = dict(zip(tmp,val))


    def PlotComponent(self, component='total', figNum=10, specLineStyle='-', specColor='b', specLineWidth=1, conLineStyle='-', conColor='b', conLineWidth=.5, filled=False,fillAlpha=.5):
        '''
        This is the main command. The options are for controlling the plotting style.
        
        The component argument is a string that is the name of the component you would like to plot
        
        '''
        
        energy = logspace(log10(self.eMin), log10(self.eMax), self.numEneBins)
        spec = self.vFv[component]
        contour = self.contours[component]

        upper = []
        lower = []

        xlabel = r"Energy (keV)"
        ylabel = r"$\nu F_{\nu}$ (erg$^2$ s$^{-1}$ cm$^{-2}$ keV$^-1$)"

        for s,c in zip(spec, contour):
            upper.append(s+c)
            lower.append(s-c)
        

        fig = plt.figure(figNum)
        ax = fig.add_subplot(111)
        for s,up,lo, in zip(spec,upper,lower):

            ax.loglog(energy,s, ls=specLineStyle, color=specColor, lw=specLineWidth)
            
            if filled:
                ax.fill_between(energy,lo,up,alpha=fillAlpha,interpolate=True, color=conColor, lw=conLineWidth, linestyle=conLineStyle )
                ax.set_yscale('log', nonposy='clip')
            else:
                ax.loglog(energy,up, ls=conLineStyle, color=conColor, lw=conLineWidth)

                ax.loglog(energy,lo, ls=conLineStyle, color=conColor, lw=conLineWidth)


        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        return ax




