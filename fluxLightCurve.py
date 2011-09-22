from models import *
from scatReader import scatReader
from scipy.integrate import quadrature
from numpy import array



def deriv(f):

    def df(x, h=0.1e-5):
        return ( f(x+h/2) - f(x-h/2) )/h

    return df





class fluxLightCurve:


    def __init__(self):

        
        self.eMin = 10
        self.eMax = 1000
        

        self.modelNames = ''


        self.fit = ''

        self.modelDict = {'Band\'s GRB, Epeak': Band, 'Black Body': BlackBody}

        #self.model = modelDict[modelName]



    def ImportDataFromSCAT(self,scat):
        ''' 
        This method is used to read in an 
        from the scatreader object. It will then seperate 
        out the required info. 
        
        '''

        self.scat = scat

        data = scat.models


        self.tBins = scat.tBins
     #   self.values = data[self.modelName]['values']
     #   self.errors = data[self.modelName]['errors']
        self.modelNames = scat.modelNames
        


    def CalculateFlux(self,modelName,params):

        model = self.modelDict[modelName]


        val,err, = quadrature(model, self.eMin,self.eMax,args=params[0],maxiter=100)

        return val





    def GeneralizeModel(self,f,params):
        
        def func(x):
            
            val = f(x, *params)
            return val

        return func
            




    


    

   
    def FluxError(self, params, covar):
        '''
        Params is a list of the params from each models
        [mod1,mod2,...]

        '''

        firstDerivates = []
        
        for modName,par, z  in zip(self.scat.modelNames,params, self.scat.paramNames):

            model = self.modelDict[modName]

            for parName in z:

           #     print parName
           #     print modName

                def tmpFlux(currentPar):

                    tmpParams = par.copy()

                    tmpParams[parName]=currentPar

                  

                    return self.CalculateFlux(modName,tmpParams)


                firstDerivates.append( deriv(tmpFlux)(par[parName]))


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

            


                    


                
            
            
            
            

   


        

 
