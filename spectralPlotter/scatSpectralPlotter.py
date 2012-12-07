import spectralPlotter
from scatReader import scatReader

class scatSpectralPlotter(spectralPlotter.spectralPlotter):

    def FitReader(self):
      
        fits = []
        #fName MUST be a list of files
        scats = map(lambda x: scatReader(x),self.fName)
        for s in scats:

            modelNames = s.modelNames
            params = []
            for x in modelNames:
                params.append(s.models[x]['values'])
            

            fit = spectralPlotter.Fit(modelNames,params)
            fits.append(fit)

        

        return fits



