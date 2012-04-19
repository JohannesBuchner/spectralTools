import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from MakeLightCurve import MakeLightCurve
from lightCurve import lightCurve 
from numpy import array, asarray, cos, logical_and, deg2rad, sum, ones, unique, arange
from bbLook import bbLook 
import pyfits as pf
from glob import glob
from shlex import shlex
import sys, os, errno
from copy import copy
class binnedTTEBlockMaker:

    def __init__(self):
        
        #Class variables set during execution
        self.detList = [] # The will contain the lightCurve objects (counts, timeBins)
        self.rspList = [] # Contains a 2D list of detector angle and times where they apply
        self.nameList = [] # List of file names that is created WHEN the files are found
        self.correctedCounts = [] # Contains the counts corrected for detector angle

        self.fileTimes = []
        self.lightcurves = []
        self.tMax = 0
        self.tMin = 0
        

        #Class variables set by par files
        self.fileTimeBounds = False # If TRUE then the tstart and tstop from the TTE files are used as time bounds 
        self.correctCounts = False #In _CorrectDetectorsCounts this will cause a jump and make the uncorrected counts the default
        self.findBrightest = False # makes the fileList only the brightest but saves the original for writing *.ti files
        self.directory = '' # The directory to find the tte files
        self.make_ti = False
        self.preview = False
        self.multi = False
        self.merge = False
        self.summed = False
        

    def _Process(self):


        self.savedFileList = copy(self.fileList) # Save the file list for writing the *.ti files

        if self.findBrightest:
            
            print "Blocks will be built with only the counts from "+self.brightest
            self.correctCounts = False # There is no reason to correct counts for one detector
            self.fileList = [self.brightest]

        
        for x in self.savedFileList:
            self._ExtractTimeBounds(x,self.fileTimeBounds) #If set true TMIN and TMAX will be saved 
        print "The time bounds from the TTE file that will be used are "+str(self.tMin)+ " : "+str(self.tMax)

        self._ApplyDetectorEnergyBounds()

        for x,y in zip(self.fileList,self.eBounds):
            
            self.AddDetector(x,y)
        if self.nameList == []:
            print "No detectors added!"
            return
      
        
        self._CorrectDetectorsCounts()
        

        if self.summed:
            print "Summing detectors"
            self._SumDetectors()
            self.contents=self.correctedCounts[-1][0]
            #self.fileList = self.fileTimes[-1]
        else:
            self.contents=self.correctedCounts[0][0]
        self.binSizes = self.dt*ones(len(self.contents))




         #Create legend string
        legStrings = []
        if self.summed:
            for f,eb in zip(self.fileList[:-1],self.eBounds[:-1]):
                for x in eb:
                    legStrings.append( f[8:10] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")
            for x in self.eBounds[-1]:
                legStrings.append(self.fileList[-1] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")

        else:
            for f,eb in zip(self.fileList,self.eBounds):
                for x in eb:
                    legStrings.append( f[8:10] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")

                
        self.legStrings=legStrings   


       
        self._MakeBBs()
        self.lightcurves.append(self.bb)
        if self.preview:
            self._Preview()

        
 
        if self.make_ti:
            self._Make_ti_File()
        

    def _ProcessMulti(self):


        self.savedFileList = copy(self.fileList) # Save the file list for writing the *.ti files

                
        for x in self.fileList:
            self._ExtractTimeBounds(x,self.fileTimeBounds) #If set true TMIN and TMAX will be saved 
        print "The time bounds from the TTE file that will be used are "+str(self.tMin)+ " : "+str(self.tMax)

        self._ApplyDetectorEnergyBounds()

        for x,y in zip(self.fileList,self.eBounds):
            
            self.AddDetector(x,y)
        if self.nameList == []:
            print "No detectors added!"
            return
      
        
        self._CorrectDetectorsCounts()
        

        if self.summed:
            print "Summing detectors"
            self._SumDetectors()
       
        contents=self.correctedCounts
        
       
       
        for x in contents:
            for y in x:
                self.contents = y
                self.binSizes = self.dt*ones(len(self.contents))
                self._MakeBBs()
                self.lightcurves.append(self.bb)


        #Create legend string
        legStrings = []
        if self.summed:
            for f,eb in zip(self.fileList[:-1],self.eBounds[:-1]):
                for x in eb:
                    legStrings.append( f[8:10] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")
            for x in self.eBounds[-1]:
                legStrings.append(self.fileList[-1] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")

        else:
            for f,eb in zip(self.fileList,self.eBounds):
                for x in eb:
                    legStrings.append( f[8:10] + ": "+ str(x[0])+"-"+str(x[1])+"_keV")

                
        self.legStrings=legStrings   
                
        if self.preview:
            self._Preview()

        if self.merge:
            self._Merge()

        if self.make_ti:
            self._Make_ti_File()

       


    def ReadParFile(self,parFile):

        parFile = open(parFile)
        self.fileList=[]
        self.detsForSumming = [] # Don't include BGOs!!!!
        tmpEBin = []
        tmpBgoRange = []
        tmpNaiRange = []

        lex = shlex(parFile,posix=True)
        lex.whitespace += '='
        lex.whitespace_split = True
        flag = True
        while flag:
            t=lex.get_token()
        
            if t=='EBIN':
                t=lex.get_token()
                tmpEBin.append(t)
            if t=='TMIN':
                t=lex.get_token()
                self.tMin = float(t)
            if t=='TMAX':
                t=lex.get_token()
                self.tMax = float(t)
            if t=='DT':
                t=lex.get_token()
                self.dt = float(t)
            if t=='NCP_PRIOR':
                t=lex.get_token()
                self.ncp_prior = float(t)
            if t=='TTE':
                t=lex.get_token()
                self.fileList.append(t)
            if t=='SUMMED_TTE':
                t=lex.get_token()
                self.detsForSumming.append(t)
            if t=="SUM":
                self.summed=True
            if t=='DIR':
                t=lex.get_token()
                self.directory=t
            if t=='FILEBOUNDS':
                self.fileTimeBounds=True
            if t=='CORRECT_COUNTS':
                self.correctCounts=True
            if t=='BRIGHTEST':
                self.findBrightest=True
                t=lex.get_token()
                self.brightest = t
            if t=="NAI_E_RANGE":
                t=lex.get_token()
                tmpNaiRange.append(t)
            if t=="BGO_E_RANGE":
                t=lex.get_token()
                tmpBgoRange.append(t)
            if t=="PREVIEW":
                self.preview = True
            if t=="MAKE_TI":
                self.make_ti = True
            if t=="MULTI":
                self.multi = True
            if t=="MERGE":
                self.merge = True
            
                
            if t ==lex.eof:
                flag=False

            
        del parFile 
        del lex

        tmp = map(lambda x: x.split(':'), tmpEBin)
  
        tmp = map(lambda x: [float(x[0]),float(x[1])],tmp)
        tmp.sort()
        self.eBins = tmp
        
        #Assign NaI limits:
        tmp = map(lambda x: x.split(':'), tmpNaiRange)
  
        tmp = map(lambda x: [float(x[0]),float(x[1])],tmp)
        tmp.sort()
        self.naiBounds = tmp[0]

        #Assign BGO limits:
        tmp = map(lambda x: x.split(':'), tmpBgoRange)
  
        tmp = map(lambda x: [float(x[0]),float(x[1])],tmp)
        tmp.sort()
        self.bgoBounds = tmp[0]
        
        if self.multi:
            self._ProcessMulti()
        else:
            self._Process()



    def AddDetector(self,tteFile,eBound):
        

        #Make sure the detector has a response
        tteSlice = tteFile[-22:-6]
        
        test = glob(self.directory+"*glg_cspec_"+tteSlice+"*rsp*")
        
        if len(test) == 0:
            print "ERROR: "+tteFile+" has no RSP file."
            return
        elif len(test)>1:
            print "ERROR: Found more than one RSP file for "+tteFile+":\n"
            for x in test:
                print "\t"+x
            return
        else:
            rspFile = test[0]

        self._OpenDetector(tteFile,eBound)
        self._OpenRSPFile(rspFile)
        self.nameList.append(tteFile)

        return



    def _OpenDetector(self,tteFile,eBound):
        
        tteFile = self.directory+tteFile
        lc = lightCurve('') #Give lc a fake parFile
        lc.inFiles = [tteFile]
        lc.ImportData()
        lc.dt=self.dt
        lc.tMax=self.tMax
        lc.tMin=self.tMin
        lc.eBins = eBound
        lc.EnergyBinning()
        lc.TimeBinning()
        self.detList.append(lc)

    def _OpenRSPFile(self,rspFile):
  
        
        
        rspFile = pf.open(rspFile)
        numMats = len(rspFile) - 2
        rspMats = rspFile[2:2+numMats]
        detAngs = []
        deltaTs = []

        for x in rspMats:
            x=x.header
            detAngs.append(x['DET_ANG'])
            trigTime = x['TRIGTIME']
            start = x['TSTART']-trigTime
            stop = x['TSTOP']-trigTime
            deltaTs.append( [start,stop] )
        self.rspList.append([detAngs,deltaTs])
        
    def _CorrectDetectorsCounts(self):
        
        
        for det,rsp,name in zip(self.detList,self.rspList,self.nameList):
            print "\n"+name+": " 
            counts = array(det.lc)

            # If the user selected not to correct for detector angles
            if not self.correctCounts:
                
                self.correctedCounts.append(counts)
                
            else:
                print "Correcting Rates for Detector Orientation"
                if (name.find("_b0_")==-1) and (name.find("_b1_")==-1):
                
           
                    # The counts
                    tbins = asarray(det.tBins)[:,0] # The lo edge
                    detAngs, deltaTs = rsp
           
                    #Calculate the correctionFactor
                    correctionFactors = 1./cos(deg2rad(detAngs))
                    print "\tcorrecting:"
                    for cf,dt in zip(correctionFactors, deltaTs):
                
                        lo, hi = dt
                        print "\n\t\tfrom "+str(lo)+" to "+str(hi)+" by "+str(cf)
                        loMask = tbins >= lo
                        hiMask = tbins < hi
                        mask = logical_and(loMask,hiMask)
                        for i in range(len(counts)):
                            counts[i][mask] = counts[i][mask]*cf
                else:  
                    print "\n\tThis is a BGO. No correction applied\n"
                self.correctedCounts.append(counts)
            

        
    def _ExtractTimeBounds(self,tteFile,save = False):
        
        tteFile = self.directory+tteFile
        tteFile = pf.open(tteFile)
        header = tteFile[0].header
        trigTime = header['TRIGTIME']
        start = header['TSTART'] - trigTime
        end = header['TSTOP'] - trigTime
        self.fileTimes.append([start,end])
        # We want to check that the start and end times
        # are at the extreme for all files
        
        if save:
            if start < self.tMin:
                self.tMin = start
            if end > self.tMax:
                self.tMax = end
        
    def _ApplyDetectorEnergyBounds(self):
        
        customEnergyBounds = []
        for x in self.fileList:
            if (x.find("_b0_")==-1) and (x.find("_b1_")==-1): #Nai detector
                print "Applying NAI energy bounds to : " +x
                tmpType = self.naiBounds
            else: #bgo detector
                print "Applying BGO energy bounds to : " +x
                tmpType = self.bgoBounds
            tmp = []    
            for eBin in self.eBins:
                exlude=False
                
                if eBin[0]>tmpType[1]: #The ebin is outSide the range of the det Range
                    exlude=True
                elif eBin[0]<tmpType[0]:
                    eMin = tmpType[0]
                else:
                    eMin = eBin[0]
                
                
                #######
                
                if eBin[1]<tmpType[0]: #The ebin is outSide the range of the det Range
                    exlude = True
                elif eBin[1]>tmpType[1]:
                    exlude2=True
                    eMax = tmpType[1]
                else:
                    eMax = eBin[1]

                
                if not exlude:
                    
                    tmp.append([eMin,eMax])
            customEnergyBounds.append(tmp)
        self.eBounds = customEnergyBounds
        


    def _Merge(self):

        print "Merging change points...."
        times = []
        for x in self.lightcurves:
            times.extend(x[:,0])

        
        times = unique(asarray(times))
        self.mergeTimes = times.tolist()
        
        


    def _SumDetectors(self):
      
        tmp1 = [] #Index is for each detector
        removeList = []
       # self.test = copy(self.correctedCounts)
        for name, det in zip(self.fileList, self.correctedCounts):
            if name in self.detsForSumming:
                print name+" in summing list"
                tmp2 = [] #index is for each energy bin 
                #for ebin in det:
                #    tmp2.append(ebin)
                tmp1.append(det)
                removeList.append(1)
            else: 
                removeList.append(0)
        tmp1 = array(tmp1)
        #self.tmp1 = tmp1        
        


        # Go through and remove the detectors that were summed together 
        # from the corrected counts
        
        for det,name,eb,trial in zip( self.correctedCounts, self.fileList, self.eBounds, removeList):
            if trial == 1:
                self.correctedCounts.remove(det)
                self.fileList.remove(name)
                newBound = eb 
                self.eBounds.remove(eb)
    
        tmp3 = []
        for i in range(len(newBound)):
            tmp3.append( sum(tmp1[:,i], axis=0)  ) #Summed over detectors


        #print len(self.correctedCounts)
        self.correctedCounts.append(tmp3)
        self.eBounds.append(newBound)

        #Construct strings for legends
        summedString = ""
        for x in self.detsForSumming:
            summedString = summedString +x[8:10]+"+"
        summedString=summedString[:-1]
        self.fileList.append(summedString)


        
            
        
                    

        #self.correctedCounts = array(map(lambda cc: cc[0] ,self.correctedCounts))
        #self.contents = sum(self.correctedCounts,axis=0)
        #self.binSizes = self.dt*ones(len(self.contents))


    def _MakeBBs(self):
        
        bb = MakeLightCurve(self.binSizes,self.contents,self.tMin,self.ncp_prior)
        self.bb=bb


    def _Preview(self):
        
        plt = bbLook()
        
        plt.AddLegendStrings(self.legStrings)
        for x in self.lightcurves:
            plt.AddLightCurve(x)
        plt.PlotLightCurves()


    def _Make_ti_File(self):
        

        if self.multi and (not self.merge):
            print "Creating folders for .ti files in each energy bin"
            
             #Create legend string
            folderStrings = []

            if self.summed:
                for f,eb in zip(self.fileList[:-1],self.eBounds[:-1]):
                    for x in eb:
                        folderStrings.append( f[8:10] + "_"+ str(x[0])+"-"+str(x[1])+"_keV")
                    for x in self.eBounds[-1]:
                        folderStrings.append(self.fileList[-1] + "_"+ str(x[0])+"-"+str(x[1])+"_keV")

            else:
                for f,eb in zip(self.fileList,self.eBounds):
                    for x in eb:
                        folderStrings.append( f[8:10] + "_"+ str(x[0])+"-"+str(x[1])+"_keV")

            for x in folderStrings:
                mkdir_p(self.directory+"ti/"+x)

            for lc,name in zip(self.lightcurves,folderStrings):
                tmpBins = lc[:,0].tolist()
                start = tmpBins.pop(0)
                end =  tmpBins.pop(-1)
                
                

                tis = []
                for j in self.fileTimes:
                    ti = []
                    for i in range(0,len(tmpBins),2):
                        ti.append(tmpBins[i])
                    ti.append(end)
                    ti.insert(0,start)
                    tmp = arange(j[0],start,.1)
                    tmp = tmp.tolist()
                    tmp.extend(ti)
                    ti = tmp
                    tmp = arange(j[1],end,-.1)
                    tmp = tmp[::-1]
                    ti.extend(tmp)

                    length = len(ti)
                    ti.insert(0,length)
                    tis.append(ti)
                #Write files
                tiNames = []
                self.fileList = self.savedFileList
                for x in self.fileList:
        
                    tiName = x[:-3]+"ti"
                    tiNames.append(self.directory+"ti/"+name+"/"+tiName)
        
      
                #del x
                for x,y in zip(tiNames,tis):
                    tmp = y
                    print "\n Writing "+x
                    f=open(x,"w")
                    for z in tmp:
                        f.write(str(z)+"\n")
                f.close()
                del f
                del tmp
            return

        elif self.merge and self.multi:
            tmpBins = self.mergeTimes
            step = 1

        else:
            step=2
            tmpBins = self.bb[:,0].tolist()

###############################################
        mkdir_p(self.directory+"ti")
        start = tmpBins.pop(0)
        end =  tmpBins.pop(-1)
        


        tis=[]
        for j in self.fileTimes:
            ti = []
            for i in range(0,len(tmpBins),step):
                ti.append(tmpBins[i])
            ti.append(end)
            ti.insert(0,start)
            tmp = arange(j[0],start,.1)
            tmp = tmp.tolist()
            tmp.extend(ti)
            ti = tmp
            tmp = arange(j[1],end,-.1)
            tmp = tmp[::-1]
            ti.extend(tmp)

            length = len(ti)
            ti.insert(0,length)
            tis.append(ti)
        
        #Write files
        tiNames = []
        self.fileList = self.savedFileList
        
        
        for x in self.fileList:
        
            tiName = x[:-3]+"ti"
            tiNames.append(self.directory+"ti/"+tiName)
        
      
        del x
        for x,y in zip(tiNames,tis):
            
            tmp = y
            print "\n Writing "+x
            f=open(x,"w")
            for z in tmp:
                f.write(str(z)+"\n")
            f.close()
            del f
            del tmp 


############ END CLASS
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise


if __name__ == '__main__':

    bb = binnedTTEBlockMaker()
    bb.ReadParFile(sys.argv[1])
    



