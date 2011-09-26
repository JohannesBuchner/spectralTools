from models import *
from scatReader import scatReader
from scipy.integrate import quadrature
from numpy import array, sqrt, zeros



def deriv(f):

    def df(x, h=0.1e-7):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df





class fluxLightCurve:


    def __init__(self,scat,eMin,eMax):

        
        self.eMin = eMin
        self.eMax = eMax
        

        self.scat = scat

#        data = scat.models


        self.tBins = scat.tBins
     #   self.values = data[self.modelName]['values']
     #   self.errors = data[self.modelName]['errors']
        self.modelNames = scat.modelNames


 
        self.modelDict = {'Band\'s GRB, Epeak': Band, 'Black Body': BlackBody}

        #self.model = modelDict[modelName]



    def ImportDataFromSCAT(self,scat):
        ''' 
        This method is used to read in an 
        from the scatreader object. It will then seperate 
        out the required info. 
        
        '''

 
        


    def CalculateFlux(self,modelName,params):

        model = self.modelDict[modelName]


        val,err, = quadrature(model, self.eMin,self.eMax,args=params[0],maxiter=100)

        return val


   
    def FluxError(self, params, covar):
        '''
        Params is a list of the params from each models
        [mod1,mod2,...]

        '''

        firstDerivates = []
        
        for modName,par, z  in zip(self.scat.modelNames,params, self.scat.paramNames):

            model = self.modelDict[modName]

            for parName in z:

#                print parName
#                print modName

                def tmpFlux(currentPar):

                    tmpParams = par.copy()
 #                   print "\nCurrent param:"
 #                   print currentPar

  #                  print "\nTmp Params:"
   #                 print tmpParams
                    tmpParams[parName]=currentPar


    #                print "\n New Tmp Params:"
     #               print tmpParams

                    return self.CalculateFlux(modName,tmpParams)



                firstDerivates.append( deriv(tmpFlux)(par[parName]))

    
        firstDerivates = array(firstDerivates)

        tmp = firstDerivates.dot(covar)

        self.errors =  tmp.dot(firstDerivates)

  


    def FormatCovarMat(self):


        length = self.scat.numParams
        
        self.covars = []
      
        for x in self.scat.covars:
            
            covar = []
    

            for i in range(length):
                

                tmp = []

                for j in range(length):

       

                    tmp.append(x[i*length+j])

                covar.append(tmp)
                    
            self.covars.append(array(covar))

            


    def CreateLightCurve(self):


        fluxes = []

        for x in self.modelNames:

            tmp = []

            for pars in self.scat.models[x]['values']:

                flux = self.CalculateFlux(x,pars)
                tmp.append(flux)


            fluxes.append(tmp)

       
        fluxes = map(array,fluxes)

        totFlux = zeros(len(fluxes[0]))

        for x in fluxes:
            totFlux+=x

        fluxes.append(totFlux)

        tmp = list(self.modelNames)
        tmp.append('total')

        self.fluxes = dict(zip(tmp,fluxes))


        






    def LightCurveErrors(self):

        tmpParamArray = map(lambda x: [] ,self.tBins)
        

        for mod in self.modelNames:
            
            
            for x,row in zip(self.scat.models[mod]['values'],tmpParamArray):

                row.append(x)



#        print tmpParamArray

        self.fluxErrors= map(lambda par,cov:self.FluxError(par,cov), tmpParamArray,self.covars  )

            
            










