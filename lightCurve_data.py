import astropy.io.fits as pf
import matplotlib.pyplot as plt
from numpy import arange, logical_and, array, zeros, genfromtxt, savez, mean
from shlex import shlex
import sys
import operator
from mpl_toolkits.axes_grid1 import AxesGrid, ImageGrid, Grid

from spectralTools.lightCurve import lightCurve




class lightCurve_data(lightCurve):

    def __init__(self, dataFile,dt,tstart,tstop,emin,emax):
        """
        A class

        """
        
        self.dataSets = []
        self.inFiles = [dataFile]
        self.customFlag = False
        
        self.drawGrid = False
        self.drawStack = False
        self.drawStackSub = False
        self.drawGridSub = False
        self.drawBkgGrid=False
        self.save =False
        self.bkgFlag =False
        self.lleFlag=False

        self.tMin = tstart
        self.tMax = tstop
        self.dt = dt


        self.eBins = [[emin,emax]]


        self.ImportData()
        self.run()        

    def GetCounts(self):


        return self.lc[0]


    def GetTime(self):


        t = array(map(mean,self.tBins))

        return t

    def GetTbins(self):


        return self.tBins



    def SaveLightCurve(self,filename):


        tmp = array(self.tBins)


        tmp2 = zip(self.GetTime(),tmp[:,0],tmp[:,1],self.GetCounts())

        tmp2 = array(tmp2)

        savez(filename,lc=tmp2)
        


                
        
        

        
