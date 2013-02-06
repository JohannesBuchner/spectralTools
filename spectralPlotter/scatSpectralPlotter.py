import spectralPlotter
from scatReader import scatReader
from numpy import array, dtype

class scatSpectralPlotter(spectralPlotter.spectralPlotter):

    def FitReader(self):
      
        fits = []
        #fName MUST be a list of files
        scats = map(lambda x: scatReader(x),self.fName)
        
        if len(scats[0].tBins) > 1: #Test if the scat is a batch fit
            print "\n\n Detected multiple FITS in "+ self.fName[0]+'\n\n'
            #Convert the list over to an entry
            scats = scats[0]
            self.scats = scats
            modelNames = scats.modelNames
            self.numFiles = len(scats.tBins)
            for i in range(len(scats.tBins)):
                params = []
                for x in modelNames:

                    #Needed to get array indexing correct
                    tmpDtype = scats.models[x]['values'][i].dtype
                    tmp = scats.models[x]['values'][i].tolist()
                    tmp = array(tmp)
                    tmp.dtype = tmpDtype

                    
                    params.append(tmp)
                    
                fit = spectralPlotter.Fit(modelNames,params)
                fits.append(fit)
            return fits





        for s in scats:
            
          
            modelNames = s.modelNames
            params = []
            for x in modelNames:
                params.append(s.models[x]['values'])
               
            fit = spectralPlotter.Fit(modelNames,params)
            fits.append(fit)

        

        return fits



 
