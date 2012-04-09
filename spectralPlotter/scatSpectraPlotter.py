import spectraPlotter
from scatReader import scatReader

class scatSpectraPlotter(spectraPlotter.spectraPlotter):

    def FitReader(self):
      
        fits = []
        #fName MUST be a list of files
        scats = map(lambda x: scatReader(x),self.fName)
        for s in scats:

            modelNames = s.modelNames
            params = []
            for x in modelsNames:
                params.append(s.models[x]['values'])
            

            fit = spectraPlotter.Fit(modelNames,params)
            fits.append(fit)

        return fits



